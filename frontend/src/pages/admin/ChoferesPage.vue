<template>
  <q-page class="q-pa-md">
    <page-title title="Transportes" subtitle="Catálogo de transportes y conductores" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-8">
            <q-input
              v-model="filters.search"
              label="Buscar"
              placeholder="Buscar por nombre"
              outlined
              dense
              clearable
              @keyup.enter="loadChoferes"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
          <div class="col-12 col-md-4">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadChoferes"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla -->
    <data-table
      :rows="choferes"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      create-button
      create-label="Nuevo Conductor"
      @create="showFormDialog = true"
      no-data-label="No hay conductores registrados"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nuevo Transporte' : ''"
          @click="openDialog()"
          :class="$q.screen.xs ? 'full-width' : ''"
        />
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
          <div class="text-h6">{{ isEditing ? 'Editar Transporte' : 'Nuevo Transporte' }}</div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <q-form @submit="saveChofer" class="q-gutter-md">
            <q-input
              v-model="form.nombre"
              label="Nombre *"
              outlined
              dense
              :rules="[(val) => !!val || 'El nombre es requerido']"
            />

            <q-input
              v-model="form.telefono"
              label="Teléfono *"
              outlined
              dense
              :rules="[(val) => !!val || 'El teléfono es requerido']"
            />

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

const choferes = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)

const filters = ref({
  search: '',
})

const form = ref({
  nombre: '',
  telefono: '',
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
    name: 'telefono',
    label: 'Teléfono',
    field: 'telefono',
    align: 'left',
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

const loadChoferes = async (props) => {
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

    const response = await api.get('base/choferes/', { params })

    choferes.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar los transportes')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadChoferes(props)
}

const openDialog = (chofer = null) => {
  if (chofer) {
    isEditing.value = true
    form.value = { ...chofer }
  } else {
    isEditing.value = false
    form.value = {
      nombre: '',
      telefono: '',
    }
  }
  showDialog.value = true
}

const saveChofer = async () => {
  saving.value = true

  try {
    const payload = {
      nombre: form.value.nombre,
      telefono: form.value.telefono,
    }

    if (isEditing.value) {
      await api.put(`base/choferes/${form.value.id}/`, payload)
      notifySuccess('Transporte actualizado correctamente')
    } else {
      await api.post('base/choferes/', payload)
      notifySuccess('Transporte creado correctamente')
    }

    showDialog.value = false
    loadChoferes()
  } catch (error) {
    notifyError('Error al guardar el transporte')
    console.error(error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadChoferes()
})
</script>
