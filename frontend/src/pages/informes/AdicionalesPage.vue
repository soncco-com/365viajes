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
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.adicional"
              label="Adicional"
              endpoint="base/adicionales"
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
      :rows="adicionales"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:body-cell-contable="props">
        <q-td :props="props">
          <q-badge :color="props.row.adicional?.contable ? 'positive' : 'warning'">
            {{ props.row.adicional?.contable ? 'Contable' : 'No Contable' }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-subtotal="props">
        <q-td :props="props">S/ {{ props.row.subtotal }}</q-td>
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

const adicionales = ref([])
const loading = ref(false)
const filters = ref({ fecha: { from: null, to: null }, adicional: null })

const columns = [
  {
    name: 'fecha',
    label: 'Fecha',
    field: (row) => row.reserva?.fecha,
    align: 'left',
    sortable: true,
  },
  { name: 'reserva', label: 'Reserva', field: (row) => row.reserva?.numero, align: 'left' },
  {
    name: 'cliente',
    label: 'Agencia',
    field: (row) => row.reserva?.cliente?.nombre_comercial,
    align: 'left',
  },
  { name: 'adicional', label: 'Adicional', field: (row) => row.adicional?.nombre, align: 'left' },
  { name: 'cantidad', label: 'Cant.', field: 'cantidad', align: 'center' },
  { name: 'precio', label: 'Precio Unit.', field: (row) => row.adicional?.precio, align: 'right' },
  { name: 'contable', label: 'Tipo', field: 'contable', align: 'center' },
  { name: 'subtotal', label: 'Subtotal', field: 'subtotal', align: 'right', sortable: true },
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
    (sum, a) => (a.adicional?.contable ? sum + parseFloat(a.subtotal || 0) : sum),
    0,
  )
})

const totalNoContable = computed(() => {
  return adicionales.value.reduce(
    (sum, a) => (!a.adicional?.contable ? sum + parseFloat(a.subtotal || 0) : sum),
    0,
  )
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
      params.reserva__fecha__gte = filters.value.fecha.from
      params.reserva__fecha__lte = filters.value.fecha.to
    }
    if (filters.value.adicional) {
      params.adicional = filters.value.adicional.id
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

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha = { from: today, to: today }
  loadReporte()
})
</script>
