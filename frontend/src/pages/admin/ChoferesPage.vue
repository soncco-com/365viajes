<template>
  <q-page class="q-pa-md">
    <page-title title="Choferes" subtitle="Catálogo de choferes" />

    <data-table
      :rows="choferes"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Chofer" @click="openDialog()" />
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
          <q-btn flat dense round icon="delete" color="negative" @click="deleteChofer(props.row)" />
        </q-td>
      </template>
    </data-table>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Chofer' : 'Nuevo Chofer' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveChofer" class="q-gutter-md">
            <q-input
              v-model="form.nombre_completo"
              label="Nombre Completo"
              filled
              :rules="[(val) => !!val || 'Requerido']"
              required
            />
            <q-input v-model="form.telefono" label="Teléfono" filled />
            <q-input v-model="form.licencia" label="Licencia" filled />
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

const choferes = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const form = ref({ nombre_completo: '', telefono: '', licencia: '', activo: true })

const columns = [
  {
    name: 'nombre_completo',
    label: 'Nombre',
    field: 'nombre_completo',
    align: 'left',
    sortable: true,
  },
  { name: 'telefono', label: 'Teléfono', field: 'telefono', align: 'left' },
  { name: 'licencia', label: 'Licencia', field: 'licencia', align: 'left' },
  { name: 'activo', label: 'Estado', field: 'activo', align: 'center', sortable: true },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'nombre_completo',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadChoferes = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = { page, page_size: rowsPerPage, ordering: (descending ? '-' : '') + sortBy }
    const response = await api.get('base/choferes/', { params })
    choferes.value = response.data.results
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

const onRequest = (props) => loadChoferes(props)

const openDialog = (chofer = null) => {
  isEditing.value = !!chofer
  form.value = chofer
    ? { ...chofer }
    : { nombre_completo: '', telefono: '', licencia: '', activo: true }
  showDialog.value = true
}

const saveChofer = async () => {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.put(`base/choferes/${form.value.id}/`, form.value)
      notifySuccess('Chofer actualizado')
    } else {
      await api.post('base/choferes/', form.value)
      notifySuccess('Chofer creado')
    }
    showDialog.value = false
    loadChoferes()
  } finally {
    saving.value = false
  }
}

const deleteChofer = async (chofer) => {
  if (!(await confirm(`¿Eliminar chofer "${chofer.nombre_completo}"?`))) return
  try {
    await api.delete(`base/choferes/${chofer.id}/`)
    notifySuccess('Chofer eliminado')
    loadChoferes()
  } catch {
    notifyError('Error al eliminar')
  }
}

onMounted(() => loadChoferes())
</script>
