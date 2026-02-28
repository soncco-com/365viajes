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
    """
    Serializa una instancia de modelo a JSON con valores legibles
    Incluye nombres de relaciones y valores display de choices
    """
    try:
        # Obtener campos del modelo
        campos = {}
        for field in instancia._meta.fields:
            field_name = field.name
            field_value = getattr(instancia, field_name, None)

            # Para campos con choices, guardar tanto el valor como el display
            if hasattr(field, 'choices') and field.choices:
                campos[field_name] = field_value
                # Intentar obtener el display
                display_method = f'get_{field_name}_display'
                if hasattr(instancia, display_method):
                    display_value = getattr(instancia, display_method)()
                    campos[f'{field_name}_display'] = display_value
            # Para DateTimeField/DateField
            elif hasattr(field_value, 'isoformat'):
                campos[field_name] = field_value.isoformat()
            # Para ForeignKey - guardar ID y representación
            elif hasattr(field_value, 'pk'):
                campos[field_name] = field_value.pk
                # Intentar obtener el nombre o representación legible
                if hasattr(field_value, 'nombre'):
                    campos[f'{field_name}_nombre'] = field_value.nombre
                elif hasattr(field_value, 'username'):
                    campos[f'{field_name}_username'] = field_value.username
                elif hasattr(field_value, 'first_name') and field_value.first_name:
                    campos[f'{field_name}_nombre'] = f"{field_value.first_name} {getattr(field_value, 'last_name', '')}".strip(
                    )
                else:
                    campos[f'{field_name}_str'] = str(field_value)
            # Para valores simples
            elif isinstance(field_value, (str, int, float, bool, type(None))):
                campos[field_name] = field_value
            else:
                campos[field_name] = str(field_value)

        return campos
    except Exception as e:
        # Fallback: intentar con el serializador original
        try:
            data = serialize('json', [instancia])
            return json.loads(data)[0]['fields']
        except:
            return {'error': f'No se pudo serializar: {str(e)}'}


def obtener_usuario_actual():
    """
    Obtiene el usuario actual desde el middleware local thread
    Compatible con autenticación JWT de DRF
    """
    from threading import current_thread
    thread = current_thread()

    # Primero intentar obtener del thread directamente (para compatibilidad)
    usuario = getattr(thread, 'auditoria_usuario', None)
    if usuario and usuario.is_authenticated:
        return usuario

    # Si no está, obtener del request (para autenticación JWT de DRF)
    request = getattr(thread, 'auditoria_request', None)
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user

    return None


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
