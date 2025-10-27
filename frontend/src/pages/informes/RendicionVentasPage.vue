<template>
  <q-page class="q-pa-md">
    <page-title
      title="Rendición de Ventas"
      subtitle="Informe administrativo de ventas por período"
    />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-4">
            <q-select
              v-model="filters.estado"
              :options="estadoOptions"
              label="Estado"
              emit-value
              map-options
              clearable
              fill-input
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-2 flex items-center">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadRendicion"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-card class="q-mt-md" v-if="resumen">
      <q-card-section>
        <div class="text-h6 q-mb-md">Resumen General</div>
        <div class="row q-col-gutter-md">
          <div class="col-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-grey-7 text-caption">Total Reservas</div>
                <div class="text-h5 text-primary">{{ resumen.total_reservas }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-grey-7 text-caption">Monto Total</div>
                <div class="text-h5 text-positive">S/ {{ resumen.monto_total.toFixed(2) }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-grey-7 text-caption">Pagadas</div>
                <div class="text-h5 text-positive">{{ resumen.pagadas }}</div>
                <div class="text-caption">S/ {{ resumen.monto_pagadas.toFixed(2) }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-3">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-grey-7 text-caption">Con Deuda</div>
                <div class="text-h5 text-warning">{{ resumen.con_deuda }}</div>
                <div class="text-caption">S/ {{ resumen.monto_deuda.toFixed(2) }}</div>
              </q-card-section>
            </q-card>
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
      <template v-slot:body-cell-estado="props">
        <q-td :props="props">
          <q-badge :color="props.row.estado === '0' ? 'positive' : 'warning'">
            {{ props.row.estado === '0' ? 'Pagado' : 'Deuda' }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-total="props">
        <q-td :props="props">S/ {{ props.row.total }}</q-td>
      </template>

      <template v-slot:body-cell-girado_por="props">
        <q-td :props="props">
          <div v-if="props.row.girado_por">
            {{ props.row.girado_por.username }}
            <div class="text-caption text-grey-7">
              {{ formatDateTime(props.row.girado_cuando) }}
            </div>
          </div>
        </q-td>
      </template>
    </data-table>

    <div class="q-mt-md row justify-end">
      <q-btn
        color="primary"
        icon="download"
        label="Exportar PDF"
        @click="exportPdf"
        :loading="exporting"
      />
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'

const api = useApi()
const { notifyError } = useNotify()

const reservas = ref([])
const loading = ref(false)
const exporting = ref(false)
const filters = ref({ fecha: { from: null, to: null }, estado: null })
const estadoOptions = [
  { label: 'Pagado', value: '0' },
  { label: 'Deuda', value: '1' },
]

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
  { name: 'estado', label: 'Estado', field: 'estado', align: 'center', sortable: true },
  { name: 'total', label: 'Total', field: 'total', align: 'right', sortable: true },
  { name: 'girado_por', label: 'Girado por', field: 'girado_por', align: 'left' },
]

const pagination = ref({
  sortBy: 'fecha',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const resumen = computed(() => {
  if (reservas.value.length === 0) return null

  const pagadas = reservas.value.filter((r) => r.estado === '0')
  const conDeuda = reservas.value.filter((r) => r.estado === '1')

  return {
    total_reservas: pagination.value.rowsNumber,
    monto_total: reservas.value.reduce((sum, r) => sum + parseFloat(r.total || 0), 0),
    pagadas: pagadas.length,
    monto_pagadas: pagadas.reduce((sum, r) => sum + parseFloat(r.total || 0), 0),
    con_deuda: conDeuda.length,
    monto_deuda: conDeuda.reduce((sum, r) => sum + parseFloat(r.total || 0), 0),
  }
})

const formatDateTime = (datetime) => {
  if (!datetime) return ''
  return new Date(datetime).toLocaleString('es-PE')
}

const loadRendicion = async (props) => {
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
    if (filters.value.estado !== null) {
      params.estado = filters.value.estado
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
    notifyError('Error al cargar rendición')
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadRendicion(props)

const exportPdf = async () => {
  exporting.value = true
  try {
    const params = {}
    if (filters.value.fecha.from && filters.value.fecha.to) {
      params.fecha__gte = filters.value.fecha.from
      params.fecha__lte = filters.value.fecha.to
    }
    if (filters.value.estado !== null) {
      params.estado = filters.value.estado
    }

    const response = await api.get('reservas/rendicion-pdf/', { params, responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `rendicion_ventas_${new Date().toISOString().split('T')[0]}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch {
    notifyError('Error al exportar PDF')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  const firstDay = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
    .toISOString()
    .split('T')[0]
  filters.value.fecha = { from: firstDay, to: today }
  loadRendicion()
})
</script>
