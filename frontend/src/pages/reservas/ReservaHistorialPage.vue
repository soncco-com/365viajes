<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <q-btn flat dense round icon="arrow_back" @click="$router.back()" class="q-mr-md" />
      <page-title
        title="Historial de Cambios"
        :subtitle="
          reserva
            ? `Reserva ${reserva.reserva_numero || 'S/N'} - ${reserva.pasajero}`
            : 'Cargando...'
        "
      />
    </div>

    <q-card v-if="reserva" class="q-mb-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-3">
            <div class="text-grey-7 text-caption">Número</div>
            <div class="text-body1 text-weight-medium">
              {{ reserva.reserva_numero || 'Sin número' }}
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="text-grey-7 text-caption">Pasajero</div>
            <div class="text-body1 text-weight-medium">{{ reserva.pasajero }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-grey-7 text-caption">Total de cambios</div>
            <div class="text-h6 text-primary">{{ reserva.total_cambios }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">Historial de Cambios</div>

        <q-table
          :rows="historial"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          bordered
          :pagination="{ rowsPerPage: 20 }"
        >
          <template v-slot:body-cell-fecha="props">
            <q-td :props="props">
              <div class="text-caption">{{ formatDate(props.row.fecha) }}</div>
              <div class="text-caption text-grey-7">{{ formatTime(props.row.fecha) }}</div>
            </q-td>
          </template>

          <template v-slot:body-cell-accion="props">
            <q-td :props="props">
              <q-badge
                :color="getAccionColor(props.row.accion)"
                :label="props.row.accion_display"
              />
            </q-td>
          </template>

          <template v-slot:body-cell-modelo="props">
            <q-td :props="props">
              <q-chip dense size="sm" :icon="getModeloIcon(props.row.modelo)">
                {{ props.row.modelo }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                round
                icon="visibility"
                color="primary"
                @click="verDetalle(props.row)"
                :disable="!props.row.datos_anteriores && !props.row.datos_nuevos"
              >
                <q-tooltip>Ver detalles</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Dialog para ver detalles del cambio -->
    <q-dialog v-model="showDetalleDialog" maximized>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Detalle del Cambio</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section v-if="cambioSeleccionado">
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-12 col-md-4">
              <div class="text-grey-7">Fecha y Hora</div>
              <div class="text-body1">
                {{ formatDate(cambioSeleccionado.fecha) }}
                {{ formatTime(cambioSeleccionado.fecha) }}
              </div>
            </div>
            <div class="col-12 col-md-4">
              <div class="text-grey-7">Usuario</div>
              <div class="text-body1">{{ cambioSeleccionado.usuario_nombre_completo }}</div>
            </div>
            <div class="col-12 col-md-4">
              <div class="text-grey-7">IP</div>
              <div class="text-body1">{{ cambioSeleccionado.ip_address || 'N/A' }}</div>
            </div>
          </div>

          <div class="row q-col-gutter-md">
            <!-- Datos Anteriores -->
            <div
              class="col-12"
              :class="cambioSeleccionado.datos_anteriores ? 'col-md-6' : 'col-md-12'"
            >
              <q-card flat bordered>
                <q-card-section class="bg-primary text-white">
                  <div class="text-h6">
                    {{ cambioSeleccionado.datos_anteriores ? 'Antes' : 'Datos' }}
                  </div>
                </q-card-section>
                <q-card-section>
                  <div v-if="cambioSeleccionado.datos_nuevos">
                    <div
                      v-for="(value, key) in getFilteredData(cambioSeleccionado.datos_nuevos)"
                      :key="key"
                      class="q-mb-sm"
                    >
                      <div class="row">
                        <div class="col-4 text-grey-7 text-weight-medium">
                          {{ formatKey(key) }}:
                        </div>
                        <div
                          class="col-8"
                          :class="{
                            'text-positive text-weight-bold':
                              !cambioSeleccionado.datos_anteriores ||
                              cambioSeleccionado.datos_anteriores[key] !== value,
                          }"
                        >
                          {{ formatValueWithDisplay(key, value, cambioSeleccionado.datos_nuevos) }}
                        </div>
                      </div>
                      <q-separator class="q-mt-sm" />
                    </div>
                  </div>
                  <div v-else class="text-grey-7 text-center">Sin datos</div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Datos Nuevos (solo si hay datos anteriores) -->
            <div class="col-12 col-md-6" v-if="cambioSeleccionado.datos_anteriores">
              <q-card flat bordered>
                <q-card-section class="bg-positive text-white">
                  <div class="text-h6">Después</div>
                </q-card-section>
                <q-card-section>
                  <div v-if="cambioSeleccionado.datos_anteriores">
                    <div
                      v-for="(value, key) in getFilteredData(cambioSeleccionado.datos_anteriores)"
                      :key="key"
                      class="q-mb-sm"
                    >
                      <div class="row">
                        <div class="col-4 text-grey-7 text-weight-medium">
                          {{ formatKey(key) }}:
                        </div>
                        <div class="col-8">
                          {{
                            formatValueWithDisplay(key, value, cambioSeleccionado.datos_anteriores)
                          }}
                        </div>
                      </div>
                      <q-separator class="q-mt-sm" />
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import { formatDateOnly, formatDateTimeInLima, formatTimeInLima } from 'src/utils/date'

const route = useRoute()
const api = useApi()
const { notifyError } = useNotify()

const reservaId = ref(route.params.id)
const reserva = ref(null)
const historial = ref([])
const loading = ref(false)
const showDetalleDialog = ref(false)
const cambioSeleccionado = ref(null)

const columns = [
  {
    name: 'fecha',
    label: 'Fecha/Hora',
    field: 'fecha',
    align: 'left',
    sortable: true,
  },
  {
    name: 'usuario',
    label: 'Usuario',
    field: 'usuario_nombre_completo',
    align: 'left',
    sortable: true,
  },
  {
    name: 'accion',
    label: 'Acción',
    field: 'accion_display',
    align: 'center',
    sortable: true,
  },
  {
    name: 'modelo',
    label: 'Tipo',
    field: 'modelo',
    align: 'center',
    sortable: true,
  },
  {
    name: 'ip',
    label: 'IP',
    field: 'ip_address',
    align: 'left',
  },
  {
    name: 'actions',
    label: 'Acciones',
    field: 'actions',
    align: 'center',
  },
]

const loadHistorial = async () => {
  loading.value = true
  try {
    const response = await api.get(`reservas/reservas/${reservaId.value}/historial/`)
    reserva.value = response.data
    historial.value = response.data.historial
  } catch (error) {
    notifyError('Error al cargar el historial')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return formatDateTimeInLima(dateString, { dateOnly: true, fallback: '-' })
}

const formatTime = (dateString) => {
  return formatTimeInLima(dateString, { fallback: '-' })
}

const getAccionColor = (accion) => {
  const colors = {
    C: 'positive',
    E: 'warning',
    D: 'negative',
  }
  return colors[accion] || 'grey'
}

const getModeloIcon = (modelo) => {
  const icons = {
    Reserva: 'receipt',
    Reservadetalle: 'list_alt',
    Reservaadicionaldetalle: 'add_circle',
  }
  return icons[modelo] || 'description'
}

const formatKey = (key) => {
  // Convertir snake_case a Title Case
  return key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const getFilteredData = (data) => {
  // Filtrar campos auxiliares (_display, _nombre, _username, _str)
  // Solo mostrar los campos base
  const filtered = {}
  for (const key in data) {
    if (
      !key.endsWith('_display') &&
      !key.endsWith('_nombre') &&
      !key.endsWith('_username') &&
      !key.endsWith('_str')
    ) {
      filtered[key] = data[key]
    }
  }
  return filtered
}

const formatValueWithDisplay = (key, value, dataObject) => {
  // Intentar obtener el valor display asociado
  const displayKey = `${key}_display`
  const nombreKey = `${key}_nombre`
  const usernameKey = `${key}_username`
  const strKey = `${key}_str`

  // Priorizar valores legibles
  if (dataObject[displayKey]) {
    return dataObject[displayKey]
  }
  if (dataObject[nombreKey]) {
    return dataObject[nombreKey]
  }
  if (dataObject[usernameKey]) {
    return dataObject[usernameKey]
  }
  if (dataObject[strKey]) {
    return dataObject[strKey]
  }

  // Formatear el valor original
  if (value === null || value === undefined) return 'N/A'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  if (typeof value === 'object') return JSON.stringify(value, null, 2)

  // Para fechas ISO, formatearlas
  if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
    return value.includes('T')
      ? formatDateTimeInLima(value, { fallback: value })
      : formatDateOnly(value, value)
  }

  return String(value)
}

const verDetalle = (cambio) => {
  cambioSeleccionado.value = cambio
  showDetalleDialog.value = true
}

onMounted(() => {
  loadHistorial()
})
</script>

<style scoped>
.q-card {
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.12),
    0 1px 2px rgba(0, 0, 0, 0.24);
}
</style>
