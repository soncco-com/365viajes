<template>
  <q-page class="q-pa-md">
    <page-title title="Adicionales" subtitle="Catálogo de servicios adicionales" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-5">
            <q-input
              v-model="filters.search"
              label="Buscar"
              placeholder="Buscar por nombre"
              fill-input
              outlined
              dense
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
      create-button
      create-label="Nuevo Adicional"
      @create="showFormDialog = true"
      no-data-label="No hay servicios adicionales registrados"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nuevo Adicional' : ''"
          @click="openDialog()"
          :class="$q.screen.xs ? 'full-width' : ''"
        />
      </template>

      <template v-slot:body-cell-precio="props">
        <q-td :props="props">
          <span class="text-weight-bold"
            >S/ {{ parseFloat(props.row.precio || 0).toFixed(2) }}</span
          >
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
        </q-td>
      </template>
    </data-table>

    <!-- Dialog de formulario -->
    <q-dialog v-model="showDialog" persistent :maximized="$q.screen.xs">
      <q-card :style="$q.screen.gt.xs ? 'min-width: 600px; max-width: 600px' : ''">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Adicional' : 'Nuevo Adicional' }}</div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <q-form @submit="saveAdicional" class="q-gutter-md">
            <q-input
              v-model="form.nombre"
              label="Nombre del Adicional *"
              outlined
              dense
              :rules="[(val) => !!val || 'El nombre es requerido']"
            />

            <q-input
              v-model.number="form.precio"
              label="Precio *"
              type="number"
              outlined
              dense
              prefix="S/"
              step="0.01"
              :rules="[(val) => val >= 0 || 'El precio debe ser mayor o igual a 0']"
            />

            <date-picker
              v-model="form.fecha_precio"
              label="Fecha de Precio *"
              :rules="[(val) => !!val || 'La fecha es requerida']"
            />

            <div class="row q-col-gutter-md">
              <div class="col-6">
                <q-toggle v-model="form.contable" label="Contable">
                  <q-tooltip>
                    Si está desmarcado, este adicional se restará del total (descuento)
                  </q-tooltip>
                </q-toggle>
              </div>
              <div class="col-6">
                <q-toggle v-model="form.almuerzo" label="Almuerzo" />
              </div>
              <div class="col-6">
                <q-toggle v-model="form.boleto" label="Boleto" />
              </div>
              <div class="col-6">
                <q-toggle v-model="form.visible" label="Visible" />
              </div>
              <div class="col-6">
                <q-toggle v-model="form.activo" label="Activo" />
              </div>
            </div>

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
import DatePicker from 'src/components/DatePicker.vue'

const $q = useQuasar()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

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
  fecha_precio: null,
  contable: true,
  almuerzo: false,
  boleto: false,
  visible: true,
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
      fecha_precio: adicional.fecha_precio,
      contable: adicional.contable,
      almuerzo: adicional.almuerzo || false,
      boleto: adicional.boleto || false,
      visible: adicional.visible !== undefined ? adicional.visible : true,
      activo: adicional.activo,
    }
  } else {
    isEditing.value = false
    form.value = {
      nombre: '',
      precio: 0,
      fecha_precio: null,
      contable: true,
      almuerzo: false,
      boleto: false,
      visible: true,
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
      fecha_precio: form.value.fecha_precio,
      contable: form.value.contable,
      almuerzo: form.value.almuerzo,
      boleto: form.value.boleto,
      visible: form.value.visible,
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

onMounted(() => {
  loadAdicionales()
})
</script>
