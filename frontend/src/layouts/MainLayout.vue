<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header no fijo con navegación -->
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title class="text-weight-bold"> 365 Viajes </q-toolbar-title>

        <!-- Menú de navegación -->
        <q-tabs v-if="isAuthenticated" align="right" inline-label shrink>
          <!-- Reservas -->
          <q-route-tab name="reservas" label="Reservas" icon="event_note" to="/reservas" />

          <!-- Informes con dropdown -->
          <q-btn-dropdown flat label="Informes" icon="assessment" dropdown-icon="expand_more">
            <q-list>
              <q-item clickable v-close-popup to="/informes/biblia-digital">
                <q-item-section avatar>
                  <q-icon name="book" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Biblia Digital</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/informes/servicio-agencias">
                <q-item-section avatar>
                  <q-icon name="business" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Servicio por Agencias</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/informes/adicionales">
                <q-item-section avatar>
                  <q-icon name="add_circle" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Adicionales</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/informes/ordenes-servicio">
                <q-item-section avatar>
                  <q-icon name="list_alt" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Órdenes de Servicio</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/informes/rendicion-ventas" v-if="isAdmin">
                <q-item-section avatar>
                  <q-icon name="account_balance" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Rendición de Ventas</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>

          <!-- Gastos -->
          <q-route-tab name="gastos" label="Gastos" icon="attach_money" to="/gastos" />

          <!-- Administración (solo admin) con dropdown -->
          <q-btn-dropdown
            v-if="isAdmin"
            flat
            label="Administración"
            icon="settings"
            dropdown-icon="expand_more"
          >
            <q-list>
              <q-item clickable v-close-popup to="/admin/usuarios">
                <q-item-section avatar>
                  <q-icon name="person" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Usuarios</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/clientes">
                <q-item-section avatar>
                  <q-icon name="business" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Agencias</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/servicios">
                <q-item-section avatar>
                  <q-icon name="tour" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Servicios</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/lugares">
                <q-item-section avatar>
                  <q-icon name="hotel" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Hoteles</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/guias">
                <q-item-section avatar>
                  <q-icon name="badge" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Guías</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/choferes">
                <q-item-section avatar>
                  <q-icon name="drive_eta" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Choferes</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/transportes">
                <q-item-section avatar>
                  <q-icon name="directions_bus" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Transportes</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/adicionales">
                <q-item-section avatar>
                  <q-icon name="add_box" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Adicionales</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/horarios">
                <q-item-section avatar>
                  <q-icon name="schedule" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Horarios</q-item-label>
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup to="/admin/auditoria">
                <q-item-section avatar>
                  <q-icon name="history" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Auditoría</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>

          <!-- Usuario y logout -->
          <q-btn-dropdown flat :label="userName" icon="account_circle" dropdown-icon="expand_more">
            <q-list>
              <q-item clickable v-close-popup @click="handleLogout">
                <q-item-section avatar>
                  <q-icon name="logout" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Cerrar Sesión</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </q-tabs>
      </q-toolbar>
    </q-header>

    <!-- Contenido principal -->
    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Footer no fijo -->
    <q-footer class="bg-grey-8 text-white">
      <q-toolbar>
        <q-toolbar-title class="text-center">
          <div class="text-caption">365 Viajes - Sistema de Reservas</div>
          <div class="text-caption text-grey-5">
            © {{ currentYear }} - Todos los derechos reservados
          </div>
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'

const router = useRouter()
const { isAuthenticated, currentUser, logout, isAdmin: adminRole } = useAuth()

const currentYear = new Date().getFullYear()

const userName = computed(() => {
  if (!currentUser.value) return 'Usuario'
  return currentUser.value.username || currentUser.value.first_name || 'Usuario'
})

const isAdmin = computed(() => {
  return adminRole.value
})

const handleLogout = async () => {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
/* Estilos personalizados si son necesarios */
</style>
