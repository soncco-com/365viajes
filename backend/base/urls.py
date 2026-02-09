"""
URLs para el app base
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OpcionGeneralViewSet, AuditoriaViewSet, LugarViewSet,
    ServicioViewSet, AdicionalViewSet,
    ClienteViewSet, ChoferViewSet, GuiaViewSet, HorarioViewSet,
    ResponsableViewSet, UserViewSet, GroupViewSet,
    ServicioPrecioEspecialViewSet, ServicioParadaViewSet,
    AdicionalPrecioEspecialViewSet
)

router = DefaultRouter()
router.register(r'opciones-generales', OpcionGeneralViewSet,
                basename='opcion-general')
router.register(r'auditoria', AuditoriaViewSet, basename='auditoria')
router.register(r'lugares', LugarViewSet, basename='lugar')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'adicionales', AdicionalViewSet, basename='adicional')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'guias', GuiaViewSet, basename='guia')
router.register(r'choferes', ChoferViewSet, basename='chofer')
router.register(r'responsables', ResponsableViewSet, basename='responsable')
router.register(r'usuarios', UserViewSet, basename='usuario')
router.register(r'grupos', GroupViewSet, basename='grupo')
router.register(r'servicio-precios-especiales',
                ServicioPrecioEspecialViewSet, basename='servicio-precio-especial')
router.register(r'servicio-paradas', ServicioParadaViewSet,
                basename='servicio-parada')
router.register(r'adicional-precios-especiales',
                AdicionalPrecioEspecialViewSet, basename='adicional-precio-especial')

urlpatterns = [
    path('', include(router.urls)),
]
