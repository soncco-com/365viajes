<template>
  <q-page class="q-pa-md">
    <page-title title="Hoteles" subtitle="Catálogo de hoteles y lugares de recojo" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <q-input
              v-model="filters.search"
              label="Buscar"
              placeholder="Buscar por nombre o dirección"
              fill-input
              outlined
              dense
              clearable
              @keyup.enter="loadLugares"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
          <div class="col-12 col-md-3">
            <q-select
              v-model="filters.activo"
              label="Estado"
              :options="estadoOptions"
              emit-value
              map-options
              clearable
              fill-input
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-3 flex items-end">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadLugares"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla -->
    <data-table
      :rows="lugares"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Hotel" @click="openDialog()" />
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
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)">
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="delete" color="negative" @click="deleteLugar(props.row)">
            <q-tooltip>Eliminar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <!-- Dialog de formulario -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Hotel' : 'Nuevo Hotel' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveLugar" class="q-gutter-md">
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <q-input
                  v-model="form.nombre"
                  label="Nombre del Hotel"
                  filled
                  :rules="[(val) => !!val || 'El nombre es requerido']"
                  required
                />
              </div>

              <div class="col-12">
                <q-input
                  v-model="form.direccion"
                  label="Dirección"
                  filled
                  type="textarea"
                  rows="2"
                />
              </div>

              <div class="col-12 col-md-6">
                <q-input v-model="form.telefono" label="Teléfono" filled />
              </div>

              <div class="col-12 col-md-6">
                <q-input v-model="form.email" label="Email" filled type="email" />
              </div>

              <div class="col-12">
                <q-toggle v-model="form.activo" label="Activo" />
              </div>
            </div>

            <div class="row q-gutter-sm justify-end">
              <q-btn label="Cancelar" color="grey" flat @click="showDialog = false" />
              <q-btn
                label="Guardar"
                type="submit"
                color="primary"
                :loading="saving"
                :disable="saving"
              />
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

const lugares = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)

const filters = ref({
  search: '',
  activo: null,
})

const estadoOptions = [
  { label: 'Activo', value: true },
  { label: 'Inactivo', value: false },
]

const form = ref({
  nombre: '',
  direccion: '',
  telefono: '',
  email: '',
  activo: true,
})

const columns = [
  {
    name: 'nombre',
    label: 'Nombre',
    field: 'nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'direccion',
    label: 'Dirección',
    field: 'direccion',
    align: 'left',
  },
  {
    name: 'telefono',
    label: 'Teléfono',
    field: 'telefono',
    align: 'left',
  },
  {
    name: 'activo',
    label: 'Estado',
    field: 'activo',
    align: 'center',
    sortable: true,
  },
  {
    name: 'actions',
    label: 'Acciones',
    field: 'actions',
    align: 'center',
  },
]

const pagination = ref({
  sortBy: 'nombre',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadLugares = async (props) => {
  loading.value = true

  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value

    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.search) {
      params.search = filters.value.search
    }

    if (filters.value.activo !== null && filters.value.activo !== undefined) {
      params.activo = filters.value.activo
    }

    const response = await api.get('base/lugares/', { params })

    lugares.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar los hoteles')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadLugares(props)
}

const openDialog = (lugar = null) => {
  if (lugar) {
    isEditing.value = true
    form.value = { ...lugar }
  } else {
    isEditing.value = false
    form.value = {
      nombre: '',
      direccion: '',
      telefono: '',
      email: '',
      activo: true,
    }
  }
  showDialog.value = true
}

const saveLugar = async () => {
  saving.value = true

  try {
    const payload = {
      nombre: form.value.nombre,
      direccion: form.value.direccion,
      telefono: form.value.telefono,
      email: form.value.email,
      activo: form.value.activo,
    }

    if (isEditing.value) {
      await api.put(`base/lugares/${form.value.id}/`, payload)
      notifySuccess('Hotel actualizado correctamente')
    } else {
      await api.post('base/lugares/', payload)
      notifySuccess('Hotel creado correctamente')
    }

    showDialog.value = false
    loadLugares()
  } catch (error) {
    notifyError('Error al guardar el hotel')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const deleteLugar = async (lugar) => {
  const confirmed = await confirm(
    `¿Está seguro de eliminar el hotel "${lugar.nombre}"?`,
    'Eliminar Hotel',
  )

  if (!confirmed) return

  try {
    await api.delete(`base/lugares/${lugar.id}/`)
    notifySuccess('Hotel eliminado correctamente')
    loadLugares()
  } catch (error) {
    notifyError('Error al eliminar el hotel')
    console.error(error)
  }
}

onMounted(() => {
  loadLugares()
})
</script>
