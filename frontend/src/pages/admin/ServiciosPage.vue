<template>
  <q-page class="q-pa-md">
    <page-title title="Servicios" subtitle="Catálogo de servicios y tours" />

    <!-- Filtros -->
    <q-card flat bordered class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <q-input
              v-model="filters.search"
              label="Buscar"
              placeholder="Buscar por nombre"
              fill-input
              outlined
              dense
              clearable
              @keyup.enter="loadServicios"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
          <div class="col-12 col-md-2">
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
          <div class="col-12 col-md-3">
            <q-btn
              color="primary"
              icon="search"
              label="Buscar"
              @click="loadServicios"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabla -->
    <data-table
      :rows="servicios"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      create-button
      create-label="Nuevo Servicio"
      @create="showFormDialog = true"
      no-data-label="No hay servicios registrados"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nuevo Servicio' : ''"
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

      <template v-slot:body-cell-mostrar_destinos="props">
        <q-td :props="props">
          <q-badge :color="props.row.mostrar_destinos ? 'info' : 'grey'">
            {{ props.row.mostrar_destinos ? 'Sí' : 'No' }}
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
      <q-card :style="$q.screen.gt.xs ? 'min-width: 700px; max-width: 700px' : ''">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Servicio' : 'Nuevo Servicio' }}</div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <q-form @submit="saveServicio">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-8">
                <q-input
                  v-model="form.nombre"
                  label="Nombre del Servicio *"
                  outlined
                  dense
                  :rules="[(val) => !!val || 'El nombre es requerido']"
                />
              </div>

              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="form.precio"
                  label="Precio *"
                  type="number"
                  outlined
                  dense
                  prefix="S/"
                  step="0.01"
                  :rules="[(val) => val > 0 || 'El precio debe ser mayor a 0']"
                />
              </div>

              <div class="col-12 col-md-4">
                <date-picker
                  v-model="form.fecha_precio"
                  label="Fecha de Precio *"
                  :rules="[(val) => !!val || 'La fecha es requerida']"
                />
              </div>

              <div class="col-12 col-md-4">
                <q-toggle v-model="form.activo" label="Activo" />
              </div>

              <div class="col-12">
                <q-toggle
                  v-model="form.mostrar_destinos"
                  label="Mostrar campo destino en reservas"
                  hint="Permite especificar el destino final al crear reservas"
                />
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
import { todayInLima } from 'src/utils/date'

const $q = useQuasar()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const servicios = ref([])
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
  fecha_precio: todayInLima(),
  mostrar_destinos: false,
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
    name: 'mostrar_destinos',
    label: 'Requiere Destino',
    field: 'mostrar_destinos',
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

const loadServicios = async (props) => {
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

    const response = await api.get('base/servicios/', { params })

    servicios.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar los servicios')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadServicios(props)
}

const openDialog = (servicio = null) => {
  if (servicio) {
    isEditing.value = true
    form.value = {
      id: servicio.id,
      nombre: servicio.nombre,
      precio: parseFloat(servicio.precio),
      fecha_precio: servicio.fecha_precio,
      mostrar_destinos: servicio.mostrar_destinos || false,
      activo: servicio.activo,
    }
  } else {
    isEditing.value = false
    form.value = {
      nombre: '',
      precio: 0,
      fecha_precio: todayInLima(),
      mostrar_destinos: false,
      activo: true,
    }
  }
  showDialog.value = true
}

const saveServicio = async () => {
  saving.value = true

  try {
    const payload = {
      nombre: form.value.nombre,
      precio: form.value.precio,
      fecha_precio: form.value.fecha_precio,
      mostrar_destinos: form.value.mostrar_destinos,
      activo: form.value.activo,
    }

    if (isEditing.value) {
      await api.put(`base/servicios/${form.value.id}/`, payload)
      notifySuccess('Servicio actualizado correctamente')
    } else {
      await api.post('base/servicios/', payload)
      notifySuccess('Servicio creado correctamente')
    }

    showDialog.value = false
    loadServicios()
  } catch (error) {
    notifyError('Error al guardar el servicio')
    console.error(error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadServicios()
})
</script>
