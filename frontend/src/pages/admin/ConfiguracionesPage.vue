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

    <!-- Card de logo del sistema -->
    <q-card class="q-mt-md">
      <q-card-section>
        <div class="row items-center q-mb-md">
          <div class="col">
            <div class="text-h6">Logo del Sistema</div>
            <div class="text-caption text-grey-7">
              Personaliza el logo que se muestra en el login, menú y PDFs
            </div>
          </div>
        </div>

        <div class="row q-gutter-md items-center">
          <div class="col-12 col-md-auto">
            <div class="logo-preview" :class="{ 'has-logo': logoPreview }">
              <img v-if="logoPreview" :src="logoPreview" alt="Logo actual" />
              <div v-else class="no-logo">
                <q-icon name="image" size="48px" color="grey-5" />
                <div class="text-caption text-grey-6 q-mt-sm">Sin logo</div>
              </div>
            </div>
          </div>

          <div class="col">
            <q-file
              v-model="logoFile"
              outlined
              dense
              accept="image/*"
              label="Seleccionar imagen"
              max-file-size="2048000"
              @update:model-value="onLogoSelected"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
            <div class="text-caption text-grey-7 q-mt-xs">
              Formatos permitidos: JPG, PNG, SVG. Tamaño máximo: 2MB
            </div>
            <div class="q-mt-md">
              <q-btn
                color="primary"
                label="Guardar Logo"
                icon="save"
                :disable="!logoFile || savingLogo"
                :loading="savingLogo"
                @click="guardarLogo"
              />
              <q-btn
                v-if="logoPreview"
                flat
                color="negative"
                label="Eliminar Logo"
                icon="delete"
                class="q-ml-sm"
                :disable="savingLogo"
                @click="eliminarLogo"
              />
            </div>
          </div>
        </div>
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
const logoFile = ref(null)
const logoPreview = ref('')
const savingLogo = ref(false)

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

const loadLogo = async () => {
  try {
    const response = await api.get('base/opciones-generales/logo/')
    if (response.data.valor) {
      logoPreview.value = response.data.valor
    }
  } catch {
    // No hacer nada si no hay logo
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

const onLogoSelected = (file) => {
  if (!file) {
    logoPreview.value = ''
    return
  }

  // Crear preview
  const reader = new FileReader()
  reader.onload = (e) => {
    logoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const guardarLogo = async () => {
  if (!logoFile.value) return

  savingLogo.value = true
  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        await api.post('base/opciones-generales/logo/', {
          logo: e.target.result,
        })
        notifySuccess('Logo guardado correctamente')
        logoFile.value = null
        await loadLogo()
      } catch (error) {
        notifyError('Error al guardar el logo')
        console.error(error)
      } finally {
        savingLogo.value = false
      }
    }
    reader.readAsDataURL(logoFile.value)
  } catch (error) {
    notifyError('Error al procesar el logo')
    console.error(error)
    savingLogo.value = false
  }
}

const eliminarLogo = async () => {
  savingLogo.value = true
  try {
    await api.post('base/opciones-generales/logo/', {
      logo: '',
    })
    notifySuccess('Logo eliminado correctamente')
    logoPreview.value = ''
    logoFile.value = null
  } catch (error) {
    notifyError('Error al eliminar el logo')
    console.error(error)
  } finally {
    savingLogo.value = false
  }
}

onMounted(() => {
  loadConfiguraciones()
  loadLogo()
})
</script>

<style scoped>
.logo-preview {
  width: 150px;
  height: 150px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  overflow: hidden;
}

.logo-preview.has-logo {
  border-style: solid;
  border-color: #4caf50;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-logo {
  text-align: center;
}
</style>
