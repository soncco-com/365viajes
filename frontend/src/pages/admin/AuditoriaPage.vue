<template>
  <q-page class="q-pa-md">
    <page-title title="Auditoría" subtitle="Registro de trazabilidad de operaciones" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.usuario"
              label="Usuario"
              endpoint="base/usuarios"
              option-label="username"
            />
          </div>
          <div class="col-12 col-md-3">
            <q-select
              v-model="filters.accion"
              :options="accionOptions"
              label="Acción"
              filled
              emit-value
              map-options
              clearable
            />
          </div>
          <div class="col-12 col-md-2 flex items-center">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadAuditoria"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="logs"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      :searchable="false"
      no-data-label="No se encontraron registros de auditoría"
      class="q-mt-md"
    >
      <template v-slot:body-cell-accion="props">
        <q-td :props="props">
          <q-badge :color="getAccionColor(props.row.accion)">
            {{ props.row.accion }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="visibility" color="primary" @click="viewDetalle(props.row)">
            <q-tooltip>Ver detalles</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <q-dialog v-model="showDetailDialog" full-width>
      <q-card>
        <q-card-section>
          <div class="text-h6">Detalle de Auditoría</div>
        </q-card-section>

        <q-card-section v-if="selectedRegistro">
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-3">
              <div class="text-grey-7">Fecha/Hora:</div>
              <div class="text-subtitle1">{{ formatDateTime(selectedRegistro.fecha) }}</div>
            </div>
            <div class="col-3">
              <div class="text-grey-7">Usuario:</div>
              <div class="text-subtitle1">{{ selectedRegistro.usuario?.username }}</div>
            </div>
            <div class="col-3">
              <div class="text-grey-7">Acción:</div>
              <div>
                <q-badge :color="getAccionColor(selectedRegistro.accion)">{{
                  selectedRegistro.accion
                }}</q-badge>
              </div>
            </div>
            <div class="col-3">
              <div class="text-grey-7">Modelo:</div>
              <div class="text-subtitle1">{{ selectedRegistro.modelo }}</div>
            </div>
          </div>

          <q-separator class="q-my-md" />

          <div v-if="selectedRegistro.objeto_id">
            <div class="text-grey-7">ID Objeto:</div>
            <div class="text-subtitle1 q-mb-md">{{ selectedRegistro.objeto_id }}</div>
          </div>

          <div v-if="selectedRegistro.datos_anteriores">
            <div class="text-subtitle1 q-mb-sm">Datos Anteriores:</div>
            <q-card flat bordered class="q-mb-md">
              <q-card-section>
                <pre class="text-caption">{{ formatJson(selectedRegistro.datos_anteriores) }}</pre>
              </q-card-section>
            </q-card>
          </div>

          <div v-if="selectedRegistro.datos_nuevos">
            <div class="text-subtitle1 q-mb-sm">Datos Nuevos:</div>
            <q-card flat bordered>
              <q-card-section>
                <pre class="text-caption">{{ formatJson(selectedRegistro.datos_nuevos) }}</pre>
              </q-card-section>
            </q-card>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn label="Cerrar" color="primary" flat @click="showDetailDialog = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const api = useApi()
const { notifyError } = useNotify()

const registros = ref([])
const loading = ref(false)
const showDetailDialog = ref(false)
const selectedRegistro = ref(null)
const filters = ref({ fecha: { from: null, to: null }, usuario: null, accion: null })
const accionOptions = [
  { label: 'Crear', value: 'CREATE' },
  { label: 'Actualizar', value: 'UPDATE' },
  { label: 'Eliminar', value: 'DELETE' },
]

const columns = [
  {
    name: 'fecha',
    label: 'Fecha/Hora',
    field: 'fecha',
    align: 'left',
    sortable: true,
    format: formatDateTime,
  },
  { name: 'usuario', label: 'Usuario', field: (row) => row.usuario?.username, align: 'left' },
  { name: 'accion', label: 'Acción', field: 'accion', align: 'center', sortable: true },
  { name: 'modelo', label: 'Modelo', field: 'modelo', align: 'left' },
  { name: 'objeto_id', label: 'ID Objeto', field: 'objeto_id', align: 'left' },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'fecha',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

function formatDateTime(datetime) {
  if (!datetime) return ''
  return new Date(datetime).toLocaleString('es-PE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatJson(data) {
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

function getAccionColor(accion) {
  switch (accion) {
    case 'CREATE':
      return 'positive'
    case 'UPDATE':
      return 'info'
    case 'DELETE':
      return 'negative'
    default:
      return 'grey'
  }
}

const loadAuditoria = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.fecha.from && filters.value.fecha.to) {
      params.fecha__gte = filters.value.fecha.from
      params.fecha__lte = filters.value.fecha.to
    }
    if (filters.value.usuario) {
      params.usuario = filters.value.usuario?.id || filters.value.usuario
    }
    if (filters.value.accion) {
      params.accion = filters.value.accion
    }

    const response = await api.get('base/auditoria/', { params })
    registros.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } catch {
    notifyError('Error al cargar auditoría')
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadAuditoria(props)

const viewDetalle = (registro) => {
  selectedRegistro.value = registro
  showDetailDialog.value = true
}

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha = { from: today, to: today }
  loadAuditoria()
})
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}
</style>
