"""
Señales para auditoría automática de modelos
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
import json

from .models import Auditoria


# Lista de modelos que NO deben ser auditados
MODELOS_EXCLUIDOS = ['Auditoria', 'Session', 'ContentType', 'LogEntry']


def obtener_datos_modelo(instancia):
    """Serializa una instancia de modelo a JSON"""
    try:
        data = serialize('json', [instancia])
        return json.loads(data)[0]['fields']
    except:
        return {}


def obtener_usuario_actual():
    """
    Obtiene el usuario actual desde el middleware local thread
    Requiere implementar middleware de auditoría
    """
    from threading import current_thread
    return getattr(current_thread(), 'auditoria_usuario', None)


def obtener_ip_actual():
    """Obtiene la IP actual desde el middleware local thread"""
    from threading import current_thread
    return getattr(current_thread(), 'auditoria_ip', None)


# Almacenamiento temporal de datos antes de guardar
_datos_anteriores = {}


@receiver(pre_save)
def guardar_datos_anteriores(sender, instance, **kwargs):
    """Guarda los datos anteriores antes de modificar"""
    if sender.__name__ in MODELOS_EXCLUIDOS:
        return

    if instance.pk:
        try:
            instancia_anterior = sender.objects.get(pk=instance.pk)
            _datos_anteriores[instance.pk] = obtener_datos_modelo(
                instancia_anterior)
        except sender.DoesNotExist:
            pass


@receiver(post_save)
def auditar_creacion_edicion(sender, instance, created, **kwargs):
    """Audita creaciones y ediciones de modelos"""
    if sender.__name__ in MODELOS_EXCLUIDOS:
        return

    usuario = obtener_usuario_actual()
    if not usuario:
        return  # No auditar si no hay usuario (migraciones, scripts, etc.)

    content_type = ContentType.objects.get_for_model(sender)
    datos_nuevos = obtener_datos_modelo(instance)

    if created:
        accion = 'C'
        datos_anteriores = None
    else:
        accion = 'E'
        datos_anteriores = _datos_anteriores.pop(instance.pk, None)

    Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        content_type=content_type,
        object_id=instance.pk,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        ip_address=obtener_ip_actual()
    )


@receiver(post_delete)
def auditar_eliminacion(sender, instance, **kwargs):
    """Audita eliminaciones de modelos"""
    if sender.__name__ in MODELOS_EXCLUIDOS:
        return

    usuario = obtener_usuario_actual()
    if not usuario:
        return

    content_type = ContentType.objects.get_for_model(sender)
    datos_anteriores = obtener_datos_modelo(instance)

    Auditoria.objects.create(
        usuario=usuario,
        accion='D',
        content_type=content_type,
        object_id=instance.pk,
        datos_anteriores=datos_anteriores,
        ip_address=obtener_ip_actual()
    )
