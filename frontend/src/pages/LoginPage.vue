<template>
  <div class="login-container">
    <div class="login-background"></div>
    <div class="login-content">
      <q-card class="login-card">
        <!-- Logo y título -->
        <q-card-section class="text-center q-pt-xl q-pb-lg">
          <div v-if="logoUrl" class="logo-container q-mb-md">
            <img :src="logoUrl" alt="Logo" class="logo-image" />
          </div>
          <div v-else class="q-mb-md">
            <q-icon name="tour" size="80px" color="deep-orange-8" />
          </div>
          <div class="text-h4 text-weight-bold text-deep-orange-8 q-mb-xs">365 Viajes</div>
          <div class="text-subtitle1 text-grey-7">Sistema de Reservas</div>
        </q-card-section>

        <!-- Formulario -->
        <q-card-section class="q-px-xl q-pb-xl">
          <q-form @submit="handleLogin" class="q-gutter-md">
            <q-input
              v-model="username"
              outlined
              label="Usuario"
              placeholder="Ingrese su usuario"
              :rules="[(val) => !!val || 'El usuario es requerido']"
              lazy-rules
              autofocus
              color="deep-orange-8"
            >
              <template v-slot:prepend>
                <q-icon name="person" color="deep-orange-8" />
              </template>
            </q-input>

            <q-input
              v-model="password"
              outlined
              :type="showPassword ? 'text' : 'password'"
              label="Contraseña"
              placeholder="Ingrese su contraseña"
              :rules="[(val) => !!val || 'La contraseña es requerida']"
              lazy-rules
              color="deep-orange-8"
              @keyup.enter="handleLogin"
            >
              <template v-slot:prepend>
                <q-icon name="lock" color="deep-orange-8" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  color="deep-orange-8"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>

            <div class="q-mt-lg">
              <q-btn
                type="submit"
                color="deep-orange-8"
                label="Iniciar Sesión"
                class="full-width"
                size="lg"
                unelevated
                :loading="loading"
                :disable="loading"
              />
            </div>
          </q-form>
        </q-card-section>

        <!-- Footer -->
        <q-card-section class="text-center text-caption text-grey-6 q-py-md bg-grey-2">
          © {{ currentYear }} - Todos los derechos reservados
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'
import { useNotify } from 'src/composables/useNotify'
import axios from 'axios'

const router = useRouter()
const { login } = useAuth()
const { notifyError } = useNotify()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const logoUrl = ref('')

const currentYear = new Date().getFullYear()

const loadLogo = async () => {
  try {
    // Usar axios directamente ya que no tenemos token en el login
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/base/opciones-generales/logo/`,
    )
    if (response.data.valor) {
      logoUrl.value = response.data.valor
    }
  } catch {
    // No hacer nada si no hay logo configurado
  }
}

const handleLogin = async () => {
  if (!username.value || !password.value) {
    notifyError('Por favor complete todos los campos')
    return
  }

  loading.value = true

  try {
    await login(username.value, password.value)
    router.push('/')
  } catch (error) {
    notifyError(error.message || 'Error al iniciar sesión')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogo()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #bf360c 0%, #d84315 50%, #ff5722 100%);
  z-index: 0;
}

.login-background::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: backgroundMove 20s linear infinite;
}

@keyframes backgroundMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.login-content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px;
  padding: 20px;
}

.login-card {
  width: 100%;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  background: white;
}

.logo-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo-image {
  max-width: 120px;
  max-height: 120px;
  object-fit: contain;
}

.full-width {
  width: 100%;
}
</style>
