<template>
  <div class="flex flex-center bg-grey-2 full-height">
    <q-card class="login-card q-pa-md">
      <q-card-section class="text-center">
        <div class="text-h4 text-weight-bold text-primary q-mb-md">365 Viajes</div>
        <div class="text-subtitle1 text-grey-7">Sistema de Reservas</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="handleLogin" class="q-gutter-md">
          <q-input
            v-model="username"
            filled
            label="Usuario"
            placeholder="Ingrese su usuario"
            :rules="[(val) => !!val || 'El usuario es requerido']"
            lazy-rules
            autofocus
          >
            <template v-slot:prepend>
              <q-icon name="person" />
            </template>
          </q-input>

          <q-input
            v-model="password"
            filled
            :type="showPassword ? 'text' : 'password'"
            label="Contraseña"
            placeholder="Ingrese su contraseña"
            :rules="[(val) => !!val || 'La contraseña es requerida']"
            lazy-rules
            @keyup.enter="handleLogin"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>

          <div>
            <q-btn
              type="submit"
              color="primary"
              label="Iniciar Sesión"
              class="full-width"
              :loading="loading"
              :disable="loading"
            />
          </div>
        </q-form>
      </q-card-section>

      <q-card-section class="text-center text-caption text-grey-6">
        © {{ currentYear }} - Todos los derechos reservados
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'
import { useNotify } from 'src/composables/useNotify'

const router = useRouter()
const { login } = useAuth()
const { notifyError } = useNotify()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)

const currentYear = new Date().getFullYear()

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
</script>

<style scoped>
.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.full-height {
  min-height: 100vh;
  width: 100vw;
}

.bg-grey-2 {
  background-color: #f5f5f5;
}
</style>
