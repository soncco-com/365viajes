<template>
  <q-page class="q-pa-md">
    <page-title title="Reservas" subtitle="Gestión de reservas de tours y servicios" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-2">
            <q-input v-model="filters.id" label="ID" outlined dense clearable type="number" />
          </div>
          <div class="col-12 col-md-3">
            <q-input v-model="filters.pasajero" label="Pasajero" outlined dense clearable />
          </div>
          <div class="col-12 col-md-3">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
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
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.tipo_pago"
              label="Tipo de Pago"
              :options="tipoPagoOptions"
              emit-value
              map-options
              clearable
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.girado_por"
              label="Girado por"
              endpoint="base/usuarios"
              option-label="first_name"
              option-value="id"
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-input
              v-model="filters.numero_rango"
              label="Num. Recibo"
              placeholder="Ej: 1-5"
              outlined
              dense
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.tipo_documento"
              label="Tipo de Documento"
              :options="tipoDocumentoOptions"
              emit-value
              map-options
              clearable
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-2 flex items-end">
            <q-btn color="grey" icon="clear" label="Limpiar" @click="clearFilters" flat />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Totales -->
    <q-card flat bordered class="q-mt-md" v-if="totales.cantidad">
      <q-card-section horizontal class="q-gutter-md items-center q-pa-sm">
        <div class="q-px-md">
          <div class="text-caption text-grey-7">Registros</div>
          <div class="text-subtitle1 text-weight-bold">{{ totales.cantidad }}</div>
        </div>
        <q-separator vertical />
        <div class="q-px-md">
          <div class="text-caption text-grey-7">Total</div>
          <div class="text-subtitle1 text-weight-bold text-primary">
            S/ {{ parseFloat(totales.total || 0).toFixed(2) }}
          </div>
        </div>
        <q-separator vertical />
        <div class="q-px-md">
          <div class="text-caption text-grey-7">Total Neto</div>
          <div class="text-subtitle1 text-weight-bold text-positive">
            S/ {{ parseFloat(totales.total_neto || 0).toFixed(2) }}
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
      :show-totals="true"
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

      <template v-slot:totals>
        <q-tr class="text-weight-bold bg-grey-2">
          <q-td colspan="5" class="text-right">Totales:</q-td>
          <q-td class="text-right">S/ {{ parseFloat(totales.total || 0).toFixed(2) }}</q-td>
          <q-td :colspan="columns.length - 6"></q-td>
        </q-tr>
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
import { ref, onMounted, watch } from 'vue'
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
const totales = ref({ total: 0, total_nocontable: 0, total_neto: 0, cantidad: 0 })

const filters = ref({
  id: null,
  pasajero: '',
  fecha: { desde: '', hasta: '', range: null },
  cliente_id: null,
  estado: null,
  tipo_pago: null,
  tipo_documento: null,
  girado_por: null,
  numero_rango: '',
})

const estadoOptions = [
  { label: 'Pagado', value: '0' },
  { label: 'Deuda', value: '1' },
]

const tipoPagoOptions = [
  { label: 'Efectivo', value: '0' },
  { label: 'Depósito', value: '1' },
  { label: 'Otro', value: '2' },
]

const tipoDocumentoOptions = [
  { label: 'Boleta', value: '0' },
  { label: 'Factura', value: '1' },
  { label: 'Otros', value: '2' },
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
    name: 'cliente_nombre',
    label: 'Agencia',
    field: 'cliente_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'fecha',
    label: 'Fecha reserva',
    field: 'fecha',
    align: 'left',
    sortable: true,
    format: (val) => {
      if (!val) return '-'
      const [y, m, d] = val.split('-')
      return new Date(y, m - 1, d).toLocaleDateString('es-ES')
    },
  },
  {
    name: 'fecha_primer_servicio',
    label: 'Fecha primer servicio',
    field: 'fecha_primer_servicio',
    align: 'left',
    sortable: false,
    format: (val) => {
      if (!val) return '-'
      const [y, m, d] = val.split('-')
      return new Date(y, m - 1, d).toLocaleDateString('es-ES')
    },
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
    name: 'girado_por_nombre',
    label: 'Girado por',
    field: 'girado_por_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'tipo_pago_display',
    label: 'Pago',
    field: 'tipo_pago_display',
    align: 'center',
    sortable: false,
  },
  {
    name: 'numero',
    label: 'Num. Recibo',
    field: 'numero',
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
      page_size: rowsPerPage === 0 ? 99999 : rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.id) {
      params.id = filters.value.id
    }

    if (filters.value.pasajero) {
      params.search = filters.value.pasajero
    }

    // Añadir filtros
    if (filters.value.fecha.range) {
      params.fecha__range = filters.value.fecha.range
    } else if (filters.value.fecha.desde) {
      params.fecha__gte = filters.value.fecha.desde
    } else if (filters.value.fecha.hasta) {
      params.fecha__lte = filters.value.fecha.hasta
    }

    if (filters.value.cliente_id) {
      params.cliente = filters.value.cliente_id?.id || filters.value.cliente_id
    }

    if (filters.value.estado !== null && filters.value.estado !== undefined) {
      params.estado = filters.value.estado
    }

    if (filters.value.tipo_pago !== null && filters.value.tipo_pago !== undefined) {
      params.tipo_pago = filters.value.tipo_pago
    }

    if (filters.value.tipo_documento !== null && filters.value.tipo_documento !== undefined) {
      params.tipo_documento = filters.value.tipo_documento
    }

    if (filters.value.girado_por) {
      params.girado_por = filters.value.girado_por?.id || filters.value.girado_por
    }

    if (filters.value.numero_rango) {
      params.numero_rango = filters.value.numero_rango
    }

    const response = await api.get('reservas/reservas/', { params })

    reservas.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count

    // Cargar totales con los mismos filtros
    loadTotales(params)
  } catch (error) {
    notifyError('Error al cargar las reservas')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadTotales = async (filterParams) => {
  try {
    // Solo enviar filtros, no paginación
    const totalesFilters = { ...filterParams }
    delete totalesFilters.page
    delete totalesFilters.page_size
    delete totalesFilters.ordering
    const response = await api.get('reservas/reservas/totales/', { params: totalesFilters })
    totales.value = response.data
  } catch (error) {
    console.error('Error al cargar totales', error)
  }
}

const onRequest = (props) => {
  loadReservas(props)
}

const clearFilters = () => {
  filters.value = {
    id: null,
    pasajero: '',
    fecha: { desde: '', hasta: '', range: null },
    cliente_id: null,
    estado: null,
    tipo_pago: null,
    tipo_documento: null,
    girado_por: null,
    numero_rango: '',
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

let debounceTimer = null
watch(
  filters,
  () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      loadReservas()
    }, 400)
  },
  { deep: true },
)
</script>

<style scoped>
/* Estilos personalizados si son necesarios */
</style>
