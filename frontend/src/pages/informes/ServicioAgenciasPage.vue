<template>
  <q-page class="q-pa-md">
    <page-title
      title="Informe de Servicios y Adicionales por Agencia"
      subtitle="Detalle de servicios y adicionales - Estado de deudas"
    />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas *" />
          </div>
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.cliente"
              label="Agencia *"
              endpoint="base/clientes"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.estado"
              :options="estadoOptions"
              label="Estado"
              outlined
              dense
              clearable
              emit-value
              map-options
            />
          </div>
          <div class="col-12 col-md-2 flex items-center q-gutter-sm">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadReporte"
              :loading="loading"
              :disable="!canSearch"
            />
            <q-btn
              v-if="hasSearched && (servicios.length > 0 || adicionales.length > 0)"
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

    <!-- Tabla de Servicios -->
    <q-card class="q-mt-md" v-if="servicios.length > 0">
      <q-card-section>
        <div class="text-h6 q-mb-md">Servicios</div>
        <q-table
          :rows="servicios"
          :columns="serviciosColumns"
          :loading="loading"
          row-key="id"
          flat
          bordered
          dense
          :pagination="{ rowsPerPage: 0 }"
          hide-pagination
          no-data-label="No hay servicios para mostrar"
        >
          <template v-slot:body-cell-fecha="props">
            <q-td :props="props">{{ formatDate(props.row.cuando) }}</q-td>
          </template>

          <template v-slot:body-cell-subtotal="props">
            <q-td :props="props">S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}</q-td>
          </template>

          <template v-slot:body-cell-estado="props">
            <q-td :props="props">
              <q-badge :color="props.row.estado === '0' ? 'positive' : 'warning'">
                {{ props.row.estado === '0' ? 'Pagado' : 'Deuda' }}
              </q-badge>
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                round
                icon="visibility"
                color="primary"
                @click="verReserva(props.row.reserva_id)"
              >
                <q-tooltip>Ver reserva</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-6">
            <div class="text-grey-7">Total Pagado (Servicios):</div>
            <div class="text-h6 text-positive">S/ {{ totalServiciosPagados.toFixed(2) }}</div>
          </div>
          <div class="col-6">
            <div class="text-grey-7">Total Deuda (Servicios):</div>
            <div class="text-h6 text-warning">S/ {{ totalServiciosDeuda.toFixed(2) }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla de Adicionales -->
    <q-card class="q-mt-md" v-if="adicionales.length > 0">
      <q-card-section>
        <div class="text-h6 q-mb-md">Adicionales</div>
        <q-table
          :rows="adicionales"
          :columns="adicionalesColumns"
          :loading="loading"
          row-key="id"
          flat
          bordered
          dense
          :pagination="{ rowsPerPage: 0 }"
          hide-pagination
          no-data-label="No hay adicionales para mostrar"
        >
          <template v-slot:body-cell-fecha="props">
            <q-td :props="props">{{ formatDate(props.row.cuando) }}</q-td>
          </template>

          <template v-slot:body-cell-subtotal="props">
            <q-td :props="props">S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}</q-td>
          </template>

          <template v-slot:body-cell-estado="props">
            <q-td :props="props">
              <q-badge :color="props.row.estado === '0' ? 'positive' : 'warning'">
                {{ props.row.estado === '0' ? 'Pagado' : 'Deuda' }}
              </q-badge>
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                round
                icon="visibility"
                color="primary"
                @click="verReserva(props.row.reserva_id)"
              >
                <q-tooltip>Ver reserva</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-6">
            <div class="text-grey-7">Total Pagado (Adicionales):</div>
            <div class="text-h6 text-positive">S/ {{ totalAdicionalesPagados.toFixed(2) }}</div>
          </div>
          <div class="col-6">
            <div class="text-grey-7">Total Deuda (Adicionales):</div>
            <div class="text-h6 text-warning">S/ {{ totalAdicionalesDeuda.toFixed(2) }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Resumen General -->
    <q-card class="q-mt-md" v-if="servicios.length > 0 || adicionales.length > 0">
      <q-card-section class="bg-grey-2">
        <div class="text-h6 q-mb-md">Resumen General</div>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <q-card flat bordered class="bg-positive text-white">
              <q-card-section>
                <div class="text-subtitle2">Total Pagado</div>
                <div class="text-h4">S/ {{ totalGeneralPagado.toFixed(2) }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-md-6">
            <q-card flat bordered class="bg-warning text-white">
              <q-card-section>
                <div class="text-subtitle2">Total Deuda</div>
                <div class="text-h4">S/ {{ totalGeneralDeuda.toFixed(2) }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <div
      v-if="!loading && servicios.length === 0 && adicionales.length === 0 && hasSearched"
      class="q-mt-md text-center text-grey"
    >
      <q-icon name="search_off" size="64px" />
      <div class="text-h6 q-mt-md">No se encontraron resultados</div>
      <div class="text-subtitle2">Intenta con otros filtros</div>
    </div>

    <!-- Dialog para ver PDF -->
    <pdf-viewer
      v-model="showPdfDialog"
      :pdf-url="pdfUrl"
      title="Informe de Servicios por Agencia"
    />
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'
import PdfViewer from 'src/components/PdfViewer.vue'
import { formatDateOnly as formatDate } from 'src/utils/date'

const router = useRouter()
const api = useApi()
const { notifyError } = useNotify()

const servicios = ref([])
const adicionales = ref([])
const loading = ref(false)
const loadingPDF = ref(false)
const hasSearched = ref(false)
const showPdfDialog = ref(false)
const pdfUrl = ref('')
const filters = ref({
  fecha: { desde: null, hasta: null },
  cliente: null,
  estado: null,
})

const estadoOptions = [
  { label: 'Pagado', value: '0' },
  { label: 'Deuda', value: '1' },
]

const serviciosColumns = [
  {
    name: 'reserva_id',
    label: 'ID',
    field: 'reserva_id',
    align: 'center',
    sortable: true,
  },
  {
    name: 'fecha',
    label: 'Fecha Salida',
    field: 'cuando',
    align: 'left',
    sortable: true,
    format: formatDate,
  },
  {
    name: 'servicio',
    label: 'Servicio',
    field: 'servicio_nombre',
    align: 'left',
  },
  {
    name: 'pax',
    label: 'Nro PAX',
    field: 'numero_pax',
    align: 'center',
  },
  {
    name: 'pasajero',
    label: 'Pasajero',
    field: 'pasajero',
    align: 'left',
  },
  {
    name: 'subtotal',
    label: 'Subtotal',
    field: 'total',
    align: 'right',
    sortable: true,
    format: (val) => `S/ ${parseFloat(val || 0).toFixed(2)}`,
  },
  {
    name: 'lugar',
    label: 'Lugar Recojo',
    field: 'lugar_nombre',
    align: 'left',
  },
  {
    name: 'idioma',
    label: 'Idioma',
    field: 'idioma_display',
    align: 'center',
  },
  {
    name: 'estado',
    label: 'Estado',
    field: 'estado',
    align: 'center',
    format: (val) => (val === '0' ? 'Pagado' : 'Deuda'),
  },
  {
    name: 'actions',
    label: 'Acción',
    field: 'actions',
    align: 'center',
  },
]

const adicionalesColumns = [
  {
    name: 'reserva_id',
    label: 'ID',
    field: 'reserva_id',
    align: 'center',
    sortable: true,
  },
  {
    name: 'cantidad',
    label: 'Cantidad',
    field: 'cantidad',
    align: 'center',
  },
  {
    name: 'adicional',
    label: 'Adicional',
    field: 'adicional_nombre',
    align: 'left',
  },
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'cuando',
    align: 'left',
    sortable: true,
    format: formatDate,
  },
  {
    name: 'pasajero',
    label: 'Pasajero',
    field: 'pasajero',
    align: 'left',
  },
  {
    name: 'subtotal',
    label: 'Subtotal',
    field: 'total',
    align: 'right',
    sortable: true,
    format: (val) => `S/ ${parseFloat(val || 0).toFixed(2)}`,
  },
  {
    name: 'estado',
    label: 'Estado',
    field: 'estado',
    align: 'center',
    format: (val) => (val === '0' ? 'Pagado' : 'Deuda'),
  },
  {
    name: 'actions',
    label: 'Acción',
    field: 'actions',
    align: 'center',
  },
]

const canSearch = computed(() => {
  return filters.value.fecha.desde && filters.value.fecha.hasta && filters.value.cliente
})

const totalServiciosPagados = computed(() => {
  return servicios.value
    .filter((s) => s.estado === '0')
    .reduce((sum, s) => sum + parseFloat(s.total || 0), 0)
})

const totalServiciosDeuda = computed(() => {
  return servicios.value
    .filter((s) => s.estado === '1')
    .reduce((sum, s) => sum + parseFloat(s.total || 0), 0)
})

const totalAdicionalesPagados = computed(() => {
  return adicionales.value
    .filter((a) => a.estado === '0')
    .reduce((sum, a) => sum + parseFloat(a.total || 0), 0)
})

const totalAdicionalesDeuda = computed(() => {
  return adicionales.value
    .filter((a) => a.estado === '1')
    .reduce((sum, a) => sum + parseFloat(a.total || 0), 0)
})

const totalGeneralPagado = computed(() => {
  return totalServiciosPagados.value + totalAdicionalesPagados.value
})

const totalGeneralDeuda = computed(() => {
  return totalServiciosDeuda.value + totalAdicionalesDeuda.value
})

const loadReporte = async () => {
  if (!canSearch.value) {
    notifyError('Debe seleccionar rango de fechas y agencia')
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    const params = {
      cuando__range: filters.value.fecha.range,
      pertenece_a__cliente: filters.value.cliente?.id || filters.value.cliente,
    }

    if (filters.value.estado !== null && filters.value.estado !== undefined) {
      params['pertenece_a__estado'] = filters.value.estado
    }

    // Cargar servicios y adicionales en paralelo
    const [serviciosResponse, adicionalesResponse] = await Promise.all([
      api.get('reservas/reserva-detalles/', { params }),
      api.get('reservas/reserva-adicionales/', { params }),
    ])

    // Procesar servicios - usar campos del serializer
    servicios.value = (serviciosResponse.data.results || serviciosResponse.data).map((detalle) => ({
      ...detalle,
      estado: detalle.reserva_estado,
      pasajero: detalle.reserva_pasajero,
    }))

    // Procesar adicionales - usar campos del serializer
    adicionales.value = (adicionalesResponse.data.results || adicionalesResponse.data).map(
      (adicional) => ({
        ...adicional,
        estado: adicional.reserva_estado,
        pasajero: adicional.reserva_pasajero,
      }),
    )

    if (servicios.value.length === 0 && adicionales.value.length === 0) {
      notifyError('No se encontraron registros')
    }
  } catch (error) {
    console.error(error)
    notifyError('Error al cargar reporte')
  } finally {
    loading.value = false
  }
}

const verReserva = (reservaId) => {
  router.push(`/reservas/${reservaId}/editar`)
}

const imprimirPDF = async () => {
  if (!canSearch.value) return

  loadingPDF.value = true
  try {
    const params = {
      cuando__range: filters.value.fecha.range,
      pertenece_a__cliente: filters.value.cliente?.id || filters.value.cliente,
    }

    if (filters.value.estado !== null && filters.value.estado !== undefined) {
      params['pertenece_a__estado'] = filters.value.estado
    }

    const response = await api.get('reservas/reserva-detalles/pdf_servicio_agencias/', {
      params,
      responseType: 'blob',
    })

    // Crear URL del blob y mostrar en visor
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
</script>
