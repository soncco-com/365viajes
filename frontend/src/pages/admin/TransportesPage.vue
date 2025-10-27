<template>
  <q-page class="q-pa-md">
    <page-title title="Transportes" subtitle="Catálogo de vehículos de transporte" />

    <data-table
      :rows="transportes"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Transporte" @click="openDialog()" />
      </template>

      <template v-slot:body-cell-activo="props">
        <q-td :props="props">
          <q-badge :color="props.row.activo ? 'positive' : 'negative'">
            {{ props.row.activo ? 'Activo' : 'Inactivo' }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)" />
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            @click="deleteTransporte(props.row)"
          />
        </q-td>
      </template>
    </data-table>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Transporte' : 'Nuevo Transporte' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveTransporte" class="q-gutter-md">
            <q-input
              v-model="form.placa"
              label="Placa"
              filled
              :rules="[(val) => !!val || 'Requerido']"
              required
            />
            <q-input v-model="form.marca" label="Marca" filled />
            <q-input v-model="form.modelo" label="Modelo" filled />
            <q-input v-model.number="form.capacidad" label="Capacidad" type="number" filled />
            <q-toggle v-model="form.activo" label="Activo" />

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
import { ref, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'

const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const transportes = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const form = ref({ placa: '', marca: '', modelo: '', capacidad: 0, activo: true })

const columns = [
  { name: 'placa', label: 'Placa', field: 'placa', align: 'left', sortable: true },
  { name: 'marca', label: 'Marca', field: 'marca', align: 'left' },
  { name: 'modelo', label: 'Modelo', field: 'modelo', align: 'left' },
  { name: 'capacidad', label: 'Capacidad', field: 'capacidad', align: 'center' },
  { name: 'activo', label: 'Estado', field: 'activo', align: 'center', sortable: true },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'placa',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadTransportes = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = { page, page_size: rowsPerPage, ordering: (descending ? '-' : '') + sortBy }
    const response = await api.get('base/transportes/', { params })
    transportes.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadTransportes(props)

const openDialog = (transporte = null) => {
  isEditing.value = !!transporte
  form.value = transporte
    ? { ...transporte }
    : { placa: '', marca: '', modelo: '', capacidad: 0, activo: true }
  showDialog.value = true
}

const saveTransporte = async () => {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.put(`base/transportes/${form.value.id}/`, form.value)
      notifySuccess('Transporte actualizado')
    } else {
      await api.post('base/transportes/', form.value)
      notifySuccess('Transporte creado')
    }
    showDialog.value = false
    loadTransportes()
  } finally {
    saving.value = false
  }
}

const deleteTransporte = async (transporte) => {
  if (!(await confirm(`¿Eliminar transporte "${transporte.placa}"?`))) return
  try {
    await api.delete(`base/transportes/${transporte.id}/`)
    notifySuccess('Transporte eliminado')
    loadTransportes()
  } catch {
    notifyError('Error al eliminar')
  }
}

onMounted(() => loadTransportes())
</script>
