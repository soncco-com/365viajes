from django.db import models
from django.contrib.auth.models import User

from decimal import Decimal

IDIOMAS = (
    ('en', 'Inglés'),
    ('es', 'Español'),
    ('xx', 'Bilingüe'),
)


class Reserva(models.Model):
    ESTADOS = (
        ('0', 'Pagado'),
        ('1', 'Deuda'),
    )
    DOCUMENTOS = (
        ('0', 'Boleta'),
        ('1', 'Factura'),
        ('2', 'Otros'),
    )
    PAGOS = (
        ('0', 'Efectivo'),
        ('1', 'Depósito'),
        ('2', 'Otro'),
    )
    cliente = models.ForeignKey('base.Cliente', on_delete=models.PROTECT)
    fecha = models.DateField()
    pasajero = models.CharField(max_length=255, default='')
    total = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))
    total_nocontable = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(max_length=1, choices=ESTADOS, default='1')
    tipo_documento = models.CharField(
        max_length=1, choices=DOCUMENTOS, default='2')
    tipo_pago = models.CharField(
        max_length=1, choices=PAGOS, null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    girado_por = models.ForeignKey(
        User, related_name='girado', on_delete=models.PROTECT)
    girado_cuando = models.DateTimeField(blank=True, null=True)
    numero = models.CharField(max_length=100, null=True, blank=True)
    cuentas = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)
    numero_factura = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '%s (%s)' % (self.cliente, self.fecha.strftime('%d/%m/%Y'))


class ReservaDetalle(models.Model):

    pertenece_a = models.ForeignKey(Reserva, on_delete=models.PROTECT)
    numero_pax = models.IntegerField()
    servicio = models.ForeignKey('base.Servicio', on_delete=models.PROTECT)
    recoger_en = models.ForeignKey('base.Lugar', on_delete=models.PROTECT)
    cuando = models.DateField()
    total = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))
    seleccionado = models.BooleanField(default=False)
    idioma = models.CharField(max_length=2, choices=IDIOMAS, default='es')

    def __str__(self):
        return '%s pertenece a %s' % (self.servicio.nombre, self.pertenece_a.id)


class ReservaAdicionalDetalle(models.Model):
    pertenece_a = models.ForeignKey(Reserva, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    adicional = models.ForeignKey('base.Adicional', on_delete=models.PROTECT)
    cuando = models.DateField()
    total = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))


class OrdenServicio(models.Model):
    fecha = models.DateField()
    chofer = models.ForeignKey('base.Chofer', on_delete=models.PROTECT)
    guia = models.ForeignKey('base.Guia', on_delete=models.PROTECT)
    servicio = models.ForeignKey('base.Servicio', on_delete=models.PROTECT)
    idioma = models.CharField(max_length=2, choices=IDIOMAS, default='es')

    class Meta:
        verbose_name_plural = 'Órdenes de Servicio'


class OrdenServicioDetalle(models.Model):
    pertenece_a = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE)
    referencia = models.ForeignKey(ReservaDetalle, on_delete=models.PROTECT)
    sort = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort']


class Gasto(models.Model):
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(
        max_digits=11, decimal_places=2, default=Decimal('0.00'))
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT)
