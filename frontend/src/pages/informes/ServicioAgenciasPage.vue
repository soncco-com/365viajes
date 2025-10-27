<template>
  <q-page class="q-pa-md">
    <page-title
      title="Servicios por Agencia"
      subtitle="Detalle de servicios contratados por cada agencia"
    />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.cliente"
              label="Agencia"
              endpoint="base/clientes"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-2 flex items-center">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadReporte"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="reservas"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:body-cell-total="props">
        <q-td :props="props">S/ {{ props.row.total }}</q-td>
      </template>
    </data-table>

    <q-card class="q-mt-md" v-if="reservas.length > 0">
      <q-card-section>
        <div class="text-h6">Resumen</div>
        <div class="row q-mt-md">
          <div class="col-6">
            <div class="text-grey-7">Total Reservas:</div>
            <div class="text-h5">{{ pagination.rowsNumber }}</div>
          </div>
          <div class="col-6">
            <div class="text-grey-7">Total General:</div>
            <div class="text-h5 text-positive">S/ {{ totalGeneral.toFixed(2) }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>
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

const api = useApi()
const { notifyError } = useNotify()

const reservas = ref([])
const loading = ref(false)
const filters = ref({ fecha: { from: null, to: null }, cliente: null })

const columns = [
  { name: 'numero', label: 'N°', field: 'numero', align: 'left', sortable: true },
  { name: 'fecha', label: 'Fecha', field: 'fecha', align: 'left', sortable: true },
  {
    name: 'cliente',
    label: 'Agencia',
    field: (row) => row.cliente?.nombre_comercial,
    align: 'left',
  },
  { name: 'pasajero', label: 'Pasajero', field: 'pasajero', align: 'left' },
  {
    name: 'servicios',
    label: 'Servicios',
    field: (row) => row.detalles?.length || 0,
    align: 'center',
  },
  {
    name: 'adicionales',
    label: 'Adicionales',
    field: (row) => row.adicionales?.length || 0,
    align: 'center',
  },
  { name: 'total', label: 'Total', field: 'total', align: 'right', sortable: true },
]

const pagination = ref({
  sortBy: 'fecha',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const totalGeneral = computed(() => {
  return reservas.value.reduce((sum, r) => sum + parseFloat(r.total || 0), 0)
})

const loadReporte = async (props) => {
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
    if (filters.value.cliente) {
      params.cliente = filters.value.cliente.id
    }

    const response = await api.get('reservas/reservas/', { params })
    reservas.value = response.data.results
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

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha = { from: today, to: today }
  loadReporte()
})
</script>
