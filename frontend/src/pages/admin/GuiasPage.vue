<template>
  <q-page class="q-pa-md">
    <page-title title="Guías" subtitle="Catálogo de guías turísticos" />

    <!-- Tabla -->
    <data-table
      :rows="guias"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Guía" @click="openDialog()" />
      </template>

      <template v-slot:body-cell-nombre_completo="props">
        <q-td :props="props">
          <span class="text-weight-bold">{{ props.row.nombre_completo }}</span>
        </q-td>
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
          <q-btn flat dense round icon="delete" color="negative" @click="deleteGuia(props.row)" />
        </q-td>
      </template>
    </data-table>

    <!-- Dialog -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Guía' : 'Nuevo Guía' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveGuia" class="q-gutter-md">
            <q-input
              v-model="form.nombre_completo"
              label="Nombre Completo"
              filled
              :rules="[(val) => !!val || 'El nombre es requerido']"
              required
            />

            <q-input v-model="form.telefono" label="Teléfono" filled />

            <q-input v-model="form.email" label="Email" filled type="email" />

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

const guias = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)

const form = ref({
  nombre_completo: '',
  telefono: '',
  email: '',
  activo: true,
})

const columns = [
  {
    name: 'nombre_completo',
    label: 'Nombre',
    field: 'nombre_completo',
    align: 'left',
    sortable: true,
  },
  { name: 'telefono', label: 'Teléfono', field: 'telefono', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
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

const loadGuias = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = { page, page_size: rowsPerPage, ordering: (descending ? '-' : '') + sortBy }
    const response = await api.get('base/guias/', { params })
    guias.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } catch {
    notifyError('Error al cargar los guías')
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadGuias(props)

const openDialog = (guia = null) => {
  isEditing.value = !!guia
  form.value = guia ? { ...guia } : { nombre_completo: '', telefono: '', email: '', activo: true }
  showDialog.value = true
}

const saveGuia = async () => {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (isEditing.value) {
      await api.put(`base/guias/${form.value.id}/`, payload)
      notifySuccess('Guía actualizado correctamente')
    } else {
      await api.post('base/guias/', payload)
      notifySuccess('Guía creado correctamente')
    }
    showDialog.value = false
    loadGuias()
  } catch {
    notifyError('Error al guardar el guía')
  } finally {
    saving.value = false
  }
}

const deleteGuia = async (guia) => {
  if (!(await confirm(`¿Eliminar guía "${guia.nombre_completo}"?`))) return
  try {
    await api.delete(`base/guias/${guia.id}/`)
    notifySuccess('Guía eliminado correctamente')
    loadGuias()
  } catch {
    notifyError('Error al eliminar el guía')
  }
}

onMounted(() => loadGuias())
</script>
