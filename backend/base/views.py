"""
ViewSets para el app base
"""
from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User, Group
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from .models import (
    OpcionGeneral, Auditoria, Lugar, Formato, Servicio,
    Adicional, Cliente, Horario, Guia, Chofer,
    ServicioPrecioEspecial, ServicioParada
)
from .serializers import (
    OpcionGeneralSerializer, AuditoriaSerializer, LugarSerializer,
    FormatoSerializer, ServicioSerializer, AdicionalSerializer,
    ClienteSerializer, HorarioSerializer, GuiaSerializer,
    ChoferSerializer, UserSerializer,
    ServicioPrecioEspecialSerializer, ServicioParadaSerializer
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
        """Las opciones públicas no requieren autenticación"""
        if self.action == 'list' and self.request.query_params.get('es_publica') == 'true':
            return [AllowAny()]
        return [IsAuthenticated()]

    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
    filterset_fields = ['accion', 'usuario', 'content_type', 'fecha']
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


class FormatoViewSet(viewsets.ModelViewSet):
    """ViewSet para Formatos"""
    queryset = Formato.objects.all()
    serializer_class = FormatoSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = '__all__'


class ServicioViewSet(viewsets.ModelViewSet):
    """ViewSet para Servicios"""
    queryset = Servicio.objects.select_related('formato').all()
    serializer_class = ServicioSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'formato']
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
    serializer_class = serializers.Serializer

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
