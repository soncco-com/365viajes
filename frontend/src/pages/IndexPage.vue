<template>
  <q-page class="q-pa-md">
    <page-title title="Inicio" subtitle="Bienvenido al sistema de reservas" />

    <div class="row q-col-gutter-md q-mt-md">
      <!-- Tarjeta de Reservas -->
      <div class="col-12 col-md-4">
        <q-card class="cursor-pointer" @click="$router.push('/reservas')">
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">
              <q-icon name="event_note" size="md" class="q-mr-sm" />
              Reservas
            </div>
          </q-card-section>
          <q-card-section>
            <div class="text-body2 text-grey-7">
              Gestiona las reservas de tours y servicios para las agencias de viajes.
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Tarjeta de Informes -->
      <div class="col-12 col-md-4">
        <q-card class="cursor-pointer" @click="$router.push('/informes/biblia-digital')">
          <q-card-section class="bg-secondary text-white">
            <div class="text-h6">
              <q-icon name="assessment" size="md" class="q-mr-sm" />
              Informes
            </div>
          </q-card-section>
          <q-card-section>
            <div class="text-body2 text-grey-7">
              Consulta reportes como Biblia Digital, servicios por agencia y órdenes de servicio.
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Tarjeta de Gastos -->
      <div class="col-12 col-md-4">
        <q-card class="cursor-pointer" @click="$router.push('/gastos')">
          <q-card-section class="bg-accent text-white">
            <div class="text-h6">
              <q-icon name="attach_money" size="md" class="q-mr-sm" />
              Gastos
            </div>
          </q-card-section>
          <q-card-section>
            <div class="text-body2 text-grey-7">
              Registra y consulta los gastos asociados a las órdenes de servicio.
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Tarjeta de Administración (solo admin) -->
      <div class="col-12 col-md-4" v-if="isAdmin">
        <q-card class="cursor-pointer" @click="$router.push('/admin/clientes')">
          <q-card-section class="bg-grey-8 text-white">
            <div class="text-h6">
              <q-icon name="settings" size="md" class="q-mr-sm" />
              Administración
            </div>
          </q-card-section>
          <q-card-section>
            <div class="text-body2 text-grey-7">
              Gestiona usuarios, catálogos de servicios, hoteles, guías y más.
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Información del usuario -->
    <div class="q-mt-xl text-center">
      <div class="text-h6 text-grey-7">Bienvenido, {{ userName }}</div>
      <div class="text-caption text-grey-6 q-mt-sm">Hoy es {{ currentDate }}</div>
    </div>
  </q-page>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from 'src/composables/useAuth'
import PageTitle from 'src/components/PageTitle.vue'

const { currentUser, hasPermission } = useAuth()

const userName = computed(() => {
  if (!currentUser.value) return 'Usuario'
  return currentUser.value.first_name || currentUser.value.username || 'Usuario'
})

const isAdmin = computed(() => {
  return hasPermission('Administrador')
})

const currentDate = new Date().toLocaleDateString('es-ES', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
})
</script>

<style scoped>
.cursor-pointer {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.cursor-pointer:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}
</style>
