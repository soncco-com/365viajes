<template>
  <q-page class="q-pa-md">
    <page-title
      title="Paradas de Servicios"
      subtitle="Gestiona las paradas/itinerarios de cada servicio turístico"
    />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-10">
            <autocomplete-input
              v-model="filters.servicio"
              label="Filtrar por Servicio"
              endpoint="base/servicios/"
              option-label="nombre"
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadParadas"
              :loading="loading"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="paradas"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No hay paradas configuradas"
      row-key="id"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nueva Parada' : ''"
          @click="openDialog()"
        />
      </template>

      <template v-slot:body-cell-orden="props">
        <q-td :props="props">
          <div class="row items-center q-gutter-xs">
            <q-chip color="primary" text-color="white" size="sm">
              {{ props.row.orden }}
            </q-chip>
            <q-btn
              flat
              dense
              round
              size="sm"
              icon="arrow_upward"
              color="primary"
              @click="moveParada(props.row, 'up')"
              :disable="props.rowIndex === 0"
            >
              <q-tooltip>Mover arriba</q-tooltip>
            </q-btn>
            <q-btn
              flat
              dense
              round
              size="sm"
              icon="arrow_downward"
              color="primary"
              @click="moveParada(props.row, 'down')"
              :disable="props.rowIndex === paradas.length - 1"
            >
              <q-tooltip>Mover abajo</q-tooltip>
            </q-btn>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-descripcion="props">
        <q-td :props="props">
          <div class="text-caption text-grey-7" style="max-width: 300px">
            {{ props.row.descripcion || 'Sin descripción' }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)">
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="delete" color="negative" @click="deleteParada(props.row)">
            <q-tooltip>Eliminar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <!-- Dialog de formulario -->
    <q-dialog v-model="showDialog" persistent :maximized="$q.screen.xs">
      <q-card :style="$q.screen.gt.xs ? 'min-width: 600px; max-width: 700px' : ''">
        <q-card-section class="bg-primary text-white">
          <div class="row items-center">
            <q-icon :name="isEditing ? 'edit' : 'add'" size="sm" class="q-mr-sm" />
            <div class="text-h6">
              {{ isEditing ? 'Editar Parada' : 'Nueva Parada' }}
            </div>
            <q-space />
            <q-btn flat dense round icon="close" @click="showDialog = false" />
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-md">
          <q-form @submit="saveParada" class="q-gutter-md">
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <div class="text-subtitle2 text-grey-7 q-mb-sm">
                  <q-icon name="info" size="xs" class="q-mr-xs" />
                  Define los puntos de parada o itinerario del servicio turístico
                </div>
              </div>

              <div class="col-12">
                <autocomplete-input
                  v-model="form.servicio"
                  label="Servicio"
                  endpoint="base/servicios/"
                  option-label="nombre"
                  :rules="[(val) => !!val || 'El servicio es requerido']"
                >
                  <template v-slot:prepend>
                    <q-icon name="tour" />
                  </template>
                </autocomplete-input>
              </div>

              <div class="col-12 col-md-8">
                <q-input
                  v-model="form.nombre"
                  label="Nombre de la Parada"
                  outlined
                  dense
                  :rules="[(val) => !!val || 'El nombre es requerido']"
                >
                  <template v-slot:prepend>
                    <q-icon name="location_on" />
                  </template>
                  <template v-slot:hint> Ej: Plaza de Armas, Mirador, Catedral </template>
                </q-input>
              </div>

              <div class="col-12 col-md-4">
                <q-input
                  v-model.number="form.orden"
                  label="Orden"
                  type="number"
                  outlined
                  dense
                  :rules="[(val) => val > 0 || 'El orden debe ser mayor a 0']"
                >
                  <template v-slot:prepend>
                    <q-icon name="format_list_numbered" />
                  </template>
                  <template v-slot:hint> Posición en el itinerario </template>
                </q-input>
              </div>

              <div class="col-12">
                <q-input
                  v-model="form.descripcion"
                  label="Descripción"
                  type="textarea"
                  outlined
                  dense
                  rows="4"
                  hint="Detalles sobre esta parada (duración, actividades, etc.)"
                >
                  <template v-slot:prepend>
                    <q-icon name="description" />
                  </template>
                </q-input>
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="Cancelar" color="grey" flat @click="showDialog = false" :disable="saving" />
          <q-btn
            label="Guardar"
            color="primary"
            icon-right="save"
            @click="saveParada"
            :loading="saving"
            :disable="saving"
            unelevated
          />
        </q-card-actions>
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
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const $q = useQuasar()
const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const paradas = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)

const filters = ref({
  servicio: null,
})

const form = ref({
  servicio: null,
  nombre: '',
  orden: 1,
  descripcion: '',
})

const columns = [
  {
    name: 'servicio_nombre',
    label: 'Servicio',
    field: 'servicio_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'orden',
    label: 'Orden',
    field: 'orden',
    align: 'center',
    sortable: true,
  },
  {
    name: 'nombre',
    label: 'Parada',
    field: 'nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'descripcion',
    label: 'Descripción',
    field: 'descripcion',
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
  sortBy: 'orden',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadParadas = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.servicio) {
      params.servicio = filters.value.servicio?.id || filters.value.servicio
    }

    const response = await api.get('base/servicio-paradas/', { params })
    paradas.value = response.data.results || []
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count || 0,
    }
  } catch (error) {
    notifyError('Error al cargar paradas')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadParadas(props)

const openDialog = (parada = null) => {
  if (parada) {
    isEditing.value = true
    form.value = {
      id: parada.id,
      servicio: parada.servicio || { id: parada.servicio, nombre: parada.servicio_nombre },
      nombre: parada.nombre,
      orden: parada.orden,
      descripcion: parada.descripcion || '',
    }
  } else {
    isEditing.value = false
    // Si hay filtro activo, usar ese servicio
    form.value = {
      servicio: filters.value.servicio || null,
      nombre: '',
      orden: paradas.value.length + 1,
      descripcion: '',
    }
  }
  showDialog.value = true
}

const saveParada = async () => {
  saving.value = true
  try {
    const payload = {
      servicio: form.value.servicio?.id || form.value.servicio,
      nombre: form.value.nombre,
      orden: form.value.orden,
      descripcion: form.value.descripcion,
    }

    if (isEditing.value) {
      await api.put(`base/servicio-paradas/${form.value.id}/`, payload)
      notifySuccess('Parada actualizada correctamente')
    } else {
      await api.post('base/servicio-paradas/', payload)
      notifySuccess('Parada creada correctamente')
    }

    showDialog.value = false
    loadParadas()
  } catch (error) {
    notifyError('Error al guardar la parada')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const deleteParada = async (parada) => {
  if (!(await confirm(`¿Eliminar la parada "${parada.nombre}"?`))) return

  try {
    await api.delete(`base/servicio-paradas/${parada.id}/`)
    notifySuccess('Parada eliminada')
    loadParadas()
  } catch {
    notifyError('Error al eliminar')
  }
}

const moveParada = async (parada, direction) => {
  const currentIndex = paradas.value.findIndex((p) => p.id === parada.id)
  if (currentIndex === -1) return

  const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
  if (targetIndex < 0 || targetIndex >= paradas.value.length) return

  const targetParada = paradas.value[targetIndex]

  try {
    // Intercambiar órdenes
    const tempOrden = parada.orden
    await api.patch(`base/servicio-paradas/${parada.id}/`, { orden: targetParada.orden })
    await api.patch(`base/servicio-paradas/${targetParada.id}/`, { orden: tempOrden })

    notifySuccess('Orden actualizado')
    loadParadas()
  } catch {
    notifyError('Error al cambiar el orden')
  }
}

onMounted(() => {
  loadParadas()
})
</script>
