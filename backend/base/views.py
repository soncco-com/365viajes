"""
ViewSets para el app base
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User, Group
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from .models import (
    OpcionGeneral, Auditoria, Lugar, Servicio,
    Adicional, Cliente, Horario, Guia, Chofer, Responsable,
    ServicioPrecioEspecial, ServicioParada, AdicionalPrecioEspecial
)
from .serializers import (
    OpcionGeneralSerializer, AuditoriaSerializer, LugarSerializer,
    ServicioSerializer, AdicionalSerializer,
    ClienteSerializer, ChoferSerializer, GuiaSerializer, HorarioSerializer,
    ResponsableSerializer, UserSerializer, GroupSerializer,
    ServicioPrecioEspecialSerializer, ServicioParadaSerializer,
    AdicionalPrecioEspecialSerializer
)


class OpcionGeneralViewSet(viewsets.ModelViewSet):
    """
    ViewSet para opciones generales del sistema
    """
    queryset = OpcionGeneral.objects.all()
    serializer_class = OpcionGeneralSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['clave', 'es_publica']
    search_fields = ['clave', 'valor', 'descripcion']
    ordering_fields = '__all__'

    def get_permissions(self):
        """Las opciones públicas no requieren autenticación y el endpoint del logo es público"""
        if self.action in ['logo'] or (self.action == 'list' and self.request.query_params.get('es_publica') == 'true'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'post'], url_path='logo')
    def logo(self, request):
        """
        GET: Obtiene el logo del sistema (base64)
        POST: Actualiza el logo del sistema (base64)
        """
        if request.method == 'GET':
            try:
                opcion = OpcionGeneral.objects.get(clave='logo_sistema')
                return Response({'valor': opcion.valor})
            except OpcionGeneral.DoesNotExist:
                return Response({'valor': ''}, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            logo_data = request.data.get('logo')
            if not logo_data:
                return Response({'error': 'No se proporcionó el logo'}, status=status.HTTP_400_BAD_REQUEST)

            # Validar que sea una imagen base64 válida
            if not logo_data.startswith('data:image/'):
                return Response({'error': 'El logo debe ser una imagen en formato base64'}, status=status.HTTP_400_BAD_REQUEST)

            opcion, _ = OpcionGeneral.objects.get_or_create(
                clave='logo_sistema',
                defaults={
                    'descripcion': 'Logo del sistema en formato base64',
                    'es_publica': True
                }
            )
            opcion.valor = logo_data
            opcion.save()

            return Response({'message': 'Logo actualizado correctamente', 'valor': logo_data}, status=status.HTTP_200_OK)


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para auditoría
    Solo administradores pueden ver la auditoría
    """
    queryset = Auditoria.objects.select_related(
        'usuario', 'content_type').all()
    serializer_class = AuditoriaSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'accion': ['exact'],
        'usuario': ['exact'],
        'content_type': ['exact'],
        'fecha': ['exact', 'gte', 'lte', 'range'],
    }
    search_fields = ['usuario__username', 'datos_anteriores', 'datos_nuevos']
    ordering_fields = '__all__'
    ordering = ['-fecha']


class LugarViewSet(viewsets.ModelViewSet):
    """ViewSet para Lugares (Hoteles)"""
    queryset = Lugar.objects.all()
    serializer_class = LugarSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'telefonos']
    ordering_fields = '__all__'

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo lugares activos para autocompletes"""
        queryset = self.queryset.filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ServicioViewSet(viewsets.ModelViewSet):
    """ViewSet para Servicios"""
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre']
    ordering_fields = '__all__'

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo servicios activos"""
        queryset = self.queryset.filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdicionalViewSet(viewsets.ModelViewSet):
    """ViewSet para Adicionales"""
    queryset = Adicional.objects.all()
    serializer_class = AdicionalSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'contable', 'almuerzo', 'boleto', 'visible']
    search_fields = ['nombre']
    ordering_fields = '__all__'

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo adicionales activos"""
        queryset = self.queryset.filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para Clientes (Agencias)"""
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'telefonos']
    ordering_fields = '__all__'

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo clientes activos"""
        queryset = self.queryset.filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HorarioViewSet(viewsets.ModelViewSet):
    """ViewSet para Horarios"""
    queryset = Horario.objects.select_related('servicio', 'lugar').all()
    serializer_class = HorarioSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['servicio', 'lugar']
    search_fields = ['servicio__nombre', 'lugar__nombre']
    ordering_fields = '__all__'


class GuiaViewSet(viewsets.ModelViewSet):
    """ViewSet para Guías"""
    queryset = Guia.objects.all()
    serializer_class = GuiaSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'telefono']
    ordering_fields = '__all__'


class ChoferViewSet(viewsets.ModelViewSet):
    """ViewSet para Choferes"""
    queryset = Chofer.objects.all()
    serializer_class = ChoferSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'telefono']
    ordering_fields = '__all__'


class ResponsableViewSet(viewsets.ModelViewSet):
    """ViewSet para Responsables"""
    queryset = Responsable.objects.all()
    serializer_class = ResponsableSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'telefono']
    ordering_fields = '__all__'

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo responsables activos"""
        queryset = self.queryset.filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para Usuarios"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'groups']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = '__all__'

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint para obtener datos del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        """Endpoint para cambiar password de un usuario"""
        user = self.get_object()
        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password requerido'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({'message': 'Password cambiado exitosamente'})


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Grupos (solo lectura)"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def list(self, request):
        """Listar todos los grupos"""
        groups = Group.objects.all()
        data = [{'id': g.id, 'name': g.name} for g in groups]
        return Response(data)


class ServicioPrecioEspecialViewSet(viewsets.ModelViewSet):
    """ViewSet para Precios Especiales de Servicios"""
    queryset = ServicioPrecioEspecial.objects.select_related(
        'servicio', 'cliente').all()
    serializer_class = ServicioPrecioEspecialSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['servicio', 'cliente', 'activo']
    search_fields = ['servicio__nombre', 'cliente__nombre', 'observaciones']
    ordering_fields = '__all__'
    ordering = ['-fecha_desde']


class ServicioParadaViewSet(viewsets.ModelViewSet):
    """ViewSet para Paradas de Servicios"""
    queryset = ServicioParada.objects.select_related('servicio').all()
    serializer_class = ServicioParadaSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['servicio']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = '__all__'
    ordering = ['servicio', 'orden']


class AdicionalPrecioEspecialViewSet(viewsets.ModelViewSet):
    """ViewSet para Precios Especiales de Adicionales"""
    queryset = AdicionalPrecioEspecial.objects.select_related(
        'adicional', 'cliente').all()
    serializer_class = AdicionalPrecioEspecialSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['adicional', 'cliente', 'activo']
    search_fields = ['adicional__nombre', 'cliente__nombre', 'observaciones']
    ordering_fields = '__all__'
    ordering = ['-fecha_desde']
