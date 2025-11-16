from django.contrib import admin
from .models import Reserva, ReservaDetalle, ReservaAdicionalDetalle, OrdenServicio, OrdenServicioDetalle, Gasto


class ReservaDetalleInline(admin.TabularInline):
    model = ReservaDetalle
    extra = 1


class ReservaAdicionalDetalleInline(admin.TabularInline):
    model = ReservaAdicionalDetalle
    extra = 1


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha',
                    'pasajero', 'total', 'estado', 'numero']
    list_filter = ['estado', 'tipo_documento', 'tipo_pago', 'fecha']
    search_fields = ['pasajero', 'numero', 'numero_factura']
    inlines = [ReservaDetalleInline, ReservaAdicionalDetalleInline]


@admin.register(ReservaDetalle)
class ReservaDetalleAdmin(admin.ModelAdmin):
    list_display = ['pertenece_a', 'servicio',
                    'numero_pax', 'cuando', 'idioma', 'seleccionado']
    list_filter = ['idioma', 'seleccionado', 'cuando']
    search_fields = ['pertenece_a__pasajero', 'servicio__nombre']


@admin.register(ReservaAdicionalDetalle)
class ReservaAdicionalDetalleAdmin(admin.ModelAdmin):
    list_display = ['pertenece_a', 'adicional', 'cantidad', 'cuando']
    list_filter = ['cuando']
    search_fields = ['pertenece_a__pasajero', 'adicional__nombre']


class OrdenServicioDetalleInline(admin.TabularInline):
    model = OrdenServicioDetalle
    extra = 0


@admin.register(OrdenServicio)
class OrdenServicioAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'servicio',
                    'guia', 'chofer', 'responsable', 'idioma']
    list_filter = ['fecha', 'servicio', 'idioma']
    search_fields = ['servicio__nombre', 'guia__nombre',
                     'chofer__nombre', 'responsable__nombre']
    inlines = [OrdenServicioDetalleInline]


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'descripcion', 'monto', 'creado_por']
    list_filter = ['fecha', 'creado_por']
    search_fields = ['descripcion']
