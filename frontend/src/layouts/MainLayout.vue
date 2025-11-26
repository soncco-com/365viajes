<template>
  <q-layout view="hHh lpR fFf">
    <!-- Header no fijo con navegación -->
    <q-header class="bg-deep-orange-8 text-white">
      <q-toolbar>
        <!-- Botón menú hamburguesa (solo móvil) -->
        <q-btn
          v-if="isAuthenticated && $q.screen.lt.md"
          flat
          dense
          round
          icon="menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <!-- Logo y título -->
        <div class="row items-center q-gutter-sm cursor-pointer" @click="goToDashboard">
          <img
            v-if="logoUrl"
            :src="logoUrl"
            alt="Logo"
            style="height: 40px; max-width: 150px; object-fit: contain"
          />
          <q-toolbar-title class="text-weight-bold"> 365 Viajes </q-toolbar-title>
        </div>

        <q-space />

        <!-- Menú de navegación (solo desktop) -->
        <q-tabs v-if="isAuthenticated && $q.screen.gt.sm" inline-label shrink>
          <!-- Reservas con dropdown -->
          <q-btn-dropdown flat label="Reservas" icon="event_note" dropdown-icon="expand_more">
            <q-list>
              <q-item clickable v-close-popup to="/reservas/crear">
                <q-item-section avatar>
                  <q-icon name="add_circle" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Crear Reserva</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/reservas">
                <q-item-section avatar>
                  <q-icon name="list" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Ver Reservas</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>

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
            <q-list style="min-width: 200px">
              <!-- Catálogos -->
              <q-item-label header class="text-weight-bold text-grey-8">
                <q-icon name="folder" size="18px" class="q-mr-xs" /> Catálogos
              </q-item-label>
              <q-item clickable v-close-popup to="/admin/clientes" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="business" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Agencias</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/lugares" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="hotel" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Hoteles</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/adicionales" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="add_box" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Adicionales</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/horarios" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="schedule" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Horarios</q-item-label>
                </q-item-section>
              </q-item>

              <q-separator spaced />

              <!-- Servicios -->
              <q-item-label header class="text-weight-bold text-grey-8">
                <q-icon name="tour" size="18px" class="q-mr-xs" /> Servicios
              </q-item-label>
              <q-item clickable v-close-popup to="/admin/servicios" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="tour" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Servicios</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/precios-especiales" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="local_offer" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Precios Especiales</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/servicio-paradas" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="map" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Paradas de Servicios</q-item-label>
                </q-item-section>
              </q-item>

              <q-separator spaced />

              <!-- Personal -->
              <q-item-label header class="text-weight-bold text-grey-8">
                <q-icon name="group" size="18px" class="q-mr-xs" /> Personal
              </q-item-label>
              <q-item clickable v-close-popup to="/admin/guias" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="badge" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Guías</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/choferes" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="directions_bus" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Transportes</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/responsables" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="person_pin" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Responsables</q-item-label>
                </q-item-section>
              </q-item>

              <q-separator spaced />

              <!-- Sistema -->
              <q-item-label header class="text-weight-bold text-grey-8">
                <q-icon name="settings_applications" size="18px" class="q-mr-xs" /> Sistema
              </q-item-label>
              <q-item clickable v-close-popup to="/admin/usuarios" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="person" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Usuarios</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/configuraciones" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="tune" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Configuraciones</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/admin/auditoria" class="q-pl-md">
                <q-item-section avatar>
                  <q-icon name="history" size="20px" />
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

    <!-- Drawer para móviles -->
    <q-drawer v-if="isAuthenticated" v-model="leftDrawerOpen" side="left" bordered>
      <q-scroll-area class="fit">
        <q-list padding>
          <!-- Usuario -->
          <q-item>
            <q-item-section avatar>
              <q-icon name="account_circle" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-bold">{{ userName }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator spaced />

          <!-- Reservas -->
          <q-expansion-item expand-separator icon="event_note" label="Reservas">
            <q-item
              clickable
              v-ripple
              to="/reservas/crear"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="add_circle" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Crear Reserva</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/reservas"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="list" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Ver Reservas</q-item-label>
              </q-item-section>
            </q-item>
          </q-expansion-item>

          <!-- Informes -->
          <q-expansion-item expand-separator icon="assessment" label="Informes">
            <q-item
              clickable
              v-ripple
              to="/informes/biblia-digital"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="book" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Biblia Digital</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/informes/servicio-agencias"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="business" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Servicio por Agencias</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/informes/adicionales"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="add_circle" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Adicionales</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/informes/ordenes-servicio"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="list_alt" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Órdenes de Servicio</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              v-if="isAdmin"
              clickable
              v-ripple
              to="/informes/rendicion-ventas"
              @click="leftDrawerOpen = false"
              class="q-pl-lg"
            >
              <q-item-section avatar>
                <q-icon name="account_balance" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Rendición de Ventas</q-item-label>
              </q-item-section>
            </q-item>
          </q-expansion-item>

          <!-- Gastos -->
          <q-item clickable v-ripple to="/gastos" @click="leftDrawerOpen = false">
            <q-item-section avatar>
              <q-icon name="attach_money" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Gastos</q-item-label>
            </q-item-section>
          </q-item>

          <!-- Administración (solo admin) -->
          <q-expansion-item v-if="isAdmin" expand-separator icon="settings" label="Administración">
            <!-- Catálogos -->
            <q-item-label header class="q-pl-lg text-weight-bold text-grey-8">
              Catálogos
            </q-item-label>
            <q-item
              clickable
              v-ripple
              to="/admin/clientes"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="business" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Agencias</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/lugares"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="hotel" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Hoteles</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/adicionales"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="add_box" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Adicionales</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/horarios"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="schedule" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Horarios</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Servicios -->
            <q-item-label header class="q-pl-lg text-weight-bold text-grey-8">
              Servicios
            </q-item-label>
            <q-item
              clickable
              v-ripple
              to="/admin/servicios"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="tour" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Servicios</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/precios-especiales"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="local_offer" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Precios Especiales</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/servicio-paradas"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="map" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Paradas de Servicios</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Personal -->
            <q-item-label header class="q-pl-lg text-weight-bold text-grey-8">
              Personal
            </q-item-label>
            <q-item
              clickable
              v-ripple
              to="/admin/guias"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="badge" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Guías</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/choferes"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="directions_bus" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Transportes</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/responsables"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="person_pin" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Responsables</q-item-label>
              </q-item-section>
            </q-item>

            <!-- Sistema -->
            <q-item-label header class="q-pl-lg text-weight-bold text-grey-8">
              Sistema
            </q-item-label>
            <q-item
              clickable
              v-ripple
              to="/admin/usuarios"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="person" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Usuarios</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/configuraciones"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="tune" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Configuraciones</q-item-label>
              </q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              to="/admin/auditoria"
              @click="leftDrawerOpen = false"
              class="q-pl-xl"
            >
              <q-item-section avatar>
                <q-icon name="history" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Auditoría</q-item-label>
              </q-item-section>
            </q-item>
          </q-expansion-item>

          <q-separator spaced />

          <!-- Cerrar sesión -->
          <q-item clickable v-ripple @click="handleLogout">
            <q-item-section avatar>
              <q-icon name="logout" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Cerrar Sesión</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from 'src/composables/useAuth'
import { useApi } from 'src/composables/useApi'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const router = useRouter()
const api = useApi()
const { isAuthenticated, currentUser, logout, isAdmin: adminRole } = useAuth()

const leftDrawerOpen = ref(false)
const logoUrl = ref('')
const currentYear = new Date().getFullYear()

const userName = computed(() => {
  if (!currentUser.value) return 'Usuario'
  return currentUser.value.username || currentUser.value.first_name || 'Usuario'
})

const isAdmin = computed(() => {
  return adminRole.value
})

const loadLogo = async () => {
  try {
    const response = await api.get('base/opciones-generales/logo/')
    if (response.data.valor) {
      logoUrl.value = response.data.valor
    }
  } catch {
    // No hacer nada si no hay logo configurado
  }
}

const goToDashboard = () => {
  router.push('/')
}

onMounted(() => {
  if (isAuthenticated.value) {
    loadLogo()
  }
})

const handleLogout = async () => {
  await logout()
  leftDrawerOpen.value = false
  router.push('/login')
}
</script>

<style scoped>
/* Estilos personalizados si son necesarios */
</style>
