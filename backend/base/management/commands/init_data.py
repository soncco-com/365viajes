"""
Comando para inicializar datos de prueba del sistema
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from base.models import OpcionGeneral, Cliente, Lugar, Formato, Servicio, Adicional, Guia, Chofer
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Inicializa el sistema con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Inicializando datos de prueba...')

        # Crear grupo Administrador
        admin_group, created = Group.objects.get_or_create(
            name='Administrador')
        if created:
            self.stdout.write(self.style.SUCCESS(
                '✓ Grupo Administrador creado'))

        # Crear opciones generales
        opciones = [
            {'clave': 'nombre_empresa', 'valor': '365 Viajes',
                'es_publica': True, 'descripcion': 'Nombre de la empresa'},
            {'clave': 'direccion', 'valor': 'Av. Principal 123, Cusco',
                'es_publica': True, 'descripcion': 'Dirección de la empresa'},
            {'clave': 'telefonos', 'valor': '(084) 123-4567 / 987-654-321',
             'es_publica': True, 'descripcion': 'Teléfonos de contacto'},
            {'clave': 'email', 'valor': 'info@365viajes.com',
                'es_publica': True, 'descripcion': 'Email de contacto'},
        ]

        for opcion_data in opciones:
            OpcionGeneral.objects.get_or_create(
                clave=opcion_data['clave'],
                defaults=opcion_data
            )
        self.stdout.write(self.style.SUCCESS('✓ Opciones generales creadas'))

        # Crear clientes (agencias)
        clientes_data = [
            {'nombre': 'Agencia Sol del Cusco',
                'telefonos': '984-123-456', 'activo': True},
            {'nombre': 'Turismo Inka', 'telefonos': '984-234-567', 'activo': True},
            {'nombre': 'Viajes Machu Picchu',
                'telefonos': '984-345-678', 'activo': True},
        ]

        for cliente_data in clientes_data:
            Cliente.objects.get_or_create(
                nombre=cliente_data['nombre'],
                defaults=cliente_data
            )
        self.stdout.write(self.style.SUCCESS('✓ Clientes (agencias) creadas'))

        # Crear lugares (hoteles)
        lugares_data = [
            {'nombre': 'Hotel Costa del Sol',
                'telefonos': '084-123-456', 'activo': True},
            {'nombre': 'Hotel Monasterio', 'telefonos': '084-234-567', 'activo': True},
            {'nombre': 'Hotel Novotel', 'telefonos': '084-345-678', 'activo': True},
            {'nombre': 'Hotel Plaza de Armas',
                'telefonos': '084-456-789', 'activo': True},
        ]

        for lugar_data in lugares_data:
            Lugar.objects.get_or_create(
                nombre=lugar_data['nombre'],
                defaults=lugar_data
            )
        self.stdout.write(self.style.SUCCESS('✓ Lugares (hoteles) creados'))

        servicios_data = [
            {'nombre': 'City Tour Cusco', 'precio': Decimal(
                '35.00'), 'activo': True},
            {'nombre': 'Valle Sagrado', 'precio': Decimal(
                '45.00'), 'activo': True},
            {'nombre': 'Machu Picchu Full Day', 'precio': Decimal(
                '120.00'), 'activo': True},
            {'nombre': 'Montaña de Colores', 'precio': Decimal(
                '40.00'), 'activo': True},
            {'nombre': 'City Tour Privado', 'precio': Decimal(
                '80.00'), 'activo': True},
        ]

        for servicio_data in servicios_data:
            servicio_data['fecha_precio'] = date.today()
            Servicio.objects.get_or_create(
                nombre=servicio_data['nombre'],
                defaults=servicio_data
            )
        self.stdout.write(self.style.SUCCESS('✓ Servicios creados'))

        # Crear adicionales
        adicionales_data = [
            {'nombre': 'Almuerzo Buffet', 'precio': Decimal(
                '15.00'), 'contable': True, 'almuerzo': True, 'activo': True},
            {'nombre': 'Entrada Machu Picchu', 'precio': Decimal(
                '60.00'), 'contable': False, 'boleto': True, 'activo': True},
            {'nombre': 'Bus Consettur', 'precio': Decimal(
                '12.00'), 'contable': False, 'boleto': True, 'activo': True},
            {'nombre': 'Entrada Salineras', 'precio': Decimal(
                '10.00'), 'contable': False, 'boleto': True, 'activo': True},
        ]

        for adicional_data in adicionales_data:
            adicional_data['fecha_precio'] = date.today()
            Adicional.objects.get_or_create(
                nombre=adicional_data['nombre'],
                defaults=adicional_data
            )
        self.stdout.write(self.style.SUCCESS('✓ Adicionales creados'))

        # Crear guías
        guias_data = [
            {'nombre': 'Juan Pérez', 'telefono': '984-111-222'},
            {'nombre': 'María García', 'telefono': '984-222-333'},
            {'nombre': 'Pedro Quispe', 'telefono': '984-333-444'},
        ]

        for guia_data in guias_data:
            Guia.objects.get_or_create(
                nombre=guia_data['nombre'],
                defaults=guia_data
            )
        self.stdout.write(self.style.SUCCESS('✓ Guías creados'))

        # Crear choferes (transportes)
        choferes_data = [
            {'nombre': 'Carlos Mamani - Bus 01', 'telefono': '984-444-555'},
            {'nombre': 'José Huamán - Van 02', 'telefono': '984-555-666'},
            {'nombre': 'Luis Ccama - Bus 03', 'telefono': '984-666-777'},
        ]

        for chofer_data in choferes_data:
            Chofer.objects.get_or_create(
                nombre=chofer_data['nombre'],
                defaults=chofer_data
            )
        self.stdout.write(self.style.SUCCESS(
            '✓ Choferes (transportes) creados'))

        self.stdout.write(self.style.SUCCESS(
            '\n✓ ¡Inicialización completada exitosamente!'))
        self.stdout.write('\nPróximos pasos:')
        self.stdout.write(
            '1. Crear superusuario: python manage.py createsuperuser')
        self.stdout.write(
            '2. Agregar usuario al grupo Administrador desde el admin de Django')
        self.stdout.write('3. Iniciar servidor: python manage.py runserver')
