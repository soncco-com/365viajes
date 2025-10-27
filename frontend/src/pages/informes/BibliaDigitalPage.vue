<template>
  <q-page class="q-pa-md">
    <page-title title="Biblia Digital" subtitle="Informe de reservas por fecha y servicio" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <date-range-picker
              v-model:desde="filters.fecha_desde"
              v-model:hasta="filters.fecha_hasta"
              label="Rango de fechas"
            />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.servicio_id"
              label="Servicio"
              endpoint="base/servicios"
              option-label="nombre"
              option-value="id"
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.seleccionado"
              label="Selección"
              :options="seleccionadoOptions"
              emit-value
              map-options
              clearable
              filled
            />
          </div>
          <div class="col-12 col-md-3 flex items-end">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadDetalles"
              class="q-mr-sm"
            />
            <q-btn color="secondary" icon="clear" label="Limpiar" @click="clearFilters" flat />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla de detalles -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row items-center q-mb-md">
          <div class="text-h6 col">Detalles de Servicios</div>
          <q-btn
            v-if="selectedDetalles.length > 0"
            color="primary"
            icon="assignment"
            :label="`Crear Orden (${selectedDetalles.length})`"
            @click="createOrdenServicio"
          />
        </div>

        <q-table
          :rows="detalles"
          :columns="columns"
          :loading="loading"
          :pagination="pagination"
          @request="onRequest"
          row-key="id"
          selection="multiple"
          v-model:selected="selectedDetalles"
          flat
          bordered
        >
          <template v-slot:body-cell-fecha="props">
            <q-td :props="props">
              {{ new Date(props.row.reserva_fecha).toLocaleDateString('es-ES') }}
            </q-td>
          </template>

          <template v-slot:body-cell-seleccionado="props">
            <q-td :props="props">
              <q-badge :color="props.row.seleccionado ? 'positive' : 'grey'">
                {{ props.row.seleccionado ? 'Seleccionado' : 'Pendiente' }}
              </q-badge>
            </q-td>
          </template>

          <template v-slot:body-cell-subtotal="props">
            <q-td :props="props">
              <span class="text-weight-bold">
                S/ {{ parseFloat(props.row.subtotal).toFixed(2) }}
              </span>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Totales -->
    <q-card flat bordered class="q-mt-md bg-grey-2" v-if="detalles.length > 0">
      <q-card-section>
        <div class="row q-col-gutter-md text-center">
          <div class="col-12 col-md-3">
            <div class="text-caption text-grey-7">Total Registros</div>
            <div class="text-h5 text-primary">{{ pagination.rowsNumber }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-caption text-grey-7">Total PAX</div>
            <div class="text-h5 text-info">{{ totalPax }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-caption text-grey-7">Total Monto</div>
            <div class="text-h5 text-positive">S/ {{ totalMonto.toFixed(2) }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-caption text-grey-7">Seleccionados</div>
            <div class="text-h5 text-warning">{{ selectedDetalles.length }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Dialog para crear orden de servicio -->
    <q-dialog v-model="showOrdenDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Crear Orden de Servicio</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveOrdenServicio" class="q-gutter-md">
            <autocomplete-input
              v-model="ordenForm.guia"
              label="Guía"
              endpoint="base/guias"
              option-label="nombre_completo"
              option-value="id"
              :rules="[(val) => !!val || 'El guía es requerido']"
              required
            />

            <autocomplete-input
              v-model="ordenForm.chofer"
              label="Chofer"
              endpoint="base/choferes"
              option-label="nombre_completo"
              option-value="id"
            />

            <autocomplete-input
              v-model="ordenForm.transporte"
              label="Transporte"
              endpoint="base/transportes"
              option-label="placa"
              option-value="id"
            />

            <q-input
              v-model="ordenForm.observaciones"
              label="Observaciones"
              filled
              type="textarea"
              rows="3"
            />

            <div class="row q-gutter-sm justify-end">
              <q-btn label="Cancelar" color="grey" flat @click="showOrdenDialog = false" />
              <q-btn
                label="Crear Orden"
                type="submit"
                color="primary"
                :loading="savingOrden"
                :disable="savingOrden"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'

const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const detalles = ref([])
const selectedDetalles = ref([])
const loading = ref(false)
const showOrdenDialog = ref(false)
const savingOrden = ref(false)

const filters = ref({
  fecha_desde: '',
  fecha_hasta: '',
  servicio_id: null,
  seleccionado: null,
})

const seleccionadoOptions = [
  { label: 'Seleccionados', value: true },
  { label: 'Pendientes', value: false },
]

const ordenForm = ref({
  guia: null,
  chofer: null,
  transporte: null,
  observaciones: '',
})

const columns = [
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'reserva_fecha',
    align: 'left',
    sortable: true,
  },
  {
    name: 'servicio_nombre',
    label: 'Servicio',
    field: 'servicio_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'lugar_nombre',
    label: 'Hotel',
    field: 'lugar_nombre',
    align: 'left',
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
  },
  {
    name: 'numero_pax',
    label: 'PAX',
    field: 'numero_pax',
    align: 'center',
  },
  {
    name: 'subtotal',
    label: 'Subtotal',
    field: 'subtotal',
    align: 'right',
  },
  {
    name: 'seleccionado',
    label: 'Estado',
    field: 'seleccionado',
    align: 'center',
    sortable: true,
  },
]

const pagination = ref({
  sortBy: 'reserva_fecha',
  descending: false,
  page: 1,
  rowsPerPage: 20,
  rowsNumber: 0,
})

const totalPax = computed(() => {
  return detalles.value.reduce((sum, d) => sum + d.numero_pax, 0)
})

const totalMonto = computed(() => {
  return detalles.value.reduce((sum, d) => sum + parseFloat(d.subtotal), 0)
})

const loadDetalles = async (props) => {
  loading.value = true

  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value

    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.fecha_desde && filters.value.fecha_hasta) {
      params.fecha__range = `${filters.value.fecha_desde},${filters.value.fecha_hasta}`
    } else if (filters.value.fecha_desde) {
      params.fecha__gte = filters.value.fecha_desde
    } else if (filters.value.fecha_hasta) {
      params.fecha__lte = filters.value.fecha_hasta
    }

    if (filters.value.servicio_id) {
      params.servicio = filters.value.servicio_id
    }

    if (filters.value.seleccionado !== null && filters.value.seleccionado !== undefined) {
      params.seleccionado = filters.value.seleccionado
    }

    const response = await api.get('reservas/biblia-digital/', { params })

    detalles.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count

    // Limpiar selección
    selectedDetalles.value = []
  } catch (error) {
    notifyError('Error al cargar los detalles')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadDetalles(props)
}

const clearFilters = () => {
  filters.value = {
    fecha_desde: '',
    fecha_hasta: '',
    servicio_id: null,
    seleccionado: null,
  }
  loadDetalles()
}

const createOrdenServicio = () => {
  // Filtrar solo los que NO están seleccionados
  const pendientes = selectedDetalles.value.filter((d) => !d.seleccionado)

  if (pendientes.length === 0) {
    notifyError('Todos los detalles seleccionados ya tienen orden asignada')
    return
  }

  if (pendientes.length !== selectedDetalles.value.length) {
    notifyError('Algunos detalles ya tienen orden asignada. Se crearán solo para los pendientes.')
    selectedDetalles.value = pendientes
  }

  ordenForm.value = {
    guia: null,
    chofer: null,
    transporte: null,
    observaciones: '',
  }
  showOrdenDialog.value = true
}

const saveOrdenServicio = async () => {
  savingOrden.value = true

  try {
    const payload = {
      guia: ordenForm.value.guia,
      chofer: ordenForm.value.chofer,
      transporte: ordenForm.value.transporte,
      observaciones: ordenForm.value.observaciones,
      detalles: selectedDetalles.value.map((d) => d.id),
    }

    await api.post('reservas/ordenes-servicio/', payload)
    notifySuccess('Orden de servicio creada correctamente')

    showOrdenDialog.value = false
    selectedDetalles.value = []
    loadDetalles()
  } catch (error) {
    notifyError('Error al crear la orden de servicio')
    console.error(error)
  } finally {
    savingOrden.value = false
  }
}

onMounted(() => {
  // Cargar detalles de hoy por defecto
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha_desde = today
  filters.value.fecha_hasta = today
  loadDetalles()
})
</script>
