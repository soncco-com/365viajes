<template>
  <q-page class="q-pa-md">
    <page-title title="Órdenes de Servicio" subtitle="Registro de órdenes de servicio asignadas" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.guia"
              label="Guía"
              endpoint="base/guias"
              option-label="nombre_completo"
            />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.chofer"
              label="Chofer"
              endpoint="base/choferes"
              option-label="nombre_completo"
            />
          </div>
          <div class="col-12 col-md-2 flex items-center">
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
      class="q-mt-md"
    >
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="visibility" color="primary" @click="viewOrden(props.row)">
            <q-tooltip>Ver detalles</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="delete" color="negative" @click="deleteOrden(props.row)">
            <q-tooltip>Eliminar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <q-dialog v-model="showDetailDialog" full-width>
      <q-card>
        <q-card-section>
          <div class="text-h6">Orden de Servicio - {{ selectedOrden?.fecha }}</div>
        </q-card-section>

        <q-card-section v-if="selectedOrden">
          <div class="row q-col-gutter-md">
            <div class="col-4">
              <div class="text-grey-7">Guía:</div>
              <div class="text-subtitle1">{{ selectedOrden.guia?.nombre_completo }}</div>
            </div>
            <div class="col-4">
              <div class="text-grey-7">Chofer:</div>
              <div class="text-subtitle1">{{ selectedOrden.chofer?.nombre_completo }}</div>
            </div>
            <div class="col-4">
              <div class="text-grey-7">Transporte:</div>
              <div class="text-subtitle1">
                {{ selectedOrden.transporte?.placa }} - {{ selectedOrden.transporte?.modelo }}
              </div>
            </div>
          </div>

          <q-separator class="q-my-md" />

          <div class="text-subtitle1 q-mb-md">Detalles de Reservas</div>
          <q-table
            :rows="selectedOrden.detalles || []"
            :columns="detalleColumns"
            row-key="id"
            flat
            bordered
          >
            <template v-slot:body-cell-servicio="props">
              <q-td :props="props">{{ props.row.servicio?.nombre }}</q-td>
            </template>
            <template v-slot:body-cell-lugar="props">
              <q-td :props="props">{{ props.row.lugar?.nombre }}</q-td>
            </template>
          </q-table>
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
const { notifySuccess, notifyError, confirm } = useNotify()

const ordenes = ref([])
const loading = ref(false)
const showDetailDialog = ref(false)
const selectedOrden = ref(null)
const filters = ref({ fecha: { from: null, to: null }, guia: null, chofer: null })

const columns = [
  { name: 'fecha', label: 'Fecha', field: 'fecha', align: 'left', sortable: true },
  { name: 'guia', label: 'Guía', field: (row) => row.guia?.nombre_completo, align: 'left' },
  { name: 'chofer', label: 'Chofer', field: (row) => row.chofer?.nombre_completo, align: 'left' },
  { name: 'transporte', label: 'Transporte', field: (row) => row.transporte?.placa, align: 'left' },
  {
    name: 'detalles',
    label: 'Servicios',
    field: (row) => row.detalles?.length || 0,
    align: 'center',
  },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const detalleColumns = [
  { name: 'reserva', label: 'Reserva', field: (row) => row.reserva?.numero, align: 'left' },
  { name: 'servicio', label: 'Servicio', field: 'servicio', align: 'left' },
  { name: 'lugar', label: 'Lugar', field: 'lugar', align: 'left' },
  { name: 'numero_pax', label: 'PAX', field: 'numero_pax', align: 'center' },
  { name: 'horario', label: 'Horario', field: 'horario', align: 'left' },
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

    if (filters.value.fecha.from && filters.value.fecha.to) {
      params.fecha__gte = filters.value.fecha.from
      params.fecha__lte = filters.value.fecha.to
    }
    if (filters.value.guia) {
      params.guia = filters.value.guia.id
    }
    if (filters.value.chofer) {
      params.chofer = filters.value.chofer.id
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
  selectedOrden.value = orden
  showDetailDialog.value = true
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
  filters.value.fecha = { from: today, to: today }
  loadOrdenes()
})
</script>
