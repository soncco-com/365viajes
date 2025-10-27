# Frontend - Documentación Técnica

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── AutocompleteInput.vue
│   │   ├── DataTable.vue
│   │   ├── DatePicker.vue
│   │   ├── DateRangePicker.vue
│   │   ├── PageTitle.vue
│   │   └── PdfViewer.vue
│   ├── composables/         # Lógica reutilizable
│   │   ├── useApi.js
│   │   ├── useAuth.js
│   │   └── useNotify.js
│   ├── layouts/             # Layouts de la aplicación
│   │   └── MainLayout.vue
│   ├── pages/               # Páginas/vistas
│   │   ├── auth/
│   │   ├── reservas/
│   │   ├── informes/
│   │   ├── gastos/
│   │   ├── admin/
│   │   └── auditoria/
│   └── router/              # Configuración de rutas
│       ├── index.js
│       └── routes.js
└── .env                     # Variables de entorno
```

## Composables

### useAuth.js

Manejo centralizado de autenticación JWT.

**Funciones:**

- `login(username, password)` - Iniciar sesión
- `logout()` - Cerrar sesión
- `refreshAccessToken()` - Renovar token automáticamente
- `fetchUserData()` - Obtener datos del usuario
- `hasPermission(permission)` - Verificar permisos

**Estado:**

- `isAuthenticated` - Boolean, si está autenticado
- `currentUser` - Objeto con datos del usuario
- `isAdmin` - Boolean, si es administrador
- `accessToken` - JWT access token
- `refreshToken` - JWT refresh token

**Uso:**

```javascript
import { useAuth } from "src/composables/useAuth";

const { login, logout, isAuthenticated, isAdmin } = useAuth();

// Login
const result = await login("usuario", "password");
if (result.success) {
  // Login exitoso
}

// Logout
logout();

// Verificar autenticación
if (isAuthenticated.value) {
  // Usuario autenticado
}
```

### useApi.js

Cliente HTTP centralizado con interceptores automáticos.

**Características:**

- Interceptor automático de JWT en headers
- Refresh automático de tokens expirados
- Manejo centralizado de errores
- Notificaciones automáticas de errores

**Funciones:**

- `get(url, config)` - GET request
- `post(url, data, config)` - POST request
- `put(url, data, config)` - PUT request
- `patch(url, data, config)` - PATCH request
- `delete(url, config)` - DELETE request
- `download(url, filename)` - Descargar archivo
- `getPdf(url)` - Obtener PDF como blob

**Uso:**

```javascript
import { useApi } from "src/composables/useApi";

const api = useApi();

// GET
const { data, success } = await api.get("/base/clientes/");

// POST
const { data, success } = await api.post("/reservas/reservas/", reservaData);

// DELETE
const { success } = await api.delete(`/reservas/reservas/${id}/`);

// Descargar PDF
await api.download("/reservas/reservas/1/pdf/", "reserva.pdf");

// Obtener PDF para visualizar
const { data: pdfBlob } = await api.getPdf("/reservas/reservas/1/pdf/");
```

### useNotify.js

Sistema centralizado de notificaciones.

**Funciones:**

- `success(message, options)` - Notificación de éxito
- `error(message, options)` - Notificación de error
- `warning(message, options)` - Notificación de advertencia
- `info(message, options)` - Notificación informativa
- `confirm(options)` - Diálogo de confirmación
- `alert(message, title)` - Diálogo de alerta
- `showLoading(message)` - Mostrar loading
- `hideLoading()` - Ocultar loading

**Uso:**

```javascript
import { useNotify } from "src/composables/useNotify";

const notify = useNotify();

// Notificaciones
notify.success("Guardado exitosamente");
notify.error("Error al guardar");
notify.warning("Verifique los datos");
notify.info("Información importante");

// Confirmación
const confirmed = await notify.confirm({
  title: "Eliminar",
  message: "¿Está seguro de eliminar este registro?",
  okLabel: "Eliminar",
  cancelLabel: "Cancelar",
});

if (confirmed) {
  // Eliminar
}

// Loading
notify.showLoading("Guardando...");
// ... operación async
notify.hideLoading();
```

## Componentes Reutilizables

### DataTable.vue

Tabla de datos con paginación, filtros y acciones.

**Props:**

- `rows` - Array de datos
- `columns` - Definición de columnas
- `loading` - Estado de carga
- `searchable` - Mostrar buscador (default: true)
- `createButton` - Mostrar botón crear (default: false)
- `createLabel` - Texto del botón crear
- `showTotals` - Mostrar fila de totales

**Events:**

- `@request` - Paginación/ordenamiento
- `@create` - Click en botón crear
- `@edit` - Click en editar
- `@delete` - Click en eliminar

**Slots:**

- `filters` - Filtros personalizados
- `actions` - Acciones personalizadas por fila
- `body-cell-*` - Personalizar celdas
- `totals` - Fila de totales

**Uso:**

```vue
<DataTable
  :rows="reservas"
  :columns="columns"
  :loading="loading"
  searchable
  createButton
  createLabel="Nueva Reserva"
  @create="crearReserva"
  @edit="editarReserva"
  @delete="eliminarReserva"
>
  <template #filters>
    <DateRangePicker v-model="filtros.fecha" />
  </template>

  <template #body-cell-total="props">
    <q-td :props="props">
      S/ {{ props.row.total }}
    </q-td>
  </template>
</DataTable>
```

### AutocompleteInput.vue

Select con búsqueda y autocompletado.

**Props:**

- `modelValue` - Valor seleccionado
- `label` - Etiqueta
- `options` - Array de opciones
- `optionLabel` - Campo a mostrar (default: 'nombre')
- `loading` - Estado de carga
- `clearable` - Permitir limpiar
- `allowCreate` - Mostrar botón crear

**Events:**

- `@update:modelValue` - Cambio de valor
- `@create` - Click en botón crear
- `@filter` - Filtro cambiado

**Uso:**

```vue
<AutocompleteInput
  v-model="form.cliente_id"
  label="Agencia"
  :options="clientes"
  option-label="nombre"
  allowCreate
  @create="crearCliente"
/>
```

### DatePicker.vue

Selector de fecha con formato español.

**Props:**

- `modelValue` - Fecha (YYYY-MM-DD)
- `label` - Etiqueta
- `mask` - Formato interno (default: YYYY-MM-DD)
- `displayMask` - Formato mostrado (default: DD/MM/YYYY)

**Uso:**

```vue
<DatePicker v-model="form.fecha" label="Fecha de Reserva" />
```

### DateRangePicker.vue

Selector de rango de fechas.

**Props:**

- `modelValue` - Objeto `{ desde, hasta }`

**Uso:**

```vue
<DateRangePicker v-model="filtros.fecha" />

<!-- Acceder a las fechas -->
{{ filtros.fecha.desde }}
{{ filtros.fecha.hasta }}
```

### PageTitle.vue

Título de página consistente.

**Props:**

- `title` - Título principal
- `subtitle` - Subtítulo opcional
- `icon` - Ícono opcional
- `iconColor` - Color del ícono
- `separator` - Mostrar separador

**Uso:**

```vue
<PageTitle
  title="Reservas"
  subtitle="Gestión de reservas del sistema"
  icon="book"
  iconColor="primary"
/>
```

### PdfViewer.vue

Visualizador de PDFs con zoom, impresión y descarga.

**Props:**

- `modelValue` - Mostrar/ocultar (v-model)
- `pdfUrl` - URL del PDF
- `pdfBlob` - Blob del PDF
- `title` - Título del diálogo
- `filename` - Nombre para descarga

**Funcionalidades:**

- Zoom in/out
- Impresión
- Descarga
- Vista de múltiples páginas

**Uso:**

```vue
<template>
  <q-btn @click="verPdf">Ver PDF</q-btn>

  <PdfViewer
    v-model="showPdf"
    :pdfBlob="pdfBlob"
    title="Reserva #123"
    filename="reserva-123.pdf"
  />
</template>

<script setup>
import { ref } from "vue";
import { useApi } from "src/composables/useApi";

const showPdf = ref(false);
const pdfBlob = ref(null);
const api = useApi();

const verPdf = async () => {
  const { data } = await api.getPdf("/reservas/reservas/123/pdf/");
  pdfBlob.value = data;
  showPdf.value = true;
};
</script>
```

## Router y Navegación

### Guards de Navegación

**Autenticación:**

- Rutas con `meta: { requiresAuth: true }` requieren login
- Rutas con `meta: { requiresAdmin: true }` requieren rol Administrador
- Login redirige a página solicitada después de autenticar

**Implementación:**

```javascript
// En routes.js
{
  path: '/admin/usuarios',
  component: () => import('pages/admin/UsuariosPage.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
}
```

### Filtros de Fecha para Backend

Al enviar filtros de fecha al backend, seguir este patrón:

```javascript
// Función helper
const buildDateFilter = (dateRange) => {
  if (!dateRange.desde && !dateRange.hasta) return {};

  if (dateRange.desde && dateRange.hasta) {
    return { fecha__range: `${dateRange.desde},${dateRange.hasta}` };
  } else if (dateRange.desde) {
    return { fecha__gte: dateRange.desde };
  } else if (dateRange.hasta) {
    return { fecha__lte: dateRange.hasta };
  }
};

// Uso
const params = {
  ...buildDateFilter(filtros.fecha),
  cliente: filtros.cliente_id,
};

await api.get("/reservas/reservas/", { params });
```

## Variables de Entorno

Archivo `.env`:

```env
VITE_API_URL=http://localhost:8000/api
```

Acceso en código:

```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

## Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Desarrollo
quasar dev

# Build para producción
quasar build

# Lint
npm run lint

# Format
npm run format
```

## Convenciones de Código

### Nombres de Archivos

- Componentes: PascalCase (e.g., `DataTable.vue`)
- Composables: camelCase (e.g., `useAuth.js`)
- Páginas: PascalCase con sufijo Page (e.g., `ReservasListPage.vue`)

### Estructura de Componentes

```vue
<template>
  <!-- Template -->
</template>

<script setup>
// Imports
import { ref } from "vue";

// Props
const props = defineProps({});

// Emits
const emit = defineEmits([]);

// Refs y reactivos
const data = ref(null);

// Composables
const api = useApi();

// Funciones
const cargarDatos = async () => {};

// Lifecycle hooks
onMounted(() => {});
</script>

<style lang="scss" scoped>
/* Estilos */
</style>
```

### Manejo de Formularios

```javascript
const form = ref({
  campo1: "",
  campo2: null,
});

const rules = {
  campo1: [(val) => !!val || "Campo requerido"],
};

const guardar = async () => {
  const { success } = await api.post("/endpoint/", form.value);
  if (success) {
    notify.success("Guardado");
  }
};
```

## Próximos Pasos

1. ✅ Estructura base y composables
2. ✅ Componentes reutilizables
3. ✅ Router con guards
4. ⏳ MainLayout con menú
5. ⏳ Página de Login
6. ⏳ Módulo de Reservas
7. ⏳ Módulo de Informes
8. ⏳ Módulo de Administración
9. ⏳ Módulo de Auditoría
10. ⏳ Estilos y tema personalizado
