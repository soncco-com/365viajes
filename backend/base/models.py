from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from decimal import Decimal


class OpcionGeneral(models.Model):
    """Configuración general del sistema"""
    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    descripcion = models.TextField(blank=True, null=True)
    es_publica = models.BooleanField(
        default=False, help_text="Si es pública, no requiere login para acceder")

    class Meta:
        verbose_name = 'Opción General'
        verbose_name_plural = 'Opciones Generales'

    def __str__(self):
        return self.clave


class Auditoria(models.Model):
    """Registro de auditoría para todos los modelos"""
    ACCIONES = (
        ('C', 'Creación'),
        ('E', 'Edición'),
        ('D', 'Eliminación'),
    )

    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    accion = models.CharField(max_length=1, choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_accion_display()} - {self.content_type} - {self.usuario} - {self.fecha}'


class Lugar(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    telefonos = models.CharField(max_length=30, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hoteles'

    def __str__(self):
        return self.nombre


class Formato(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))
    fecha_precio = models.DateField()
    activo = models.BooleanField(default=True)
    formato = models.ForeignKey(Formato, on_delete=models.PROTECT)
    cantidad_carrito = models.IntegerField(default=20)

    def __str__(self):
        return '%s (%s)' % (self.nombre, self.fecha_precio.strftime('%m/%Y'))


class Adicional(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))
    fecha_precio = models.DateField()
    activo = models.BooleanField(default=True)
    contable = models.BooleanField(default=True)
    almuerzo = models.BooleanField(default=False)
    boleto = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Adicionales'

    def __str__(self):
        return '%s (%s)' % (self.nombre, self.fecha_precio.strftime('%m/%Y'))


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    telefonos = models.CharField(max_length=30, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Agencia'
        verbose_name_plural = 'Agencias'

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    lugar = models.ForeignKey(Lugar, on_delete=models.PROTECT)
    hora = models.TimeField()

    def __str__(self):
        return '%s - %s' % (self.servicio, self.lugar)


class Guia(models.Model):
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=40)

    def __str__(self):
        return self.nombre


class Chofer(models.Model):
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'Transporte'
        verbose_name_plural = 'Transportes'

    def __str__(self):
        return self.nombre
