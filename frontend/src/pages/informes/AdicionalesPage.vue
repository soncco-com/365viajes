<template>
  <q-page class="q-pa-md">
    <page-title
      title="Adicionales Vendidos"
      subtitle="Reporte de servicios adicionales contratados"
    />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas *" />
          </div>
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.adicional"
              label="Adicional *"
              endpoint="base/adicionales"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-2 flex items-center q-gutter-sm">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadReporte"
              :loading="loading"
            />
            <q-btn
              v-if="adicionales.length > 0"
              color="secondary"
              icon="print"
              flat
              round
              @click="imprimirPDF"
              :loading="loadingPDF"
            >
              <q-tooltip>Imprimir PDF</q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="adicionales"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No se encontraron adicionales vendidos"
      class="q-mt-md"
    >
      <template v-slot:body-cell-contable="props">
        <q-td :props="props">
          <q-badge :color="props.row.adicional_contable ? 'positive' : 'warning'">
            {{ props.row.adicional_contable ? 'Contable' : 'No Contable' }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-subtotal="props">
        <q-td :props="props">S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}</q-td>
      </template>
    </data-table>

    <q-card class="q-mt-md" v-if="adicionales.length > 0">
      <q-card-section>
        <div class="text-h6">Resumen</div>
        <div class="row q-mt-md">
          <div class="col-4">
            <div class="text-grey-7">Total Adicionales:</div>
            <div class="text-h5">{{ pagination.rowsNumber }}</div>
          </div>
          <div class="col-4">
            <div class="text-grey-7">Total Contable:</div>
            <div class="text-h5 text-positive">S/ {{ totalContable.toFixed(2) }}</div>
          </div>
          <div class="col-4">
            <div class="text-grey-7">Total No Contable:</div>
            <div class="text-h5 text-warning">S/ {{ totalNoContable.toFixed(2) }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Dialog para ver PDF -->
    <pdf-viewer v-model="showPdfDialog" :pdf-url="pdfUrl" title="Informe de Adicionales" />
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'
import PdfViewer from 'src/components/PdfViewer.vue'

const api = useApi()
const { notifyError } = useNotify()

const adicionales = ref([])
const loading = ref(false)
const loadingPDF = ref(false)
const showPdfDialog = ref(false)
const pdfUrl = ref('')
const filters = ref({ fecha: { desde: null, hasta: null }, adicional: null })

const columns = [
  {
    name: 'cuando',
    label: 'Fecha',
    field: 'cuando',
    align: 'left',
    sortable: true,
    format: (val) => {
      if (!val) return ''
      const [year, month, day] = val.split('-')
      return `${day}/${month}/${year}`
    },
  },
  { name: 'reserva', label: 'Reserva', field: 'reserva_id', align: 'left' },
  { name: 'pasajero', label: 'Pasajero', field: 'reserva_pasajero', align: 'left' },
  { name: 'adicional', label: 'Adicional', field: 'adicional_nombre', align: 'left' },
  { name: 'cantidad', label: 'Cant.', field: 'cantidad', align: 'center' },
  {
    name: 'precio',
    label: 'Precio Unit.',
    field: 'adicional_precio',
    align: 'right',
    format: (val) => `S/ ${parseFloat(val || 0).toFixed(2)}`,
  },
  { name: 'contable', label: 'Tipo', field: 'adicional_contable', align: 'center' },
  {
    name: 'subtotal',
    label: 'Subtotal',
    field: 'total',
    align: 'right',
    sortable: true,
    format: (val) => `S/ ${parseFloat(val || 0).toFixed(2)}`,
  },
]

const pagination = ref({
  sortBy: 'fecha',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const totalContable = computed(() => {
  return adicionales.value.reduce(
    (sum, a) => (a.adicional_contable ? sum + parseFloat(a.total || 0) : sum),
    0,
  )
})

const totalNoContable = computed(() => {
  return adicionales.value.reduce(
    (sum, a) => (!a.adicional_contable ? sum + parseFloat(a.total || 0) : sum),
    0,
  )
})

const loadReporte = async (props) => {
  // Validar filtros obligatorios
  if (!filters.value.fecha.desde || !filters.value.fecha.hasta || !filters.value.adicional) {
    notifyError('Debe seleccionar rango de fechas y adicional')
    return
  }

  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
      cuando__range: filters.value.fecha.range,
      adicional: filters.value.adicional?.id || filters.value.adicional,
    }

    const response = await api.get('reservas/reserva-adicionales/', { params })
    adicionales.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } catch {
    notifyError('Error al cargar reporte')
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadReporte(props)

const imprimirPDF = async () => {
  if (!filters.value.fecha.desde || !filters.value.fecha.hasta || !filters.value.adicional) {
    notifyError('Debe seleccionar rango de fechas y adicional')
    return
  }

  loadingPDF.value = true
  try {
    const params = {
      cuando__range: filters.value.fecha.range,
      adicional: filters.value.adicional?.id || filters.value.adicional,
    }

    const response = await api.get('reservas/reserva-adicionales/pdf_adicionales/', {
      params,
      responseType: 'blob',
    })

    const blob = new Blob([response.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
    showPdfDialog.value = true
  } catch (error) {
    console.error(error)
    notifyError('Error al generar PDF')
  } finally {
    loadingPDF.value = false
  }
}

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha = { desde: today, hasta: today }
})
</script>
