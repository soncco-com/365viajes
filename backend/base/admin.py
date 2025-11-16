from django.contrib import admin
from .models import (
    OpcionGeneral, Auditoria, Lugar, Servicio,
    Adicional, Cliente, Chofer, Guia, Horario, Responsable
)


@admin.register(OpcionGeneral)
class OpcionGeneralAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor', 'es_publica']
    list_filter = ['es_publica']
    search_fields = ['clave', 'valor']


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'content_type', 'object_id', 'fecha']
    list_filter = ['accion', 'fecha', 'content_type']
    search_fields = ['usuario__username']
    readonly_fields = ['usuario', 'accion', 'fecha', 'content_type',
                       'object_id', 'datos_anteriores', 'datos_nuevos', 'ip_address']


@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefonos', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'fecha_precio', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Adicional)
class AdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'fecha_precio',
                    'activo', 'contable', 'visible']
    list_filter = ['activo', 'contable', 'almuerzo', 'boleto', 'visible']
    search_fields = ['nombre']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefonos', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'lugar', 'hora']
    list_filter = ['servicio', 'lugar']


@admin.register(Guia)
class GuiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono']
    search_fields = ['nombre']


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono']
    search_fields = ['nombre']


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
