<template>
  <q-page class="q-pa-md">
    <page-title title="Rendición de Ventas" subtitle="Informe de cobros realizados por reserva" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.usuario"
              label="Usuario *"
              endpoint="base/usuarios/"
              option-label="username"
            />
          </div>
          <div class="col-12 col-md-4">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas *" required />
          </div>
          <div class="col-12 col-md-3">
            <autocomplete-input
              v-model="filters.agencia"
              label="Agencia"
              endpoint="base/clientes/"
              option-label="nombre"
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.tipo_pago"
              :options="tipoPagoOptions"
              label="Tipo de Pago"
              emit-value
              map-options
              clearable
              outlined
              dense
            />
          </div>
        </div>
        <div class="row q-mt-md">
          <div class="col-12 flex justify-end">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadRendicion"
              :loading="loading"
              :disable="!canSearch"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      v-if="reservas.length > 0"
      :rows="reservas"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No se encontraron cobros para los filtros seleccionados"
      class="q-mt-md"
    >
      <template v-slot:body-cell-subtotal="props">
        <q-td :props="props" class="text-right">S/ {{ props.row.total }}</q-td>
      </template>

      <template v-slot:bottom-row>
        <q-tr class="bg-grey-2 text-weight-bold">
          <q-td colspan="7" class="text-right">TOTAL:</q-td>
          <q-td class="text-right">S/ {{ totalGeneral.toFixed(2) }}</q-td>
        </q-tr>
      </template>
    </data-table>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
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
const filters = ref({
  usuario: null,
  fecha: { desde: null, hasta: null },
  agencia: null,
  tipo_pago: null,
})

const tipoPagoOptions = [
  { label: 'Efectivo', value: '0' },
  { label: 'Depósito', value: '1' },
  { label: 'Otro', value: '2' },
]

const columns = [
  { name: 'id', label: 'ID Reserva', field: 'id', align: 'left', sortable: true },
  {
    name: 'cliente',
    label: 'Agencia',
    field: 'cliente_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'fecha_primer_servicio',
    label: 'Fecha 1er Servicio',
    field: 'fecha_primer_servicio',
    align: 'center',
    sortable: true,
    format: (val) => {
      if (!val) return '-'
      const [year, month, day] = val.split('-')
      return `${day}/${month}/${year}`
    },
  },
  {
    name: 'girado_cuando',
    label: 'Fecha Girado',
    field: 'girado_cuando',
    align: 'center',
    sortable: true,
    format: (val) => {
      if (!val) return '-'
      return new Date(val).toLocaleDateString('es-PE')
    },
  },
  { name: 'pasajero', label: 'Pasajeros', field: 'pasajero', align: 'left' },
  {
    name: 'tipo_documento',
    label: 'Comprobante',
    field: 'tipo_documento_display',
    align: 'center',
  },
  {
    name: 'tipo_pago',
    label: 'Tipo Pago',
    field: 'tipo_pago_display',
    align: 'center',
  },
  { name: 'subtotal', label: 'Subtotal', field: 'total', align: 'right', sortable: true },
]

const pagination = ref({
  sortBy: 'girado_cuando',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const canSearch = computed(() => {
  return (
    filters.value.usuario !== null &&
    filters.value.fecha.desde !== null &&
    filters.value.fecha.hasta !== null
  )
})

const totalGeneral = computed(() => {
  return reservas.value.reduce((sum, r) => sum + parseFloat(r.total || 0), 0)
})

const loadRendicion = async (props) => {
  if (!canSearch.value) return

  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
      estado: '0', // Solo reservas pagadas (con cobro)
    }

    // Filtros obligatorios
    params.girado_por = filters.value.usuario?.id || filters.value.usuario

    // Asegurar que las fechas estén en formato correcto
    if (filters.value.fecha.desde) {
      params.girado_cuando__gte = filters.value.fecha.desde
    }
    if (filters.value.fecha.hasta) {
      params.girado_cuando__lte = filters.value.fecha.hasta
    }

    // Filtros opcionales
    if (filters.value.agencia) {
      params.cliente = filters.value.agencia?.id || filters.value.agencia
    }
    if (filters.value.tipo_pago !== null && filters.value.tipo_pago !== undefined) {
      params.tipo_pago = filters.value.tipo_pago
    }

    console.log('Parámetros de búsqueda:', params)

    const response = await api.get('reservas/reservas/', { params })
    reservas.value = response.data.results || []
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count || 0,
    }
  } catch (error) {
    console.error('Error cargando rendición:', error)
    notifyError('Error al cargar rendición de ventas')
    reservas.value = []
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadRendicion(props)
</script>
