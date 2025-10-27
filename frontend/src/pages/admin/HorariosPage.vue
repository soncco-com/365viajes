<template>
  <q-page class="q-pa-md">
    <page-title title="Horarios" subtitle="Gestión de horarios de servicios por lugar" />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-5">
            <autocomplete-input
              v-model="filters.servicio"
              label="Servicio"
              endpoint="base/servicios"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-5">
            <autocomplete-input
              v-model="filters.lugar"
              label="Lugar"
              endpoint="base/lugares"
              option-label="nombre"
            />
          </div>
          <div class="col-12 col-md-2 flex items-center">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadHorarios"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="horarios"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn color="primary" icon="add" label="Nuevo Horario" @click="openDialog()" />
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)" />
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            @click="deleteHorario(props.row)"
          />
        </q-td>
      </template>
    </data-table>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Horario' : 'Nuevo Horario' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveHorario" class="q-gutter-md">
            <autocomplete-input
              v-model="form.servicio"
              label="Servicio"
              endpoint="base/servicios"
              option-label="nombre"
              required
            />

            <autocomplete-input
              v-model="form.lugar"
              label="Lugar"
              endpoint="base/lugares"
              option-label="nombre"
              required
            />

            <q-input
              v-model="form.hora"
              label="Hora"
              type="time"
              filled
              :rules="[(val) => !!val || 'Requerido']"
              required
            />

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
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const horarios = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const filters = ref({ servicio: null, lugar: null })
const form = ref({ servicio: null, lugar: null, hora: '' })

const columns = [
  {
    name: 'servicio',
    label: 'Servicio',
    field: (row) => row.servicio?.nombre,
    align: 'left',
    sortable: true,
  },
  {
    name: 'lugar',
    label: 'Lugar',
    field: (row) => row.lugar?.nombre,
    align: 'left',
    sortable: true,
  },
  { name: 'hora', label: 'Hora', field: 'hora', align: 'center', sortable: true },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'servicio',
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

    if (filters.value.servicio) {
      params.servicio = filters.value.servicio.id
    }
    if (filters.value.lugar) {
      params.lugar = filters.value.lugar.id
    }

    const response = await api.get('base/horarios/', { params })
    horarios.value = response.data.results
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

const onRequest = (props) => loadHorarios(props)

const openDialog = (horario = null) => {
  isEditing.value = !!horario
  if (horario) {
    form.value = { ...horario }
  } else {
    form.value = { servicio: null, lugar: null, hora: '' }
  }
  showDialog.value = true
}

const saveHorario = async () => {
  saving.value = true
  try {
    const payload = {
      servicio: form.value.servicio?.id || form.value.servicio,
      lugar: form.value.lugar?.id || form.value.lugar,
      hora: form.value.hora,
    }

    if (isEditing.value) {
      await api.put(`base/horarios/${form.value.id}/`, payload)
      notifySuccess('Horario actualizado')
    } else {
      await api.post('base/horarios/', payload)
      notifySuccess('Horario creado')
    }
    showDialog.value = false
    loadHorarios()
  } finally {
    saving.value = false
  }
}

const deleteHorario = async (horario) => {
  if (
    !(await confirm(
      `¿Eliminar horario de ${horario.servicio?.nombre} en ${horario.lugar?.nombre}?`,
    ))
  )
    return
  try {
    await api.delete(`base/horarios/${horario.id}/`)
    notifySuccess('Horario eliminado')
    loadHorarios()
  } catch {
    notifyError('Error al eliminar')
  }
}

onMounted(() => loadHorarios())
</script>
