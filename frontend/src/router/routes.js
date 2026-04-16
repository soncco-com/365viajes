const routes = [
  // Ruta de login (pública)
  {
    path: '/login',
    name: 'login',
    component: () => import('pages/LoginPage.vue'),
    meta: { requiresAuth: false },
  },

  // Rutas protegidas
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('pages/IndexPage.vue'),
      },

      // Módulo de Reservas
      {
        path: '/reservas',
        name: 'reservas-list',
        component: () => import('pages/reservas/ReservasListPage.vue'),
      },
      {
        path: '/reservas/crear',
        name: 'reservas-create',
        component: () => import('pages/reservas/ReservaCreatePage.vue'),
      },
      {
        path: '/reservas/:id/editar',
        name: 'reservas-edit',
        component: () => import('pages/reservas/ReservaEditPage.vue'),
      },
      {
        path: '/reservas/:id/historial',
        name: 'reservas-historial',
        component: () => import('pages/reservas/ReservaHistorialPage.vue'),
        meta: { requiresAdmin: true },
      },

      // Módulo de Informes
      {
        path: '/informes/servicio-agencias',
        name: 'informe-servicio-agencias',
        component: () => import('pages/informes/ServicioAgenciasPage.vue'),
      },
      {
        path: '/informes/biblia-digital',
        name: 'informe-biblia-digital',
        component: () => import('pages/informes/BibliaDigitalPage.vue'),
      },
      {
        path: '/informes/adicionales',
        name: 'informe-adicionales',
        component: () => import('pages/informes/AdicionalesPage.vue'),
      },
      {
        path: '/informes/ordenes-servicio',
        name: 'informe-ordenes-servicio',
        component: () => import('pages/informes/OrdenesServicioPage.vue'),
      },
      {
        path: '/informes/ordenes-servicio/:id',
        name: 'informe-orden-servicio-detalle',
        component: () => import('pages/informes/OrdenServicioDetailPage.vue'),
      },
      {
        path: '/informes/rendicion-ventas',
        name: 'informe-rendicion-ventas',
        component: () => import('pages/informes/RendicionVentasPage.vue'),
        meta: { requiresAdmin: true },
      },

      // Módulo de Gastos
      {
        path: '/gastos',
        name: 'gastos',
        component: () => import('pages/gastos/GastosPage.vue'),
      },

      // Módulo de Administración
      {
        path: '/admin/usuarios',
        name: 'admin-usuarios',
        component: () => import('pages/admin/UsuariosPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/adicionales',
        name: 'admin-adicionales',
        component: () => import('pages/admin/AdicionalesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/clientes',
        name: 'admin-clientes',
        component: () => import('pages/admin/ClientesPage.vue'),
      },
      {
        path: '/admin/guias',
        name: 'admin-guias',
        component: () => import('pages/admin/GuiasPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/choferes',
        name: 'admin-choferes',
        component: () => import('pages/admin/ChoferesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/responsables',
        name: 'admin-responsables',
        component: () => import('pages/admin/ResponsablesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/lugares',
        name: 'admin-lugares',
        component: () => import('pages/admin/LugaresPage.vue'),
      },
      {
        path: '/admin/servicios',
        name: 'admin-servicios',
        component: () => import('pages/admin/ServiciosPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/precios-especiales',
        name: 'admin-precios-especiales',
        component: () => import('pages/admin/PreciosEspecialesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/precios-especiales-adicionales',
        name: 'admin-precios-especiales-adicionales',
        component: () => import('pages/admin/PreciosEspecialesAdicionalesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/servicio-paradas',
        name: 'admin-servicio-paradas',
        component: () => import('pages/admin/ServicioParadasPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/orden-servicio-columnas',
        name: 'admin-orden-servicio-columnas',
        component: () => import('pages/admin/OrdenServicioColumnasPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: '/admin/horarios',
        name: 'admin-horarios',
        component: () => import('pages/admin/HorariosPage.vue'),
        meta: { requiresAdmin: true },
      },

      // Configuraciones del Sistema
      {
        path: '/admin/configuraciones',
        name: 'admin-configuraciones',
        component: () => import('pages/admin/ConfiguracionesPage.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
