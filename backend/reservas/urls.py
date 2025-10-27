"""
URLs para el app reservas
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReservaViewSet, ReservaDetalleViewSet, ReservaAdicionalDetalleViewSet,
    OrdenServicioViewSet, GastoViewSet
)

router = DefaultRouter()
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'reserva-detalles', ReservaDetalleViewSet,
                basename='reserva-detalle')
router.register(r'reserva-adicionales',
                ReservaAdicionalDetalleViewSet, basename='reserva-adicional')
router.register(r'ordenes-servicio', OrdenServicioViewSet,
                basename='orden-servicio')
router.register(r'gastos', GastoViewSet, basename='gasto')

urlpatterns = [
    path('', include(router.urls)),
]
