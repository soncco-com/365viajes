"""
URLs para el app base
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OpcionGeneralViewSet, AuditoriaViewSet, LugarViewSet,
    FormatoViewSet, ServicioViewSet, AdicionalViewSet,
    ClienteViewSet, HorarioViewSet, GuiaViewSet,
    ChoferViewSet, UserViewSet, GroupViewSet
)

router = DefaultRouter()
router.register(r'opciones-generales', OpcionGeneralViewSet,
                basename='opcion-general')
router.register(r'auditoria', AuditoriaViewSet, basename='auditoria')
router.register(r'lugares', LugarViewSet, basename='lugar')
router.register(r'formatos', FormatoViewSet, basename='formato')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'adicionales', AdicionalViewSet, basename='adicional')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'guias', GuiaViewSet, basename='guia')
router.register(r'choferes', ChoferViewSet, basename='chofer')
router.register(r'usuarios', UserViewSet, basename='usuario')
router.register(r'grupos', GroupViewSet, basename='grupo')

urlpatterns = [
    path('', include(router.urls)),
]
