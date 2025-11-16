<template>
  <q-page padding>
    <page-title title="Configuraciones del Sistema" icon="tune" />

    <!-- Tabla de configuraciones -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row items-center q-mb-md">
          <div class="col">
            <div class="text-h6">Opciones Generales</div>
            <div class="text-caption text-grey-7">Configuraciones globales del sistema</div>
          </div>
        </div>

        <q-list bordered separator>
          <q-item v-for="config in configuraciones" :key="config.id" class="q-pa-md">
            <q-item-section>
              <q-item-label class="text-weight-medium">{{ config.clave }}</q-item-label>
              <q-item-label caption class="text-grey-7">
                {{ config.descripcion || 'Sin descripción' }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <div class="row items-center q-gutter-sm" style="min-width: 300px">
                <q-input
                  v-model="config.valor"
                  dense
                  outlined
                  class="col"
                  :disable="saving === config.id"
                />
                <q-btn
                  icon="save"
                  color="primary"
                  flat
                  round
                  dense
                  :disable="saving === config.id"
                  :loading="saving === config.id"
                  @click="guardarConfiguracion(config)"
                >
                  <q-tooltip>Guardar</q-tooltip>
                </q-btn>
              </div>
            </q-item-section>
          </q-item>

          <q-item v-if="configuraciones.length === 0" class="text-center text-grey-7 q-pa-lg">
            <q-item-section>
              <div class="text-body1">No hay configuraciones disponibles</div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>

      <q-card-section v-if="loading" class="text-center">
        <q-spinner color="primary" size="50px" />
      </q-card-section>
    </q-card>

    <!-- Card de información -->
    <q-card class="q-mt-md bg-blue-1">
      <q-card-section>
        <div class="row items-center q-gutter-sm">
          <q-icon name="info" color="blue" size="24px" />
          <div class="col">
            <div class="text-body2 text-weight-medium">Información</div>
            <div class="text-caption text-grey-8">
              Las configuraciones se guardan automáticamente al hacer clic en el botón guardar.
              Estos valores afectan el comportamiento global del sistema.
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'

const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const configuraciones = ref([])
const loading = ref(false)
const saving = ref(null)

const loadConfiguraciones = async () => {
  loading.value = true
  try {
    // Agregar timestamp para evitar caché
    const response = await api.get('base/opciones-generales/', {
      params: { _t: Date.now() },
    })
    configuraciones.value = response.data.results || response.data
  } catch (error) {
    notifyError('Error al cargar las configuraciones')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const guardarConfiguracion = async (config) => {
  saving.value = config.id
  try {
    await api.put(`base/opciones-generales/${config.id}/`, {
      clave: config.clave,
      valor: config.valor,
      descripcion: config.descripcion,
    })
    notifySuccess('Configuración guardada correctamente')

    // Recargar configuraciones después de guardar para obtener datos frescos
    await loadConfiguraciones()
  } catch (error) {
    notifyError('Error al guardar la configuración')
    console.error(error)
  } finally {
    saving.value = null
  }
}

onMounted(() => {
  loadConfiguraciones()
})
</script>
