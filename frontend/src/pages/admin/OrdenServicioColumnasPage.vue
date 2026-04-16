<template>
  <q-page class="q-pa-md">
    <page-title
      title="Columnas Orden de Servicio"
      subtitle="Configura las columnas del PDF por servicio — orden, etiqueta, ancho y visibilidad"
    />

    <!-- Selector de Servicio -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row q-col-gutter-md items-end">
          <div class="col-12 col-md-8">
            <autocomplete-input
              v-model="servicioSelected"
              label="Servicio *"
              endpoint="base/servicios/"
              option-label="nombre"
              clearable
              @update:model-value="onServicioChange"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-center q-pa-xl">
      <q-spinner-dots size="40px" color="primary" />
    </div>

    <template v-if="servicioSelected && !loading">
      <!-- Sin columnas configuradas -->
      <q-card v-if="columnas.length === 0" class="q-mt-md">
        <q-card-section class="text-center q-py-xl">
          <q-icon name="view_column" size="60px" color="grey-4" />
          <div class="text-h6 text-grey-6 q-mt-sm">Sin columnas configuradas</div>
          <div class="text-body2 text-grey-5 q-mb-lg">
            Este servicio no tiene columnas configuradas para el PDF de Orden de Servicio.
          </div>
          <q-btn
            color="primary"
            icon="auto_fix_high"
            label="Inicializar columnas por defecto"
            @click="inicializarColumnas"
            :loading="initializing"
            unelevated
          />
        </q-card-section>
      </q-card>

      <!-- Tabla de columnas -->
      <q-card v-else class="q-mt-md">
        <q-card-section>
          <div class="row items-center q-mb-md">
            <div class="text-subtitle1 text-weight-bold">
              Columnas del PDF
              <q-badge
                :color="hasChanges ? 'orange' : 'grey-4'"
                :text-color="hasChanges ? 'white' : 'grey-7'"
                class="q-ml-sm"
              >
                {{ hasChanges ? 'Sin guardar' : 'Guardado' }}
              </q-badge>
            </div>
            <q-space />
            <div class="text-caption text-grey-6 q-mr-md">
              Total ancho:
              <strong :class="totalAncho === 100 ? 'text-positive' : 'text-warning'">
                {{ totalAncho }}%
              </strong>
            </div>
            <q-btn
              color="primary"
              icon="save"
              label="Guardar cambios"
              @click="saveColumnas"
              :loading="saving"
              :disable="!hasChanges"
              unelevated
            />
          </div>

          <q-markup-table flat bordered dense separator="horizontal">
            <thead>
              <tr class="bg-grey-2">
                <th class="text-center" style="width: 110px">Orden</th>
                <th class="text-left" style="width: 140px">Columna</th>
                <th class="text-left">Etiqueta en PDF</th>
                <th class="text-center" style="width: 110px">Ancho (%)</th>
                <th class="text-center" style="width: 80px">Visible</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(col, index) in columnas"
                :key="col.id"
                :class="{ 'bg-grey-1': !col.visible }"
              >
                <!-- Orden + flechas -->
                <td class="text-center q-pa-xs">
                  <div class="row items-center justify-center q-gutter-xs no-wrap">
                    <q-btn
                      flat
                      dense
                      round
                      size="xs"
                      icon="arrow_upward"
                      color="primary"
                      @click="moveCol(index, 'up')"
                      :disable="index === 0"
                    />
                    <q-chip
                      color="primary"
                      text-color="white"
                      size="sm"
                      dense
                      style="min-width: 28px"
                    >
                      {{ col.orden }}
                    </q-chip>
                    <q-btn
                      flat
                      dense
                      round
                      size="xs"
                      icon="arrow_downward"
                      color="primary"
                      @click="moveCol(index, 'down')"
                      :disable="index === columnas.length - 1"
                    />
                  </div>
                </td>

                <!-- Nombre clave -->
                <td>
                  <q-chip
                    size="sm"
                    :color="col.visible ? 'blue-1' : 'grey-2'"
                    text-color="grey-8"
                    dense
                  >
                    {{ col.clave_display }}
                  </q-chip>
                </td>

                <!-- Etiqueta editable -->
                <td class="q-py-xs">
                  <q-input
                    v-model="col.etiqueta"
                    dense
                    outlined
                    :bg-color="col.visible ? 'white' : 'grey-1'"
                    style="min-width: 150px"
                    @update:model-value="markChanged(col)"
                  />
                </td>

                <!-- Ancho editable -->
                <td class="q-py-xs text-center">
                  <q-input
                    v-model.number="col.ancho"
                    type="number"
                    dense
                    outlined
                    min="1"
                    max="100"
                    style="width: 75px; margin: 0 auto"
                    @update:model-value="markChanged(col)"
                  />
                </td>

                <!-- Visible toggle -->
                <td class="text-center">
                  <q-toggle
                    v-model="col.visible"
                    color="primary"
                    @update:model-value="markChanged(col)"
                  />
                </td>
              </tr>
            </tbody>
          </q-markup-table>

          <div class="text-caption text-grey-6 q-mt-sm">
            <q-icon name="info" size="xs" class="q-mr-xs" />
            La suma de anchos de columnas visibles debería ser 100% para un PDF óptimo.
          </div>
        </q-card-section>
      </q-card>
    </template>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const servicioSelected = ref(null)
const columnas = ref([])
const loading = ref(false)
const saving = ref(false)
const initializing = ref(false)
const changedIds = ref(new Set())

const hasChanges = computed(() => changedIds.value.size > 0)
const totalAncho = computed(() => columnas.value.reduce((sum, c) => sum + (c.ancho || 0), 0))

const onServicioChange = async (servicio) => {
  columnas.value = []
  changedIds.value = new Set()
  if (!servicio) return
  await loadColumnas()
}

const loadColumnas = async () => {
  loading.value = true
  try {
    const { data, success } = await api.get('base/orden-servicio-columnas/', {
      params: { servicio: servicioSelected.value.id, page_size: 20 },
    })
    if (success) {
      columnas.value = data.results ?? data
    }
  } catch {
    notifyError('Error al cargar columnas')
  } finally {
    loading.value = false
  }
}

const inicializarColumnas = async () => {
  initializing.value = true
  try {
    const { success } = await api.post('base/orden-servicio-columnas/inicializar/', {
      servicio: servicioSelected.value.id,
    })
    if (success) {
      notifySuccess('Columnas inicializadas correctamente')
      await loadColumnas()
    }
  } catch {
    notifyError('Error al inicializar columnas')
  } finally {
    initializing.value = false
  }
}

const markChanged = (col) => {
  changedIds.value = new Set([...changedIds.value, col.id])
}

const moveCol = (index, direction) => {
  const cols = columnas.value
  const targetIndex = direction === 'up' ? index - 1 : index + 1
  ;[cols[index], cols[targetIndex]] = [cols[targetIndex], cols[index]]
  cols.forEach((c, i) => {
    c.orden = i + 1
    changedIds.value = new Set([...changedIds.value, c.id])
  })
}

const saveColumnas = async () => {
  saving.value = true
  try {
    const toSave = columnas.value.filter((c) => changedIds.value.has(c.id))
    const results = await Promise.all(
      toSave.map((c) =>
        api.patch(`base/orden-servicio-columnas/${c.id}/`, {
          etiqueta: c.etiqueta,
          ancho: c.ancho,
          orden: c.orden,
          visible: c.visible,
        }),
      ),
    )
    const allOk = results.every((r) => r.success)
    if (allOk) {
      changedIds.value = new Set()
      notifySuccess('Columnas guardadas correctamente')
    } else {
      notifyError('Algunas columnas no pudieron guardarse')
    }
  } catch {
    notifyError('Error al guardar columnas')
  } finally {
    saving.value = false
  }
}
</script>
