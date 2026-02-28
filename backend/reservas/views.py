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
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from .models import Reserva, ReservaDetalle, ReservaAdicionalDetalle, OrdenServicio, OrdenServicioDetalle, Gasto
from base.models import Auditoria
from .serializers import (
    ReservaSerializer, ReservaDetalleSerializer, ReservaAdicionalDetalleSerializer,
    OrdenServicioSerializer, OrdenServicioDetalleSerializer, GastoSerializer
)
from base.utils.pdf_generator import PDFGenerator


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
    filterset_fields = {
        'cliente': ['exact'],
        'estado': ['exact'],
        'tipo_documento': ['exact'],
        'tipo_pago': ['exact'],
        'fecha': ['exact', 'gte', 'lte'],
        'girado_por': ['exact'],
        'girado_cuando': ['exact', 'gte', 'lte', 'date'],
    }
    search_fields = ['pasajero', 'numero', 'numero_factura', 'observaciones']
    ordering_fields = '__all__'
    ordering = ['-fecha']

    def destroy(self, request, *args, **kwargs):
        """
        Evitar la eliminación de reservas que tengan detalles asociados a órdenes de servicio
        """
        reserva = self.get_object()

        # Verificar si algún detalle de la reserva está en una orden de servicio
        detalles_en_ordenes = OrdenServicioDetalle.objects.filter(
            referencia__pertenece_a=reserva
        ).exists()

        if detalles_en_ordenes:
            return Response(
                {
                    'error': 'No se puede eliminar la reserva porque tiene servicios asociados a órdenes de servicio. '
                             'Elimine primero las órdenes de servicio relacionadas.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)

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
    def pdf_rendicion_ventas(self, request):
        """Genera PDF de la rendición de ventas"""
        usuario_id = request.query_params.get('girado_por')
        fecha_desde = request.query_params.get('girado_cuando__gte')
        fecha_hasta = request.query_params.get('girado_cuando__lte')
        agencia_id = request.query_params.get('cliente')
        tipo_pago = request.query_params.get('tipo_pago')

        if not usuario_id or not fecha_desde or not fecha_hasta:
            return Response({'error': 'Faltan parámetros requeridos'}, status=400)

        from django.contrib.auth.models import User
        from base.models import Cliente

        usuario = User.objects.get(id=usuario_id)
        agencia = Cliente.objects.get(id=agencia_id) if agencia_id else None

        # Filtrar reservas pagadas (estado='0')
        reservas_qs = self.get_queryset().filter(
            estado='0',
            girado_por_id=usuario_id,
            girado_cuando__gte=fecha_desde,
            girado_cuando__lte=fecha_hasta
        )
        if agencia_id:
            reservas_qs = reservas_qs.filter(cliente_id=agencia_id)
        if tipo_pago is not None:
            reservas_qs = reservas_qs.filter(tipo_pago=tipo_pago)

        # Crear lista con campos necesarios para el template
        reservas = []
        for r in reservas_qs:
            reservas.append({
                'id': r.id,
                'cliente_nombre': r.cliente.nombre if r.cliente else '',
                'fecha_primer_servicio': r.fecha_primer_servicio,
                'girado_cuando': r.girado_cuando,
                'pasajero': r.pasajero,
                'tipo_documento_display': r.get_tipo_documento_display(),
                'tipo_pago_display': r.get_tipo_pago_display() if r.tipo_pago else None,
                'total': r.total,
            })

        total_general = sum(float(r['total'] or 0) for r in reservas)

        tipo_pago_map = {'0': 'Efectivo', '1': 'Depósito', '2': 'Otro'}

        context = {
            'usuario_nombre': usuario.get_full_name() or usuario.username,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'agencia_nombre': agencia.nombre if agencia else None,
            'tipo_pago_display': tipo_pago_map.get(tipo_pago) if tipo_pago else None,
            'reservas': reservas,
            'total_general': total_general,
        }

        pdf_gen = PDFGenerator('pdf/rendicion_ventas.html',
                               context, orientation='landscape')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="rendicion_ventas_{usuario.username}_{fecha_desde}_{fecha_hasta}.pdf"'
        return response

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

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """
        Obtiene el historial completo de cambios de una reserva
        Incluye cambios en la reserva, sus detalles y adicionales
        Solo accesible por administradores
        """
        reserva = self.get_object()

        # Verificar que sea administrador
        if not request.user.groups.filter(name='Administrador').exists():
            return Response(
                {'error': 'Solo los administradores pueden ver el historial'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener ContentTypes
        ct_reserva = ContentType.objects.get_for_model(Reserva)
        ct_detalle = ContentType.objects.get_for_model(ReservaDetalle)
        ct_adicional = ContentType.objects.get_for_model(
            ReservaAdicionalDetalle)

        # Obtener IDs de detalles y adicionales de esta reserva
        detalles_ids = list(
            reserva.reservadetalle_set.values_list('id', flat=True))
        adicionales_ids = list(
            reserva.reservaadicionaldetalle_set.values_list('id', flat=True))

        # Obtener todas las auditorías relacionadas
        auditorias = Auditoria.objects.filter(
            # Cambios en la reserva
            Q(content_type=ct_reserva, object_id=reserva.id) |
            # Cambios en detalles
            Q(content_type=ct_detalle, object_id__in=detalles_ids) |
            # Cambios en adicionales
            Q(content_type=ct_adicional, object_id__in=adicionales_ids)
        ).select_related('usuario', 'content_type').order_by('-fecha')

        # Serializar resultados
        historial_data = []
        for auditoria in auditorias:
            historial_data.append({
                'id': auditoria.id,
                'fecha': auditoria.fecha,
                'usuario': auditoria.usuario.username,
                'usuario_nombre_completo': f"{auditoria.usuario.first_name} {auditoria.usuario.last_name}".strip() or auditoria.usuario.username,
                'accion': auditoria.accion,
                'accion_display': auditoria.get_accion_display(),
                'modelo': str(auditoria.content_type.model).title(),
                'modelo_id': auditoria.object_id,
                'datos_anteriores': auditoria.datos_anteriores,
                'datos_nuevos': auditoria.datos_nuevos,
                'ip_address': auditoria.ip_address,
            })

        return Response({
            'reserva_id': reserva.id,
            'reserva_numero': reserva.numero,
            'pasajero': reserva.pasajero,
            'historial': historial_data,
            'total_cambios': len(historial_data)
        })

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):  # pylint: disable=unused-argument
        """Genera PDF de la reserva"""
        reserva = self.get_object()

        # Cargar detalles y adicionales con relaciones
        detalles = reserva.reservadetalle_set.select_related(
            'servicio', 'recoger_en').all()
        adicionales = reserva.reservaadicionaldetalle_set.select_related(
            'adicional').all()

        # Calcular total neto
        total_neto = float(reserva.total) - float(reserva.total_nocontable)

        context = {
            'reserva': reserva,
            'detalles': detalles,
            'adicionales': adicionales,
            'total_neto': total_neto,
        }

        pdf_gen = PDFGenerator(
            'pdf/reserva.html', context, orientation='portrait')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="reserva_{reserva.id}.pdf"'
        return response


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
    filterset_fields = ['pertenece_a', 'servicio', 'cuando', 'idioma',
                        'seleccionado', 'pertenece_a__cliente', 'pertenece_a__estado']
    search_fields = ['pertenece_a__pasajero']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def pdf_servicio_agencias(self, request):
        """Genera PDF del informe de servicios por agencia"""
        # Obtener parámetros
        fecha_desde = request.query_params.get('cuando__gte')
        fecha_hasta = request.query_params.get('cuando__lte')
        cliente_id = request.query_params.get('pertenece_a__cliente')
        estado = request.query_params.get('pertenece_a__estado')

        if not fecha_desde or not fecha_hasta or not cliente_id:
            return Response({'error': 'Faltan parámetros requeridos'}, status=400)

        # Obtener datos
        from base.models import Cliente
        cliente = Cliente.objects.get(id=cliente_id)

        # Servicios con relaciones necesarias
        servicios_qs = self.get_queryset().filter(
            cuando__gte=fecha_desde,
            cuando__lte=fecha_hasta,
            pertenece_a__cliente_id=cliente_id
        ).select_related('servicio', 'recoger_en', 'pertenece_a')
        if estado:
            servicios_qs = servicios_qs.filter(pertenece_a__estado=estado)

        # Crear lista con campos necesarios para el template
        servicios = []
        for s in servicios_qs:
            servicios.append({
                'cuando': s.cuando,
                'servicio_nombre': s.servicio.nombre if s.servicio else '',
                'numero_pax': s.numero_pax,
                'pasajero': s.pertenece_a.pasajero,
                'lugar_nombre': s.recoger_en.nombre if s.recoger_en else '',
                'idioma_display': s.get_idioma_display(),
                'estado_display': s.pertenece_a.get_estado_display(),
                'total': s.total,
                'estado': s.pertenece_a.estado,
            })

        # Adicionales con relaciones necesarias
        adicionales_qs = ReservaAdicionalDetalle.objects.select_related(
            'pertenece_a', 'adicional'
        ).filter(
            cuando__gte=fecha_desde,
            cuando__lte=fecha_hasta,
            pertenece_a__cliente_id=cliente_id
        )
        if estado:
            adicionales_qs = adicionales_qs.filter(pertenece_a__estado=estado)

        # Crear lista con campos necesarios para el template
        adicionales = []
        for a in adicionales_qs:
            adicionales.append({
                'cuando': a.cuando,
                'cantidad': a.cantidad,
                'adicional_nombre': a.adicional.nombre if a.adicional else '',
                'pasajero': a.pertenece_a.pasajero,
                'adicional_contable': a.adicional.contable if a.adicional else True,
                'estado_display': a.pertenece_a.get_estado_display(),
                'total': a.total,
                'estado': a.pertenece_a.estado,
            })

        # Calcular totales
        total_servicios = sum(float(s['total'] or 0) for s in servicios)
        total_servicios_pagados = sum(
            float(s['total'] or 0) for s in servicios if s['estado'] == '0')
        total_servicios_deuda = sum(
            float(s['total'] or 0) for s in servicios if s['estado'] == '1')

        total_adicionales = sum(float(a['total'] or 0) for a in adicionales)
        total_adicionales_pagados = sum(
            float(a['total'] or 0) for a in adicionales if a['estado'] == '0')
        total_adicionales_deuda = sum(
            float(a['total'] or 0) for a in adicionales if a['estado'] == '1')

        context = {
            'cliente_nombre': cliente.nombre,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'estado_filter': dict([('0', 'Pagado'), ('1', 'Deuda')]).get(estado) if estado else None,
            'servicios': servicios,
            'adicionales': adicionales,
            'total_servicios': total_servicios,
            'total_servicios_pagados': total_servicios_pagados,
            'total_servicios_deuda': total_servicios_deuda,
            'total_adicionales': total_adicionales,
            'total_adicionales_pagados': total_adicionales_pagados,
            'total_adicionales_deuda': total_adicionales_deuda,
            'total_general': total_servicios + total_adicionales,
            'total_general_pagado': total_servicios_pagados + total_adicionales_pagados,
            'total_general_deuda': total_servicios_deuda + total_adicionales_deuda,
        }

        pdf_gen = PDFGenerator('pdf/servicio_agencias.html',
                               context, orientation='landscape')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="servicios_agencias_{cliente.nombre}_{fecha_desde}_{fecha_hasta}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def biblia_digital(self, request):
        """
        Reporte Biblia Digital
        Devuelve detalles de reservas para crear órdenes de servicio
        """
        queryset = self.get_queryset()

        # Filtros
        servicio_id = request.query_params.get('servicio')
        fecha_gte = request.query_params.get('fecha__gte')
        fecha_lte = request.query_params.get('fecha__lte')
        fecha_range = request.query_params.get('fecha__range')
        seleccionado = request.query_params.get('seleccionado')
        idioma = request.query_params.get('idioma')

        if servicio_id:
            queryset = queryset.filter(servicio_id=servicio_id)

        if idioma:
            queryset = queryset.filter(idioma=idioma)

        if fecha_range:
            # formato: "fecha_desde,fecha_hasta"
            fechas = fecha_range.split(',')
            if len(fechas) == 2:
                queryset = queryset.filter(
                    cuando__range=[fechas[0], fechas[1]])
        else:
            if fecha_gte:
                queryset = queryset.filter(cuando__gte=fecha_gte)
            if fecha_lte:
                queryset = queryset.filter(cuando__lte=fecha_lte)

        if seleccionado is not None:
            is_selected = seleccionado.lower() == 'true'
            queryset = queryset.filter(seleccionado=is_selected)

        # Paginación y ordenamiento
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        ordering = request.query_params.get('ordering', '-cuando')

        # Mapear campos de ordenamiento a campos del modelo
        ordering_map = {
            'cuando': 'cuando',
            'reserva_fecha': 'pertenece_a__fecha',
            'reserva_numero': 'pertenece_a__numero',
            'cliente_nombre': 'pertenece_a__cliente__nombre',
            'pasajero': 'pertenece_a__pasajero',
            'servicio_nombre': 'servicio__nombre',
            'lugar_nombre': 'recoger_en__nombre',
            '-cuando': '-cuando',
            '-reserva_fecha': '-pertenece_a__fecha',
            '-reserva_numero': '-pertenece_a__numero',
            '-cliente_nombre': '-pertenece_a__cliente__nombre',
            '-pasajero': '-pertenece_a__pasajero',
            '-servicio_nombre': '-servicio__nombre',
            '-lugar_nombre': '-recoger_en__nombre',
        }

        # Aplicar ordenamiento mapeado
        ordering_field = ordering_map.get(ordering, ordering)
        queryset = queryset.order_by(ordering_field)

        # Contar total
        total_count = queryset.count()

        # Aplicar paginación
        start = (page - 1) * page_size
        end = start + page_size
        queryset = queryset[start:end]

        # Serializar con datos adicionales
        results = []
        for detalle in queryset:
            results.append({
                'id': detalle.id,
                'reserva_id': detalle.pertenece_a.id,
                'reserva_numero': detalle.pertenece_a.numero,
                'reserva_fecha': detalle.pertenece_a.fecha,
                'cliente_id': detalle.pertenece_a.cliente.id if detalle.pertenece_a.cliente else None,
                'cliente_nombre': detalle.pertenece_a.cliente.nombre if detalle.pertenece_a.cliente else '',
                'pasajero': detalle.pertenece_a.pasajero,
                'servicio_id': detalle.servicio.id,
                'servicio_nombre': detalle.servicio.nombre,
                'lugar_id': detalle.recoger_en.id if detalle.recoger_en else None,
                'lugar_nombre': detalle.recoger_en.nombre if detalle.recoger_en else '',
                'cuando': detalle.cuando,
                'numero_pax': detalle.numero_pax,
                'subtotal': float(detalle.total) if detalle.total else 0.0,
                'idioma': detalle.idioma,
                'seleccionado': detalle.seleccionado,
                'destino': detalle.destino,
                'tipo_documento': detalle.pertenece_a.tipo_documento,
                'tipo_documento_display': detalle.pertenece_a.get_tipo_documento_display(),
                'observaciones_reserva': detalle.pertenece_a.observaciones or '',
                'estado': detalle.pertenece_a.estado,
                'estado_display': detalle.pertenece_a.get_estado_display(),
                'girado_por': detalle.pertenece_a.girado_por.username if detalle.pertenece_a.girado_por else '',
            })

        return Response({
            'count': total_count,
            'next': None,
            'previous': None,
            'results': results
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
    filterset_fields = ['pertenece_a', 'adicional', 'cuando',
                        'pertenece_a__cliente', 'pertenece_a__estado']
    search_fields = ['pertenece_a__pasajero']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def pdf_adicionales(self, request):
        """Genera PDF del informe de adicionales"""
        fecha_desde = request.query_params.get('cuando__gte')
        fecha_hasta = request.query_params.get('cuando__lte')
        adicional_id = request.query_params.get('adicional')

        if not fecha_desde or not fecha_hasta or not adicional_id:
            return Response({'error': 'Faltan parámetros requeridos'}, status=400)

        from base.models import Adicional
        adicional = Adicional.objects.get(id=adicional_id)

        adicionales_qs = self.get_queryset().filter(
            cuando__gte=fecha_desde,
            cuando__lte=fecha_hasta,
            adicional_id=adicional_id
        ).select_related('pertenece_a', 'adicional')

        # Crear lista con campos necesarios para el template
        adicionales = []
        for a in adicionales_qs:
            adicionales.append({
                'cuando': a.cuando,
                'reserva_id': a.pertenece_a.id,
                'reserva_pasajero': a.pertenece_a.pasajero,
                'adicional_nombre': a.adicional.nombre if a.adicional else '',
                'cantidad': a.cantidad,
                'adicional_precio': a.adicional.precio if a.adicional else 0,
                'adicional_contable': a.adicional.contable if a.adicional else True,
                'total': a.total,
            })

        # Calcular totales
        cantidad_total = sum(a['cantidad'] for a in adicionales)
        total_contable = sum(float(a['total'] or 0)
                             for a in adicionales if a['adicional_contable'])
        total_no_contable = sum(float(a['total'] or 0)
                                for a in adicionales if not a['adicional_contable'])
        total_general = total_contable + total_no_contable

        context = {
            'adicional_nombre': adicional.nombre,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'cantidad_total': cantidad_total,
            'adicionales': adicionales,
            'total_contable': total_contable,
            'total_no_contable': total_no_contable,
            'total_general': total_general,
        }

        pdf_gen = PDFGenerator(
            'pdf/adicionales_reporte.html', context, orientation='landscape')
        pdf_bytes = pdf_gen.generate()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="adicionales_{adicional.nombre}_{fecha_desde}_{fecha_hasta}.pdf"'
        return response

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
        'servicio', 'guia', 'chofer', 'responsable'
    ).prefetch_related(
        'ordenserviciodetalle_set__referencia__pertenece_a'
    ).all()
    serializer_class = OrdenServicioSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['servicio', 'fecha',
                        'idioma', 'guia', 'chofer', 'responsable']
    search_fields = ['servicio__nombre', 'guia__nombre',
                     'chofer__nombre', 'responsable__nombre']
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

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """
        Genera PDF de la orden de servicio
        Parámetros query:
        - mostrar_agencia: true/false (por defecto true) - Muestra información de agencias
        """
        try:
            orden = self.get_object()

            # Obtener parámetro para mostrar/ocultar agencia
            mostrar_agencia = request.query_params.get(
                'mostrar_agencia', 'true').lower() == 'true'

            # Obtener paradas del servicio
            paradas = orden.servicio.paradas.all().order_by('orden')

            # Obtener todos los adicionales de esta fecha de una vez
            adicionales_fecha = ReservaAdicionalDetalle.objects.filter(
                cuando=orden.fecha
            ).select_related('adicional', 'pertenece_a').values(
                'pk', 'pertenece_a_id', 'adicional__nombre', 'adicional__precio',
                'adicional__visible', 'adicional__boleto', 'adicional__almuerzo',
                'cantidad'
            )

            # Crear diccionario de adicionales por reserva
            adicionales_por_reserva = {}
            for adic in adicionales_fecha:
                reserva_id = adic['pertenece_a_id']
                if reserva_id not in adicionales_por_reserva:
                    adicionales_por_reserva[reserva_id] = []
                adicionales_por_reserva[reserva_id].append(adic)

            # Procesar detalles
            detalles_procesados = []
            total_pax = 0
            total_ingresos = 0
            total_almuerzos = 0
            tiene_ingresos = False
            tiene_almuerzos = False
            adicionales_usados = set()

            for detalle_orden in orden.ordenserviciodetalle_set.select_related(
                'referencia__pertenece_a', 'referencia__recoger_en'
            ).all():
                reserva_detalle = detalle_orden.referencia
                reserva = reserva_detalle.pertenece_a

                # Obtener adicionales de esta reserva para esta fecha
                adicionales = adicionales_por_reserva.get(reserva.id, [])

                ingresos_count = 0
                almuerzos_count = 0
                ingresos_list = []
                almuerzos_list = []
                otros_adicionales = []

                for adicional in adicionales:
                    # Evitar duplicados
                    if adicional['pk'] in adicionales_usados:
                        continue

                    adicionales_usados.add(adicional['pk'])

                    # Solo procesar adicionales visibles
                    if not adicional['adicional__visible']:
                        continue

                    if adicional['adicional__boleto']:
                        ingresos_count += adicional['cantidad']
                        ingresos_list.append(
                            f"{adicional['cantidad']}x {adicional['adicional__nombre']}")
                        tiene_ingresos = True
                    elif adicional['adicional__almuerzo']:
                        almuerzos_count += adicional['cantidad']
                        almuerzos_list.append(
                            f"{adicional['cantidad']}x {adicional['adicional__nombre']}")
                        tiene_almuerzos = True
                    else:
                        # Adicionales que no son ingresos ni almuerzos
                        otros_adicionales.append(
                            f"{adicional['cantidad']}x {adicional['adicional__nombre']}")

                total_pax += reserva_detalle.numero_pax
                total_ingresos += ingresos_count
                total_almuerzos += almuerzos_count

                detalles_procesados.append({
                    'numero_pax': reserva_detalle.numero_pax,
                    'lugar_nombre': reserva_detalle.recoger_en.nombre,
                    'pasajero': reserva.pasajero,
                    'destino': reserva_detalle.destino,
                    'ingresos': ', '.join(ingresos_list) if ingresos_list else None,
                    'almuerzos': ', '.join(almuerzos_list) if almuerzos_list else None,
                    'observaciones': reserva.observaciones if reserva.observaciones else '',
                    'otros_adicionales': ', '.join(otros_adicionales) if otros_adicionales else None,
                })

            # Recopilar agencias únicas de las reservas
            agencias = []
            if mostrar_agencia:
                agencias_set = set()
                for detalle_orden in orden.ordenserviciodetalle_set.select_related(
                    'referencia__pertenece_a__cliente'
                ).all():
                    if detalle_orden.referencia.pertenece_a.cliente:
                        agencias_set.add(
                            detalle_orden.referencia.pertenece_a.cliente.nombre)
                agencias = sorted(list(agencias_set))

            context = {
                'orden': orden,
                'paradas': paradas,
                'detalles': detalles_procesados,
                'total_pax': total_pax,
                'total_ingresos': total_ingresos,
                'total_almuerzos': total_almuerzos,
                'tiene_ingresos': tiene_ingresos,
                'tiene_almuerzos': tiene_almuerzos,
                'mostrar_agencia': mostrar_agencia,
                'agencias': agencias,
            }

            pdf_gen = PDFGenerator(
                'pdf/orden_servicio.html', context, orientation='portrait')
            pdf_bytes = pdf_gen.generate()

            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="orden_servicio_{orden.id}.pdf"'
            return response

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
