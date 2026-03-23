<template>
  <q-page class="q-pa-md">
    <page-title title="Gastos" subtitle="Registro de gastos operacionales" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-5">
            <date-range-picker v-model="filters.fecha" label="Rango de fechas" />
          </div>
          <div class="col-12 col-md-4" v-if="isAdmin">
            <autocomplete-input
              v-model="filters.usuario"
              label="Usuario"
              endpoint="base/usuarios/"
              option-label="username"
              clearable
            />
          </div>
          <div class="col-12 col-md-3 flex items-center" :class="{ 'col-md-7': !isAdmin }">
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

            <q-input
              v-model="form.descripcion"
              label="Descripción"
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
import { useAuth } from 'src/composables/useAuth'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'
import DatePicker from 'src/components/DatePicker.vue'
import DateRangePicker from 'src/components/DateRangePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()
const { isAdmin } = useAuth()

const gastos = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const filters = ref({ fecha: { desde: null, hasta: null }, usuario: null })
const form = ref({
  fecha: new Date().toISOString().split('T')[0],
  descripcion: '',
  monto: 0,
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
    name: 'descripcion',
    label: 'Descripción',
    field: 'descripcion',
    align: 'left',
    sortable: true,
  },
  { name: 'monto', label: 'Monto', field: 'monto', align: 'right', sortable: true },
  {
    name: 'creado_por',
    label: 'Usuario',
    field: 'creado_por_nombre',
    align: 'left',
    sortable: true,
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

    if (filters.value.fecha.range) {
      params.fecha__range = filters.value.fecha.range
    } else if (filters.value.fecha.desde) {
      params.fecha__gte = filters.value.fecha.desde
    } else if (filters.value.fecha.hasta) {
      params.fecha__lte = filters.value.fecha.hasta
    }
    if (filters.value.usuario) {
      params.creado_por = filters.value.usuario?.id || filters.value.usuario
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
    form.value = { ...gasto }
  } else {
    form.value = {
      fecha: new Date().toISOString().split('T')[0],
      descripcion: '',
      monto: 0,
    }
  }
  showDialog.value = true
}

const saveGasto = async () => {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.put(`reservas/gastos/${form.value.id}/`, form.value)
      notifySuccess('Gasto actualizado')
    } else {
      await api.post('reservas/gastos/', form.value)
      notifySuccess('Gasto registrado')
    }
    showDialog.value = false
    loadGastos()
  } finally {
    saving.value = false
  }
}

const deleteGasto = async (gasto) => {
  if (!(await confirm(`¿Eliminar gasto "${gasto.descripcion}"?`))) return
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
  filters.value.fecha = { desde: today, hasta: today }
  loadGastos()
})
</script>
