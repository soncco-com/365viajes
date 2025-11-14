<template>
  <q-page class="q-pa-md">
    <page-title title="Gastos" subtitle="Registro de gastos operacionales" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.orden"
              label="Orden de Servicio"
              endpoint="reservas/ordenes-servicio"
              option-label="id"
              :option-display="(o) => `#${o.id} - ${o.fecha}`"
            />
          </div>
          <div class="col-12 col-md-2 flex items-center">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadGastos"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="gastos"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No se encontraron gastos registrados"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Gasto" @click="openDialog()" />
      </template>

      <template v-slot:body-cell-monto="props">
        <q-td :props="props">S/ {{ props.row.monto }}</q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)" />
          <q-btn flat dense round icon="delete" color="negative" @click="deleteGasto(props.row)" />
        </q-td>
      </template>
    </data-table>

    <q-card class="q-mt-md" v-if="gastos.length > 0">
      <q-card-section>
        <div class="text-h6">Total Gastos</div>
        <div class="text-h4 text-negative q-mt-sm">S/ {{ totalGastos.toFixed(2) }}</div>
      </q-card-section>
    </q-card>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Gasto' : 'Nuevo Gasto' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveGasto" class="q-gutter-md">
            <date-picker v-model="form.fecha" label="Fecha" required />

            <autocomplete-input
              v-model="form.orden_servicio"
              label="Orden de Servicio"
              endpoint="reservas/ordenes-servicio"
              option-label="id"
              :option-display="(o) => `#${o.id} - ${o.fecha} - Guía: ${o.guia?.nombre_completo}`"
              required
            />

            <q-input
              v-model="form.concepto"
              label="Concepto"
              filled
              :rules="[(val) => !!val || 'Requerido']"
              required
            />

            <q-input
              v-model.number="form.monto"
              label="Monto"
              type="number"
              step="0.01"
              filled
              prefix="S/"
              :rules="[(val) => val > 0 || 'Debe ser mayor a 0']"
              required
            />

            <q-input
              v-model="form.observaciones"
              label="Observaciones"
              type="textarea"
              filled
              rows="3"
            />

            <div class="row q-gutter-sm justify-end">
              <q-btn label="Cancelar" color="grey" flat @click="showDialog = false" />
              <q-btn label="Guardar" type="submit" color="primary" :loading="saving" />
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
import DataTable from 'src/components/DataTable.vue'
import DatePicker from 'src/components/DatePicker.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const gastos = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const filters = ref({ fecha: { from: null, to: null }, orden: null })
const form = ref({
  fecha: new Date().toISOString().split('T')[0],
  orden_servicio: null,
  concepto: '',
  monto: 0,
  observaciones: '',
})

const columns = [
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
    name: 'orden',
    label: 'Orden Servicio',
    field: (row) => `#${row.orden_servicio?.id}`,
    align: 'left',
  },
  { name: 'concepto', label: 'Concepto', field: 'concepto', align: 'left' },
  { name: 'monto', label: 'Monto', field: 'monto', align: 'right', sortable: true },
  { name: 'observaciones', label: 'Observaciones', field: 'observaciones', align: 'left' },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'fecha',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const totalGastos = computed(() => {
  return gastos.value.reduce((sum, g) => sum + parseFloat(g.monto || 0), 0)
})

const loadGastos = async (props) => {
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
    if (filters.value.orden) {
      params.orden_servicio = filters.value.orden?.id || filters.value.orden
    }

    const response = await api.get('reservas/gastos/', { params })
    gastos.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } catch {
    notifyError('Error al cargar gastos')
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadGastos(props)

const openDialog = (gasto = null) => {
  isEditing.value = !!gasto
  if (gasto) {
    form.value = { ...gasto, orden_servicio: gasto.orden_servicio }
  } else {
    form.value = {
      fecha: new Date().toISOString().split('T')[0],
      orden_servicio: null,
      concepto: '',
      monto: 0,
      observaciones: '',
    }
  }
  showDialog.value = true
}

const saveGasto = async () => {
  saving.value = true
  try {
    const payload = {
      ...form.value,
      orden_servicio: form.value.orden_servicio?.id || form.value.orden_servicio,
    }

    if (isEditing.value) {
      await api.put(`reservas/gastos/${form.value.id}/`, payload)
      notifySuccess('Gasto actualizado')
    } else {
      await api.post('reservas/gastos/', payload)
      notifySuccess('Gasto registrado')
    }
    showDialog.value = false
    loadGastos()
  } finally {
    saving.value = false
  }
}

const deleteGasto = async (gasto) => {
  if (!(await confirm(`¿Eliminar gasto "${gasto.concepto}"?`))) return
  try {
    await api.delete(`reservas/gastos/${gasto.id}/`)
    notifySuccess('Gasto eliminado')
    loadGastos()
  } catch {
    notifyError('Error al eliminar')
  }
}

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  filters.value.fecha = { from: today, to: today }
  loadGastos()
})
</script>
