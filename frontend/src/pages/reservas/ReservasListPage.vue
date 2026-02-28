<template>
  <q-page class="q-pa-md">
    <page-title title="Reservas" subtitle="Gestión de reservas de tours y servicios" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-3">
            <date-range-picker
              v-model:desde="filters.fecha_desde"
              v-model:hasta="filters.fecha_hasta"
              label="Rango de fechas"
            />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.cliente_id"
              label="Agencia"
              endpoint="base/clientes"
              option-label="nombre"
              option-value="id"
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.estado"
              label="Estado"
              :options="estadoOptions"
              emit-value
              map-options
              clearable
              fill-input
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-4 flex items-end">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadReservas"
              class="q-mr-sm"
            />
            <q-btn color="secondary" icon="clear" label="Limpiar" @click="clearFilters" flat />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla de reservas -->
    <data-table
      :rows="reservas"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No se encontraron reservas"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          label="Nueva Reserva"
          @click="$router.push('/reservas/crear')"
        />
      </template>

      <template v-slot:body-cell-numero="props">
        <q-td :props="props">
          <q-badge v-if="props.row.numero" color="primary">
            {{ props.row.numero }}
          </q-badge>
          <span v-else class="text-grey">Sin número</span>
        </q-td>
      </template>

      <template v-slot:body-cell-estado="props">
        <q-td :props="props">
          <q-badge :color="props.row.estado === '0' ? 'positive' : 'warning'">
            {{ props.row.estado === '0' ? 'Pagado' : 'Deuda' }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-total="props">
        <q-td :props="props">
          <span class="text-weight-bold">S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}</span>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="edit" color="primary" @click="editReserva(props.row)">
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="history"
            color="info"
            @click="viewHistorial(props.row)"
            v-if="isAdmin"
          >
            <q-tooltip>Ver historial de cambios</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="picture_as_pdf"
            color="negative"
            @click="downloadPdf(props.row)"
          >
            <q-tooltip>Descargar PDF</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            @click="deleteReserva(props.row)"
            v-if="props.row.estado !== '0'"
          >
            <q-tooltip>Eliminar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <!-- Dialog para ver PDF -->
    <pdf-viewer v-model="showPdfDialog" :pdf-url="pdfUrl" title="Reserva" />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useAuth } from 'src/composables/useAuth'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import PdfViewer from 'src/components/PdfViewer.vue'

const router = useRouter()
const api = useApi()
const { isAdmin } = useAuth()
const { notifySuccess, notifyError, confirm } = useNotify()

const reservas = ref([])
const loading = ref(false)
const showPdfDialog = ref(false)
const pdfUrl = ref('')

const filters = ref({
  fecha_desde: '',
  fecha_hasta: '',
  cliente_id: null,
  estado: null,
})

const estadoOptions = [
  { label: 'Pagado', value: '0' },
  { label: 'Deuda', value: '1' },
]

const columns = [
  {
    name: 'id',
    label: 'ID',
    field: 'id',
    align: 'center',
    sortable: true,
  },
  {
    name: 'numero',
    label: 'Número',
    field: 'numero',
    align: 'center',
    sortable: true,
  },
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'fecha',
    align: 'left',
    sortable: true,
    format: (val) => new Date(val).toLocaleDateString('es-ES'),
  },
  {
    name: 'cliente_nombre',
    label: 'Agencia',
    field: 'cliente_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'pasajero',
    label: 'Pasajero',
    field: 'pasajero',
    align: 'left',
    sortable: true,
  },
  {
    name: 'total',
    label: 'Total',
    field: 'total',
    align: 'right',
    sortable: true,
  },
  {
    name: 'estado',
    label: 'Estado',
    field: 'estado',
    align: 'center',
    sortable: true,
  },
  {
    name: 'actions',
    label: 'Acciones',
    field: 'actions',
    align: 'center',
  },
]

const pagination = ref({
  sortBy: 'id',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadReservas = async (props) => {
  loading.value = true

  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value

    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    // Añadir filtros
    if (filters.value.fecha_desde && filters.value.fecha_hasta) {
      params.fecha__range = `${filters.value.fecha_desde},${filters.value.fecha_hasta}`
    } else if (filters.value.fecha_desde) {
      params.fecha__gte = filters.value.fecha_desde
    } else if (filters.value.fecha_hasta) {
      params.fecha__lte = filters.value.fecha_hasta
    }

    if (filters.value.cliente_id) {
      params.cliente = filters.value.cliente_id?.id || filters.value.cliente_id
    }

    if (filters.value.estado !== null && filters.value.estado !== undefined) {
      params.estado = filters.value.estado
    }

    const response = await api.get('reservas/reservas/', { params })

    reservas.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar las reservas')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadReservas(props)
}

const clearFilters = () => {
  filters.value = {
    fecha_desde: '',
    fecha_hasta: '',
    cliente_id: null,
    estado: null,
  }
  loadReservas()
}

const editReserva = (reserva) => {
  router.push(`/reservas/${reserva.id}/editar`)
}

const viewHistorial = (reserva) => {
  router.push(`/reservas/${reserva.id}/historial`)
}

const downloadPdf = async (reserva) => {
  try {
    const response = await api.get(`reservas/reservas/${reserva.id}/pdf/`, {
      responseType: 'blob',
    })

    // Crear URL del blob
    const blob = new Blob([response.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
    showPdfDialog.value = true
  } catch (error) {
    notifyError('Error al generar el PDF')
    console.error(error)
  }
}

const deleteReserva = async (reserva) => {
  const confirmed = await confirm(
    '¿Está seguro de eliminar esta reserva?',
    'Esta acción no se puede deshacer. Se eliminarán también todos los servicios y adicionales asociados.',
  )

  if (!confirmed) return

  try {
    await api.delete(`reservas/reservas/${reserva.id}/`)
    notifySuccess('Reserva eliminada correctamente')
    loadReservas()
  } catch (error) {
    // Manejar error específico de reservas con órdenes de servicio
    if (error.response?.data?.error) {
      notifyError(error.response.data.error)
    } else {
      notifyError('Error al eliminar la reserva')
    }
    console.error(error)
  }
}

onMounted(() => {
  loadReservas()
})
</script>

<style scoped>
/* Estilos personalizados si son necesarios */
</style>
