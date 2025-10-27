"""
ViewSets para el app reservas
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q, Max, F
from django.utils import timezone
from datetime import datetime

from .models import Reserva, ReservaDetalle, ReservaAdicionalDetalle, OrdenServicio, OrdenServicioDetalle, Gasto
from .serializers import (
    ReservaSerializer, ReservaDetalleSerializer, ReservaAdicionalDetalleSerializer,
    OrdenServicioSerializer, OrdenServicioDetalleSerializer, GastoSerializer
)


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Reservas con lógica de negocio especial
    """
    queryset = Reserva.objects.select_related(
        'cliente', 'creado_por', 'girado_por'
    ).prefetch_related(
        'reservadetalle_set__servicio',
        'reservadetalle_set__recoger_en',
        'reservaadicionaldetalle_set__adicional'
    ).all()
    serializer_class = ReservaSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cliente', 'estado',
                        'tipo_documento', 'tipo_pago', 'fecha']
    search_fields = ['pasajero', 'numero', 'numero_factura', 'observaciones']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def perform_create(self, serializer):
        """Al crear, aplicar lógica de estado Pagado"""
        reserva = serializer.save()
        self._aplicar_logica_estado(reserva)

    def perform_update(self, serializer):
        """Al actualizar, aplicar lógica de estado Pagado"""
        reserva = serializer.save()
        self._aplicar_logica_estado(reserva)

    def _aplicar_logica_estado(self, reserva):
        """
        Si estado='0' (Pagado):
        - Asignar número (max+1) si no tiene
        - Asignar girado_por y girado_cuando si no tiene
        """
        if reserva.estado == '0':  # Pagado
            if not reserva.numero:
                max_numero = Reserva.objects.filter(numero__isnull=False).aggregate(
                    max_num=Max('numero')
                )['max_num']
                try:
                    nuevo_numero = int(max_numero) + 1 if max_numero else 1
                except:
                    nuevo_numero = 1
                reserva.numero = str(nuevo_numero)

            if not reserva.girado_cuando:
                reserva.girado_cuando = timezone.now()

            reserva.save()

    @action(detail=False, methods=['get'])
    def totales(self, request):
        """Calcula totales de las reservas filtradas"""
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.aggregate(total=Sum('total'))['total'] or 0
        total_nocontable = queryset.aggregate(
            total=Sum('total_nocontable'))['total'] or 0

        return Response({
            'total': total,
            'total_nocontable': total_nocontable,
            'total_neto': total - total_nocontable,
            'cantidad': queryset.count()
        })


class ReservaDetalleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para ver detalles de reservas
    Usado principalmente para reportes
    """
    queryset = ReservaDetalle.objects.select_related(
        'pertenece_a__cliente',
        'servicio',
        'recoger_en'
    ).all()
    serializer_class = ReservaDetalleSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pertenece_a', 'servicio',
                        'cuando', 'idioma', 'seleccionado']
    search_fields = ['pertenece_a__pasajero']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def biblia_digital(self, request):
        """
        Reporte Biblia Digital
        Filtra por servicio, fecha e idioma
        """
        servicio_id = request.query_params.get('servicio')
        fecha = request.query_params.get('fecha')
        idioma = request.query_params.get('idioma')

        queryset = self.get_queryset()

        if servicio_id:
            queryset = queryset.filter(servicio_id=servicio_id)
        if fecha:
            queryset = queryset.filter(cuando=fecha)
        if idioma and idioma != 'todos':
            queryset = queryset.filter(idioma=idioma)

        # Agregar información de la reserva padre
        queryset = queryset.select_related('pertenece_a')

        serializer = self.get_serializer(queryset, many=True)

        # Calcular total de pasajeros
        total_pax = queryset.aggregate(total=Sum('numero_pax'))['total'] or 0

        return Response({
            'detalles': serializer.data,
            'total_pasajeros': total_pax
        })


class ReservaAdicionalDetalleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para detalles de adicionales"""
    queryset = ReservaAdicionalDetalle.objects.select_related(
        'pertenece_a__cliente',
        'adicional'
    ).all()
    serializer_class = ReservaAdicionalDetalleSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pertenece_a', 'adicional', 'cuando']
    search_fields = ['pertenece_a__pasajero']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def informe(self, request):
        """Informe de adicionales con totales"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        total = queryset.aggregate(total=Sum('total'))['total'] or 0

        return Response({
            'detalles': serializer.data,
            'total': total
        })


class OrdenServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Órdenes de Servicio
    Al eliminar, restaura seleccionado=False en ReservaDetalle
    """
    queryset = OrdenServicio.objects.select_related(
        'servicio', 'guia', 'chofer'
    ).prefetch_related(
        'ordenserviciodetalle_set__referencia__pertenece_a'
    ).all()
    serializer_class = OrdenServicioSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['servicio', 'fecha', 'idioma', 'guia', 'chofer']
    search_fields = ['servicio__nombre', 'guia__nombre', 'chofer__nombre']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def perform_destroy(self, instance):
        """Al eliminar, restaurar seleccionado=False en detalles"""
        for detalle in instance.ordenserviciodetalle_set.all():
            detalle.referencia.seleccionado = False
            detalle.referencia.save()
        instance.delete()

    @action(detail=True, methods=['delete'])
    def eliminar_detalle(self, request, pk=None):
        """Elimina un detalle de la orden y restaura seleccionado=False"""
        detalle_id = request.data.get('detalle_id')
        if not detalle_id:
            return Response(
                {'error': 'detalle_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            detalle = OrdenServicioDetalle.objects.get(
                id=detalle_id,
                pertenece_a_id=pk
            )
            detalle.referencia.seleccionado = False
            detalle.referencia.save()
            detalle.delete()

            return Response({'message': 'Detalle eliminado'})
        except OrdenServicioDetalle.DoesNotExist:
            return Response(
                {'error': 'Detalle no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class GastoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Gastos
    Los usuarios normales solo ven sus propios gastos
    """
    queryset = Gasto.objects.select_related('creado_por').all()
    serializer_class = GastoSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fecha', 'creado_por']
    search_fields = ['descripcion']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def get_queryset(self):
        """Filtrar por usuario si no es administrador"""
        queryset = super().get_queryset()
        user = self.request.user

        # Si no es administrador, solo ver sus propios gastos
        if not user.groups.filter(name='Administrador').exists():
            queryset = queryset.filter(creado_por=user)

        return queryset

    @action(detail=False, methods=['get'])
    def totales(self, request):
        """Calcula el total de gastos filtrados"""
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            'total': total,
            'cantidad': queryset.count()
        })
