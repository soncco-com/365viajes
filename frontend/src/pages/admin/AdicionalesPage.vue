<template>
  <q-page class="q-pa-md">
    <page-title title="Adicionales" subtitle="Catálogo de servicios adicionales" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <q-input
              v-model="filters.search"
              label="Buscar"
              placeholder="Buscar por nombre"
              filled
              clearable
              @keyup.enter="loadAdicionales"
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
              filled
            />
          </div>
          <div class="col-12 col-md-3 flex items-end">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadAdicionales"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla -->
    <data-table
      :rows="adicionales"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Adicional" @click="openDialog()" />
      </template>

      <template v-slot:body-cell-precio="props">
        <q-td :props="props">
          <span class="text-weight-bold">S/ {{ parseFloat(props.row.precio).toFixed(2) }}</span>
        </q-td>
      </template>

      <template v-slot:body-cell-contable="props">
        <q-td :props="props">
          <q-badge :color="props.row.contable ? 'info' : 'warning'">
            {{ props.row.contable ? 'Contable' : 'No Contable' }}
          </q-badge>
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
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)">
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            @click="deleteAdicional(props.row)"
          >
            <q-tooltip>Eliminar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <!-- Dialog de formulario -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Adicional' : 'Nuevo Adicional' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveAdicional" class="q-gutter-md">
            <q-input
              v-model="form.nombre"
              label="Nombre del Adicional"
              filled
              :rules="[(val) => !!val || 'El nombre es requerido']"
              required
            />

            <q-input
              v-model.number="form.precio"
              label="Precio"
              type="number"
              filled
              prefix="S/"
              step="0.01"
              :rules="[(val) => val >= 0 || 'El precio debe ser mayor o igual a 0']"
              required
            />

            <q-toggle v-model="form.contable" label="Contable">
              <q-tooltip>
                Si está desmarcado, este adicional se restará del total (descuento)
              </q-tooltip>
            </q-toggle>

            <q-toggle v-model="form.activo" label="Activo" />

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

const adicionales = ref([])
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
  precio: 0,
  contable: true,
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
    name: 'precio',
    label: 'Precio',
    field: 'precio',
    align: 'right',
    sortable: true,
  },
  {
    name: 'contable',
    label: 'Tipo',
    field: 'contable',
    align: 'center',
    sortable: true,
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

const loadAdicionales = async (props) => {
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

    const response = await api.get('base/adicionales/', { params })

    adicionales.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar los adicionales')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadAdicionales(props)
}

const openDialog = (adicional = null) => {
  if (adicional) {
    isEditing.value = true
    form.value = {
      id: adicional.id,
      nombre: adicional.nombre,
      precio: parseFloat(adicional.precio),
      contable: adicional.contable,
      activo: adicional.activo,
    }
  } else {
    isEditing.value = false
    form.value = {
      nombre: '',
      precio: 0,
      contable: true,
      activo: true,
    }
  }
  showDialog.value = true
}

const saveAdicional = async () => {
  saving.value = true

  try {
    const payload = {
      nombre: form.value.nombre,
      precio: form.value.precio,
      contable: form.value.contable,
      activo: form.value.activo,
    }

    if (isEditing.value) {
      await api.put(`base/adicionales/${form.value.id}/`, payload)
      notifySuccess('Adicional actualizado correctamente')
    } else {
      await api.post('base/adicionales/', payload)
      notifySuccess('Adicional creado correctamente')
    }

    showDialog.value = false
    loadAdicionales()
  } catch (error) {
    notifyError('Error al guardar el adicional')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const deleteAdicional = async (adicional) => {
  const confirmed = await confirm(
    `¿Está seguro de eliminar el adicional "${adicional.nombre}"?`,
    'Eliminar Adicional',
  )

  if (!confirmed) return

  try {
    await api.delete(`base/adicionales/${adicional.id}/`)
    notifySuccess('Adicional eliminado correctamente')
    loadAdicionales()
  } catch (error) {
    notifyError('Error al eliminar el adicional')
    console.error(error)
  }
}

onMounted(() => {
  loadAdicionales()
})
</script>
