# Backend - Documentación Técnica

## Estructura del Proyecto

### Apps

- **base/**: Modelos core del sistema (Cliente, Servicio, Lugar, Adicional, Guía, Chofer, Horario)
- **reservas/**: Lógica de negocio de reservas (Reserva, ReservaDetalle, OrdenServicio, Gasto)

### Modelos Principales

#### base.OpcionGeneral

Almacena configuraciones generales del sistema (nombre empresa, dirección, teléfonos, etc.)

- `clave`: Identificador único de la opción
- `valor`: Valor de la opción
- `es_publica`: Si es accesible sin autenticación

#### base.Auditoria

Sistema de auditoría automática que registra todas las operaciones create/update/delete

- Se activa mediante señales de Django
- Captura usuario, IP, datos anteriores y nuevos
- Middleware `AuditoriaMiddleware` necesario para capturar usuario e IP

#### reservas.Reserva

Reserva principal con cliente, pasajero y totales

- **Estado '0' (Pagado)**: Auto-asigna `numero` (max+1), `girado_por` y `girado_cuando`
- Campos relacionados: ReservaDetalle (servicios), ReservaAdicionalDetalle (extras)

#### reservas.ReservaDetalle

Detalle de servicios contratados

- `seleccionado`: Se marca como `True` cuando se crea una OrdenServicio

#### reservas.OrdenServicio

Orden de servicio que asigna Guía y Chofer

- Al crear: marca `ReservaDetalle.seleccionado=True`
- Al eliminar: restaura `ReservaDetalle.seleccionado=False`

## API Endpoints

### Autenticación

- `POST /api/token/` - Obtener access y refresh token
- `POST /api/token/refresh/` - Renovar access token

### Base

- `/api/base/opciones-generales/` - CRUD opciones generales
- `/api/base/auditoria/` - Solo lectura, historial de cambios
- `/api/base/lugares/` - CRUD hoteles
  - `GET /api/base/lugares/activos/` - Solo activos
- `/api/base/servicios/` - CRUD servicios
  - `GET /api/base/servicios/activos/` - Solo activos
- `/api/base/adicionales/` - CRUD adicionales
  - `GET /api/base/adicionales/activos/` - Solo activos
- `/api/base/clientes/` - CRUD agencias
  - `GET /api/base/clientes/activos/` - Solo activos
- `/api/base/horarios/` - CRUD horarios
- `/api/base/guias/` - CRUD guías
- `/api/base/choferes/` - CRUD choferes (transportes)
- `/api/base/usuarios/` - CRUD usuarios
  - `POST /api/base/usuarios/{id}/cambiar_password/` - Cambiar contraseña

### Reservas

- `/api/reservas/reservas/` - CRUD reservas
  - `GET /api/reservas/reservas/totales/` - Totales de reservas filtradas
- `/api/reservas/reserva-detalles/` - Ver detalles de reservas
  - `GET /api/reservas/reserva-detalles/biblia_digital/` - Reporte Biblia Digital
- `/api/reservas/reserva-adicionales/` - Ver detalles de adicionales
  - `GET /api/reservas/reserva-adicionales/informe/` - Informe de adicionales
- `/api/reservas/ordenes-servicio/` - CRUD órdenes de servicio
  - `DELETE /api/reservas/ordenes-servicio/{id}/eliminar_detalle/` - Eliminar detalle
- `/api/reservas/gastos/` - CRUD gastos (filtrado por usuario si no es admin)
  - `GET /api/reservas/gastos/totales/` - Totales de gastos filtrados

## Filtros de Fecha

Todos los endpoints soportan filtros de rango de fechas:

- `fecha__gte=YYYY-MM-DD` - Desde
- `fecha__lte=YYYY-MM-DD` - Hasta
- `fecha__range=YYYY-MM-DD,YYYY-MM-DD` - Rango completo

## Sistema de Caché

Se usa Redis para cachear endpoints de catálogos:

- `/activos/` endpoints: 5 minutos
- Opciones generales: 15 minutos

El caché se invalida automáticamente al modificar datos mediante señales.

## Sistema de Auditoría

### Configuración

1. Modelo `Auditoria` en `base/models.py`
2. Señales en `base/signals.py`
3. Middleware `AuditoriaMiddleware` en `base/middleware.py`
4. Registrar señales en `base/apps.py`

### Exclusiones

Modelos excluidos de auditoría (ver `base/signals.py`):

- Auditoria (evitar recursión)
- Session
- ContentType
- LogEntry

## PDFs con WeasyPrint

### Generador Centralizado

Clase `PDFGenerator` en `base/utils/pdf_generator.py`

```python
from base.utils.pdf_generator import PDFGenerator

pdf_gen = PDFGenerator(
    template_name='pdf/reserva.html',
    context={'reserva': reserva},
    orientation='portrait',  # o 'landscape'
    include_header=True
)
pdf_bytes = pdf_gen.generate()
```

### Templates

- `base/templates/pdf/base.html` - Template base con cabecera común
- `base/templates/pdf/reserva.html` - Template de reserva
- Crear nuevos templates extendiendo `pdf/base.html`

### Cabecera Común

- Logo desde `STATIC_ROOT`
- Nombre de empresa desde OpcionGeneral
- Configurable por reporte

## Comandos de Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Crear grupo Administrador
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.create(name='Administrador')

# Correr servidor
python manage.py runserver

# O con Docker
docker-compose up
```

## Configuración de Entorno

Archivo `.env` necesario:

```env
SECRET_KEY=tu-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
INSTALLED_APPS=base,reservas
EXTERNAL_APPS=rest_framework,rest_framework_simplejwt,django_filters,corsheaders
DB_NAME=db
DB_USER=root
DB_PASS=root
DB_HOST=db
REDIS_SERVER=redis
CORS_ALLOWED_ORIGINS=http://localhost:9000
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

## Permisos por Grupo

### Todos los usuarios

- Reservas (CRUD)
- Informes (la mayoría)
- Agencias, Hoteles (CRUD)
- Gastos (solo propios)

### Grupo "Administrador"

- Usuarios (CRUD)
- Adicionales (CRUD)
- Guías, Servicios, Transportes (CRUD)
- Horarios (CRUD)
- Auditoría (lectura)
- Rendición de ventas
- Gastos de todos los usuarios

## Lógica de Negocio Especial

### Al crear/editar Reserva con estado='0' (Pagado)

1. Si `reserva.numero` es None/vacío: asignar max(numero)+1
2. Si `reserva.girado_cuando` es None: asignar now()
3. `reserva.girado_por` siempre se asigna al usuario actual

### Al crear OrdenServicio

1. Marcar `ReservaDetalle.seleccionado=True` para cada detalle
2. Los detalles marcados no pueden seleccionarse nuevamente en Biblia Digital

### Al eliminar OrdenServicio o detalle

1. Restaurar `ReservaDetalle.seleccionado=False`
2. Permite re-seleccionar en futuras órdenes

### Cálculo de totales en Reserva

```python
subtotal_servicios = sum(numero_pax * servicio.precio)
subtotal_adicionales = sum(cantidad * adicional.precio)
total_no_contable = sum(adicionales donde contable=False)
total = subtotal_servicios + subtotal_adicionales - total_no_contable
```

## Optimizaciones

### Prefetch/Select Related

Todos los viewsets usan `select_related()` y `prefetch_related()` para optimizar consultas:

```python
queryset = Reserva.objects.select_related(
    'cliente', 'creado_por', 'girado_por'
).prefetch_related(
    'reservadetalle_set__servicio',
    'reservadetalle_set__recoger_en'
)
```

### Paginación

Configurado en settings.py:

- Tamaño de página: 10 items
- Filtros y ordenamiento disponibles en todos los endpoints

## Testing

```bash
# Ejecutar tests
python manage.py test

# Con cobertura
coverage run --source='.' manage.py test
coverage report
```
