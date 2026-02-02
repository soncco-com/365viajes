<template>
  <q-page class="q-pa-md">
    <page-title title="Agencias" subtitle="Catálogo de agencias de viajes" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-5">
            <q-input
              v-model="filters.search"
              label="Buscar"
              placeholder="Buscar por nombre o teléfono"
              fill-input
              outlined
              dense
              clearable
              @keyup.enter="loadClientes"
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
          <div class="col-12 col-md-4">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadClientes"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla -->
    <data-table
      :rows="clientes"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      :rows-number="pagination.rowsNumber"
      @request="onRequest"
      create-button
      create-label="Nueva Agencia"
      @create="showFormDialog = true"
      no-data-label="No hay agencias registradas"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nueva Agencia' : ''"
          @click="openDialog()"
          :class="$q.screen.xs ? 'full-width' : ''"
        />
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
        </q-td>
      </template>
    </data-table>

    <!-- Dialog de formulario -->
    <q-dialog v-model="showDialog" persistent :maximized="$q.screen.xs">
      <q-card :style="$q.screen.gt.xs ? 'min-width: 600px; max-width: 600px' : ''">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Agencia' : 'Nueva Agencia' }}</div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <q-form @submit="saveCliente" class="q-gutter-md">
            <q-input
              v-model="form.nombre"
              label="Nombre *"
              outlined
              dense
              :rules="[(val) => !!val || 'El nombre es requerido']"
            />

            <q-input
              v-model="form.telefonos"
              label="Teléfonos"
              outlined
              dense
              hint="Ej: 984-123-456"
            />

            <q-toggle v-model="form.activo" label="Activo" />

            <div class="row q-gutter-sm justify-end q-mt-md">
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
import { useQuasar } from 'quasar'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'

const $q = useQuasar()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const clientes = ref([])
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
  telefonos: '',
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
    name: 'telefonos',
    label: 'Teléfonos',
    field: 'telefonos',
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

const loadClientes = async (props) => {
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

    const response = await api.get('base/clientes/', { params })

    clientes.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar las agencias')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadClientes(props)
}

const openDialog = (cliente = null) => {
  if (cliente) {
    isEditing.value = true
    form.value = { ...cliente }
  } else {
    isEditing.value = false
    form.value = {
      nombre: '',
      telefonos: '',
      activo: true,
    }
  }
  showDialog.value = true
}

const saveCliente = async () => {
  saving.value = true

  try {
    const payload = {
      nombre: form.value.nombre,
      telefonos: form.value.telefonos,
      activo: form.value.activo,
    }

    if (isEditing.value) {
      await api.put(`base/clientes/${form.value.id}/`, payload)
      notifySuccess('Agencia actualizada correctamente')
    } else {
      await api.post('base/clientes/', payload)
      notifySuccess('Agencia creada correctamente')
    }

    showDialog.value = false
    loadClientes()
  } catch (error) {
    notifyError('Error al guardar la agencia')
    console.error(error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadClientes()
})
</script>
