<template>
  <q-page class="q-pa-md">
    <page-title
      title="Precios Especiales de Adicionales"
      subtitle="Precios personalizados de adicionales para agencias específicas"
    />

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.adicional"
              label="Adicional"
              endpoint="base/adicionales/"
              option-label="nombre"
              clearable
            />
          </div>
          <div class="col-12 col-md-4">
            <autocomplete-input
              v-model="filters.cliente"
              label="Agencia"
              endpoint="base/clientes/"
              option-label="nombre"
              clearable
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="filters.activo"
              :options="estadoOptions"
              label="Estado"
              emit-value
              map-options
              clearable
              outlined
              dense
            />
          </div>
          <div class="col-12 col-md-2">
            <q-btn
              color="primary"
              label="Buscar"
              icon="search"
              @click="loadPrecios"
              :loading="loading"
              class="full-width"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <data-table
      :rows="precios"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      no-data-label="No hay precios especiales configurados"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nuevo Precio Especial' : ''"
          @click="openDialog()"
        />
      </template>

      <template v-slot:body-cell-precio="props">
        <q-td :props="props">
          <div class="text-weight-bold text-positive">
            S/ {{ parseFloat(props.row.precio || 0).toFixed(2) }}
          </div>
          <div class="text-caption text-grey-7" v-if="props.row.adicional">
            Precio normal: S/ {{ parseFloat(props.row.adicional.precio || 0).toFixed(2) }}
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-vigencia="props">
        <q-td :props="props">
          <div>Desde: {{ formatDate(props.row.fecha_desde) }}</div>
          <div v-if="props.row.fecha_hasta" class="text-caption">
            Hasta: {{ formatDate(props.row.fecha_hasta) }}
          </div>
          <div v-else class="text-caption text-grey-7">Sin límite</div>
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
          <q-btn flat dense round icon="delete" color="negative" @click="deletePrecio(props.row)">
            <q-tooltip>Eliminar</q-tooltip>
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
            <div class="text-h6">
              {{ isEditing ? 'Editar Precio Especial' : 'Nuevo Precio Especial' }}
            </div>
            <q-space />
            <q-btn flat dense round icon="close" @click="showDialog = false" />
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-md">
          <q-form @submit="savePrecio">
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <div class="text-subtitle2 text-grey-7 q-mb-sm">
                  <q-icon name="info" size="xs" class="q-mr-xs" />
                  Configure un precio especial para un adicional específico de una agencia
                </div>
              </div>

              <div class="col-12 col-md-6">
                <autocomplete-input
                  v-model="form.adicional"
                  label="Adicional"
                  endpoint="base/adicionales/"
                  option-label="nombre"
                  :rules="[(val) => !!val || 'El adicional es requerido']"
                >
                  <template v-slot:prepend>
                    <q-icon name="explore" />
                  </template>
                </autocomplete-input>
              </div>

              <div class="col-12 col-md-6">
                <autocomplete-input
                  v-model="form.cliente"
                  label="Agencia"
                  endpoint="base/clientes/"
                  option-label="nombre"
                  :rules="[(val) => !!val || 'La agencia es requerida']"
                >
                  <template v-slot:prepend>
                    <q-icon name="business" />
                  </template>
                </autocomplete-input>
              </div>

              <div class="col-12 col-md-6">
                <q-input
                  v-model.number="form.precio"
                  label="Precio Especial"
                  type="number"
                  outlined
                  dense
                  prefix="S/"
                  step="0.01"
                  :rules="[(val) => val > 0 || 'El precio debe ser mayor a 0']"
                >
                  <template v-slot:prepend>
                    <q-icon name="attach_money" />
                  </template>
                </q-input>
              </div>

              <div class="col-12 col-md-6">
                <date-picker
                  v-model="form.fecha_desde"
                  label="Vigencia desde"
                  :rules="[(val) => !!val || 'La fecha es requerida']"
                >
                  <template v-slot:prepend>
                    <q-icon name="event" />
                  </template>
                </date-picker>
              </div>

              <div class="col-12 col-md-6">
                <date-picker v-model="form.fecha_hasta" label="Vigencia hasta (opcional)">
                  <template v-slot:prepend>
                    <q-icon name="event" />
                  </template>
                  <template v-slot:hint> Dejar vacío para vigencia indefinida </template>
                </date-picker>
              </div>

              <div class="col-12 col-md-6">
                <q-toggle v-model="form.activo" label="Activo" color="primary" />
              </div>

              <div class="col-12">
                <q-input
                  v-model="form.observaciones"
                  label="Observaciones"
                  type="textarea"
                  outlined
                  dense
                  rows="3"
                  hint="Motivo del precio especial o notas adicionales"
                />
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
            @click="savePrecio"
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
import DatePicker from 'src/components/DatePicker.vue'
import { formatDateOnly as formatDate, todayInLima } from 'src/utils/date'

const $q = useQuasar()
const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const precios = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)

const filters = ref({
  adicional: null,
  cliente: null,
  activo: null,
})

const estadoOptions = [
  { label: 'Activo', value: true },
  { label: 'Inactivo', value: false },
]

const form = ref({
  adicional: null,
  cliente: null,
  precio: 0,
  fecha_desde: todayInLima(),
  fecha_hasta: null,
  activo: true,
  observaciones: '',
})

const columns = [
  {
    name: 'adicional_nombre',
    label: 'Adicional',
    field: 'adicional_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'cliente_nombre',
    label: 'Agencia',
    field: 'cliente_nombre',
    align: 'left',
    sortable: true,
  },
  {
    name: 'precio',
    label: 'Precio Especial',
    field: 'precio',
    align: 'right',
    sortable: true,
  },
  {
    name: 'vigencia',
    label: 'Vigencia',
    field: 'fecha_desde',
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
  sortBy: 'fecha_desde',
  descending: true,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadPrecios = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = {
      page,
      page_size: rowsPerPage,
      ordering: (descending ? '-' : '') + sortBy,
    }

    if (filters.value.adicional) {
      params.adicional = filters.value.adicional?.id || filters.value.adicional
    }
    if (filters.value.cliente) {
      params.cliente = filters.value.cliente?.id || filters.value.cliente
    }
    if (filters.value.activo !== null && filters.value.activo !== undefined) {
      params.activo = filters.value.activo
    }

    const response = await api.get('base/adicional-precios-especiales/', { params })
    precios.value = response.data.results || []
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count || 0,
    }
  } catch (error) {
    notifyError('Error al cargar precios especiales')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const onRequest = (props) => loadPrecios(props)

const openDialog = (precio = null) => {
  if (precio) {
    isEditing.value = true
    form.value = {
      id: precio.id,
      adicional: precio.adicional || { id: precio.adicional, nombre: precio.adicional_nombre },
      cliente: precio.cliente || { id: precio.cliente, nombre: precio.cliente_nombre },
      precio: parseFloat(precio.precio),
      fecha_desde: precio.fecha_desde,
      fecha_hasta: precio.fecha_hasta,
      activo: precio.activo,
      observaciones: precio.observaciones || '',
    }
  } else {
    isEditing.value = false
    form.value = {
      adicional: null,
      cliente: null,
      precio: 0,
      fecha_desde: todayInLima(),
      fecha_hasta: null,
      activo: true,
      observaciones: '',
    }
  }
  showDialog.value = true
}

const savePrecio = async () => {
  saving.value = true
  try {
    const payload = {
      adicional: form.value.adicional?.id || form.value.adicional,
      cliente: form.value.cliente?.id || form.value.cliente,
      precio: form.value.precio,
      fecha_desde: form.value.fecha_desde,
      fecha_hasta: form.value.fecha_hasta || null,
      activo: form.value.activo,
      observaciones: form.value.observaciones,
    }

    if (isEditing.value) {
      await api.put(`base/adicional-precios-especiales/${form.value.id}/`, payload)
      notifySuccess('Precio especial actualizado correctamente')
    } else {
      await api.post('base/adicional-precios-especiales/', payload)
      notifySuccess('Precio especial creado correctamente')
    }

    showDialog.value = false
    loadPrecios()
  } catch (error) {
    notifyError('Error al guardar el precio especial')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const deletePrecio = async (precio) => {
  if (
    !(await confirm(
      `¿Eliminar el precio especial de ${precio.adicional_nombre} para ${precio.cliente_nombre}?`,
    ))
  )
    return

  try {
    await api.delete(`base/adicional-precios-especiales/${precio.id}/`)
    notifySuccess('Precio especial eliminado')
    loadPrecios()
  } catch {
    notifyError('Error al eliminar')
  }
}

onMounted(() => {
  loadPrecios()
})
</script>
