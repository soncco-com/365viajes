# 365 Viajes - Sistema de Reservas

Sistema integral de gestión de reservas para agencias de turismo mayorista. Permite administrar reservas, servicios turísticos, órdenes de servicio, gastos y generación de reportes.

## 🏗 Arquitectura

- **Backend**: Django REST Framework + MySQL + Redis
- **Frontend**: Quasar (Vue 3) + Vite
- **PDF**: WeasyPrint con templates HTML
- **Autenticación**: JWT con tokens de 30 días
- **Auditoría**: Sistema automático de registro de cambios

## 🚀 Inicio Rápido

### Backend

```bash
cd backend

# Opción 1: Con Docker (Recomendado)
docker-compose up

# Opción 2: Sin Docker
pip install -r requirements.txt
python manage.py migrate
python manage.py init_data  # Datos de prueba
python manage.py createsuperuser
python manage.py runserver
```

El backend estará disponible en `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
quasar dev
```

El frontend estará disponible en `http://localhost:9000`

## 📦 Servicios con Docker

El archivo `docker-compose.yml` incluye:

- **db**: MySQL 8
- **redis**: Redis para caché
- **web**: Django en puerto 8000
- **pma**: PhpMyAdmin en puerto 8800

## 📚 Documentación

- [Backend - Documentación Técnica](docs/backend.md)
- [Frontend - Guía de Desarrollo](docs/frontend.md) _(por crear)_
- [Instrucciones Completas](.github/instructions.md)
- [Guía para AI Agents](.github/copilot-instructions.md)

## 🔑 Características Principales

### Gestión de Reservas

- Creación de reservas con múltiples servicios y adicionales
- Cálculo automático de totales y totales no contables
- Estados: Pagado / Deuda
- Generación automática de números de recibo

### Órdenes de Servicio

- Asignación de guías y choferes
- Gestión de servicios desde "Biblia Digital"
- Prevención de doble asignación de servicios

### Informes y Reportes

- Servicio por agencias
- Biblia digital (planning diario)
- Informe de adicionales
- Rendición de ventas
- Todos exportables a PDF

### Auditoría

- Registro automático de todos los cambios
- Captura de usuario, IP y datos modificados
- Accesible solo para administradores

### Sistema de Permisos

- **Todos los usuarios**: Reservas, informes básicos, gastos propios
- **Administradores**: Acceso completo + auditoría + configuración

## 🛠 Tecnologías

### Backend

- Django 5.2.7
- Django REST Framework 3.16.1
- MySQL Client 2.2.7
- Redis 7.0.0
- WeasyPrint 63.1 (PDFs)
- django-filter 24.3
- django-cors-headers 4.6.0

### Frontend

- Quasar 2.16.0
- Vue 3.5.22
- Vite
- Axios (para APIs)
- PDF.js (visualización de PDFs)

## 📝 Estructura del Proyecto

```
365viajes/
├── backend/
│   ├── base/              # App core (modelos base)
│   ├── reservas/          # App de reservas
│   ├── tres65viajes/      # Configuración Django
│   ├── docker-compose.yml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes reusables
│   │   ├── pages/         # Páginas de la app
│   │   ├── layouts/       # Layouts
│   │   └── router/        # Configuración de rutas
│   └── quasar.config.js
├── docs/                  # Documentación
└── .github/
    ├── instructions.md           # Especificaciones completas
    └── copilot-instructions.md   # Guía para AI
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en `backend/`:

```env
SECRET_KEY=tu-secret-key-aqui
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

## 📊 API Endpoints Principales

### Autenticación

- `POST /api/token/` - Obtener token JWT
- `POST /api/token/refresh/` - Renovar token

### Módulos

- `/api/base/*` - Clientes, servicios, lugares, guías, choferes, etc.
- `/api/reservas/*` - Reservas, órdenes de servicio, gastos

Ver documentación completa en [docs/backend.md](docs/backend.md)

## 🧪 Testing

```bash
cd backend
python manage.py test
```

## 👥 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y confidencial.

## 🤝 Soporte

Para soporte y consultas, contactar al equipo de desarrollo.

---

**Estado del Proyecto**: 🚧 En Desarrollo

**Progreso Backend**: ✅ Completado (modelos, APIs, auditoría, PDFs)
**Progreso Frontend**: 🔨 En progreso (estructura base)
