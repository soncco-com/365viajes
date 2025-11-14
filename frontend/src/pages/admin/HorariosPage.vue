<template>
  <q-page class="q-pa-md">
    <page-title title="Horarios" subtitle="Horarios de servicios por hotel" />

    <!-- Tabla -->
    <data-table
      :rows="horarios"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      :searchable="false"
      create-button
      create-label="Nuevo Horario"
      @create="openDialog()"
      no-data-label="No hay horarios configurados"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nuevo Horario' : ''"
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
      <q-card :style="$q.screen.gt.xs ? 'min-width: 700px; max-width: 800px' : ''">
        <q-card-section class="bg-primary text-white">
          <div class="row items-center">
            <q-icon :name="isEditing ? 'edit' : 'add'" size="sm" class="q-mr-sm" />
            <div class="text-h6">{{ isEditing ? 'Editar Horario' : 'Nuevo Horario' }}</div>
            <q-space />
            <q-btn flat dense round icon="close" @click="showDialog = false" />
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-md">
          <q-form @submit="saveHorario" class="">
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <div class="text-subtitle2 text-grey-7 q-mb-sm">
                  <q-icon name="info" size="xs" class="q-mr-xs" />
                  Configura el horario de recojo para un servicio en un hotel específico
                </div>
              </div>

              <div class="col-12 col-md-6">
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

              <div class="col-12 col-md-6">
                <autocomplete-input
                  v-model="form.lugar"
                  label="Hotel"
                  endpoint="base/lugares/"
                  option-label="nombre"
                  :rules="[(val) => !!val || 'El hotel es requerido']"
                >
                  <template v-slot:prepend>
                    <q-icon name="hotel" />
                  </template>
                </autocomplete-input>
              </div>

              <div class="col-12 col-md-6">
                <q-input
                  v-model="form.hora"
                  label="Hora de Recojo"
                  outlined
                  dense
                  type="time"
                  :rules="[(val) => !!val || 'La hora es requerida']"
                >
                  <template v-slot:prepend>
                    <q-icon name="schedule" />
                  </template>
                  <template v-slot:hint> Formato 24 horas (ej: 08:30) </template>
                </q-input>
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="Cancelar" color="grey" flat @click="showDialog = false" :disable="saving" />
          <q-btn
            label="Guardar Horario"
            color="primary"
            icon-right="save"
            @click="saveHorario"
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
const { notifySuccess, notifyError } = useNotify()

const horarios = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)

const form = ref({
  servicio: null,
  lugar: null,
  hora: '',
})

const columns = [
  {
    name: 'servicio_nombre',
    label: 'Servicio',
    field: (row) => row.servicio?.nombre || row.servicio_nombre || 'N/A',
    align: 'left',
    sortable: true,
  },
  {
    name: 'lugar_nombre',
    label: 'Hotel',
    field: (row) => row.lugar?.nombre || row.lugar_nombre || 'N/A',
    align: 'left',
    sortable: true,
  },
  {
    name: 'hora',
    label: 'Hora',
    field: 'hora',
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
  sortBy: 'servicio_nombre',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadHorarios = async (props) => {
  loading.value = true

  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value

    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    const response = await api.get('base/horarios/', { params })

    horarios.value = response.data.results
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy
    pagination.value.descending = descending
    pagination.value.rowsNumber = response.data.count
  } catch (error) {
    notifyError('Error al cargar los horarios')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => {
  loadHorarios(props)
}

const openDialog = (horario = null) => {
  if (horario) {
    isEditing.value = true
    // Asegurar que los autocompletes reciban el objeto completo con id y nombre
    form.value = {
      id: horario.id,
      servicio: horario.servicio
        ? horario.servicio
        : { id: horario.servicio, nombre: horario.servicio_nombre },
      lugar: horario.lugar ? horario.lugar : { id: horario.lugar, nombre: horario.lugar_nombre },
      hora: horario.hora,
    }
  } else {
    isEditing.value = false
    form.value = {
      servicio: null,
      lugar: null,
      hora: '',
    }
  }
  showDialog.value = true
}

const saveHorario = async () => {
  saving.value = true

  try {
    const payload = {
      servicio: form.value.servicio?.id,
      lugar: form.value.lugar?.id,
      hora: form.value.hora,
    }

    if (isEditing.value) {
      await api.put(`base/horarios/${form.value.id}/`, payload)
      notifySuccess('Horario actualizado correctamente')
    } else {
      await api.post('base/horarios/', payload)
      notifySuccess('Horario creado correctamente')
    }

    showDialog.value = false
    loadHorarios()
  } catch (error) {
    notifyError('Error al guardar el horario')
    console.error(error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadHorarios()
})
</script>
