# Copilot Instructions for 365 Viajes

## System Overview

Wholesale travel booking system for managing tour reservations from multiple travel agencies. Creates itineraries combining services (tours) with pickup locations and optional add-ons.

## Architecture

### Backend (Django REST Framework)

- **Apps**: `base/` (core entities), `reservas/` (booking logic)
- **Database**: MySQL + Redis caching
- **Auth**: `rest_framework_simplejwt` with 30-day tokens
- **PDF**: WeasyPrint with reusable templates, common header with logo
- **Audit**: Track all create/edit/delete operations

### Frontend (Quasar/Vue 3)

- **Router**: Hash mode, permission-based navigation
- **UI**: Top non-fixed menu with dropdowns, non-fixed footer
- **PDF Viewer**: pdf.js in dialogs (zoom, print, download)
- **Components**: Reusable autocompletes, date pickers, tables
- **Cache**: Avoid redundant API calls

## Critical Domain Logic

### Reserva Workflow

1. `Reserva` (master) has `cliente` (agency), `pasajero`, `total`, `estado` (Pagado/Deuda)
2. `ReservaDetalle` (multiple) links to `Servicio`, `Lugar` (hotel), calculates subtotal = `numero_pax * servicio.precio`
3. `ReservaAdicionalDetalle` (multiple) for extras, subtotal = `cantidad * adicional.precio`
4. **Contable field**: If `adicional.contable=False`, subtract from total (shown as "Total no Contable")
5. **Estado logic**: When `estado='0'` (Pagado), auto-assign `numero` (max+1), set `girado_por=request.user`, `girado_cuando=now()`

### OrdenServicio (Service Orders)

Created from "Biblia digital" report by selecting `ReservaDetalle` rows:

- Assigns `Guia` and `Chofer` to service
- Sets `ReservaDetalle.seleccionado=True` (prevent re-selection, show different color)
- Deletion restores `seleccionado=False`

## Key Patterns

### Backend Conventions

- **Endpoint naming**: Use `-` or `_` consistently (choose one)
- **Optimization**: Use `prefetch_related()` and `select_related()`
- **Caching**: Redis for expensive queries, invalidate on model changes
- **Filtering**: Support `fecha__gte`, `fecha__lte`, `fecha__range` for date ranges
- **Active filters**: Filter by `activo=True` in autocompletes
- **PDF**: Centralized, modular generation with shared header template

### Frontend Conventions

- **Date Range Filters**: Send `fecha__gte=desde`, `fecha__lte=hasta`, or `fecha__range=desde,hasta`
- **Master-Detail Forms**: Dynamic add/remove rows for `ReservaDetalle` and `ReservaAdicionalDetalle`
- **Autocompletes**: Filter `activo=True`, allow inline creation (e.g., new `Cliente` in dialog)
- **Tables**: Always paginated, sortable, filterable with totals row
- **Permissions**: Hide menu items/pages based on Django groups (Administrador vs all users)
- **Responsive Design**: Single color palette, modern/simple UI

## Business Rules

### Reserva Calculations

```javascript
// Frontend calculation
subtotal_servicios = sum(numero_pax * servicio.precio)
subtotal_adicionales = sum(cantidad * adicional.precio)
total_no_contable = sum(adicionales where contable=false)
total = subtotal_servicios + subtotal_adicionales - total_no_contable
```

### Permission-Based Features

- **All users**: Reservas, most reports, view own Gastos, Agencias, Hoteles
- **Administrador only**: Usuarios, Adicionales, Guías, Horarios, Servicios, Transportes, Auditoría, Rendición de ventas

## Development Commands

### Backend

```bash
cd backend
docker-compose up  # MySQL + Redis + Django
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Frontend

```bash
cd frontend
npm install
quasar dev    # Port 9000 (or configured port)
quasar build
```

## File References

- `backend/base/models.py` - Cliente, Servicio, Lugar, Adicional, Guia, Chofer, Horario
- `backend/reservas/models.py` - Reserva, ReservaDetalle, ReservaAdicionalDetalle, OrdenServicio, Gasto
- `backend/tres65viajes/settings.py` - Environment config via `python-decouple`
- `.github/instructions.md` - Complete feature specifications and page descriptions
