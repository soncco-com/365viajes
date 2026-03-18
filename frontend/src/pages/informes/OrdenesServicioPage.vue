<template>
  <q-page class="q-pa-md">
    <page-title title="Órdenes de Servicio" subtitle="Registro de órdenes de servicio asignadas" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-3">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-2">
            <autocomplete-input
              v-model="filters.servicio"
              label="Servicio"
              endpoint="base/servicios"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.idioma"
              :options="idiomaOptions"
              label="Idioma"
              outlined
              dense
              clearable
              emit-value
              map-options
            />
          </div>
          <div class="col-12 col-md-1">
            <autocomplete-input
              v-model="filters.guia"
              label="Guía"
              endpoint="base/guias"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-1">
            <autocomplete-input
              v-model="filters.chofer"
              label="Chofer"
              endpoint="base/choferes"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-2">
            <autocomplete-input
              v-model="filters.responsable"
              label="Responsable"
              endpoint="base/responsables"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-1 flex items-center">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadOrdenes"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="ordenes"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No se encontraron órdenes de servicio"
      class="q-mt-md"
    >
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="visibility" color="primary" @click="viewOrden(props.row)">
            <q-tooltip>Ver detalles</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="print" color="secondary" @click="printOrden(props.row)">
            <q-tooltip>Imprimir PDF</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="delete" color="negative" @click="deleteOrden(props.row)">
            <q-tooltip>Eliminar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <!-- Visor de PDF -->
    <pdf-viewer v-model="showPdfDialog" :pdf-url="pdfUrl" />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog } from 'quasar'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'
import PdfViewer from 'src/components/PdfViewer.vue'

const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const ordenes = ref([])
const loading = ref(false)
const showPdfDialog = ref(false)
const pdfUrl = ref('')
const filters = ref({
  fecha: { desde: null, hasta: null },
  servicio: null,
  idioma: null,
  guia: null,
  chofer: null,
  responsable: null,
})

const idiomaOptions = [
  { label: 'Español', value: 'es' },
  { label: 'Inglés', value: 'en' },
  { label: 'Bilingüe', value: 'xx' },
]

const columns = [
  {
    name: 'id',
    label: 'ID',
    field: 'id',
    align: 'left',
    sortable: true,
  },
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'fecha',
    align: 'left',
    sortable: true,
    format: (val) => {
      if (!val) return ''
      const [year, month, day] = val.split('-')
      return `${day}/${month}/${year}`
    },
  },
  {
    name: 'servicio',
    label: 'Servicio',
    field: 'servicio_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'idioma',
    label: 'Idioma',
    field: 'idioma_display',
    align: 'center',
  },
  {
    name: 'guia',
    label: 'Guía',
    field: 'guia_nombre',
    align: 'left',
  },
  {
    name: 'chofer',
    label: 'Chofer',
    field: 'chofer_nombre',
    align: 'left',
  },
  {
    name: 'responsable',
    label: 'Responsable',
    field: 'responsable_nombre',
    align: 'left',
  },
  {
    name: 'cant_servicios',
    label: 'Cant. Servicios',
    field: (row) => row.detalles?.length || 0,
    align: 'center',
  },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'fecha',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadOrdenes = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.fecha.desde && filters.value.fecha.hasta) {
      params.fecha__gte = filters.value.fecha.desde
      params.fecha__lte = filters.value.fecha.hasta
    }
    if (filters.value.servicio) {
      params.servicio = filters.value.servicio?.id || filters.value.servicio
    }
    if (filters.value.idioma) {
      params.idioma = filters.value.idioma
    }
    if (filters.value.guia) {
      params.guia = filters.value.guia?.id || filters.value.guia
    }
    if (filters.value.chofer) {
      params.chofer = filters.value.chofer?.id || filters.value.chofer
    }
    if (filters.value.responsable) {
      params.responsable = filters.value.responsable?.id || filters.value.responsable
    }

    const response = await api.get('reservas/ordenes-servicio/', { params })
    ordenes.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } catch {
    notifyError('Error al cargar órdenes')
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadOrdenes(props)

const viewOrden = (orden) => {
  router.push(`/informes/ordenes-servicio/${orden.id}`)
}

const printOrden = async (orden) => {
  try {
    // Preguntar si desea incluir información de agencia
    const incluirAgencia = await new Promise((resolve) => {
      Dialog.create({
        title: 'Imprimir Orden de Servicio',
        message: '¿Desea incluir información de agencias en el PDF?',
        cancel: {
          label: 'Cancelar',
          flat: true,
        },
        ok: {
          label: 'Imprimir',
          color: 'primary',
        },
        options: {
          type: 'radio',
          model: 'sin_agencia',
          items: [
            {
              label: 'Imprimir sin información de agencias',
              value: 'sin_agencia',
              color: 'secondary',
            },
            {
              label: 'Imprimir con información de agencias',
              value: 'con_agencia',
              color: 'primary',
            },
          ],
        },
      })
        .onOk((selected) => {
          resolve(selected === 'con_agencia')
        })
        .onCancel(() => {
          resolve(null)
        })
    })

    if (incluirAgencia === null) return // Usuario canceló

    const response = await api.get(`reservas/ordenes-servicio/${orden.id}/pdf/`, {
      params: {
        mostrar_agencia: incluirAgencia ? 'true' : 'false',
      },
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
    showPdfDialog.value = true
  } catch {
    notifyError('Error al generar el PDF')
  }
}

const deleteOrden = async (orden) => {
  if (
    !(await confirm(
      '¿Eliminar esta orden de servicio? Los detalles de reserva quedarán pendientes de asignación.',
      'Confirmar eliminación',
    ))
  )
    return
  try {
    await api.delete(`reservas/ordenes-servicio/${orden.id}/`)
    notifySuccess('Orden eliminada')
    loadOrdenes()
  } catch {
    notifyError('Error al eliminar')
  }
}

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha = { desde: today, hasta: today }
  loadOrdenes()
})
</script>
