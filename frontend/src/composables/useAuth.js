/**
 * Composable para manejo de autenticación JWT
 */
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Estado global de autenticación
const accessToken = ref(localStorage.getItem('access_token') || null)
const refreshToken = ref(localStorage.getItem('refresh_token') || null)
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

export function useAuth() {
  const isAuthenticated = computed(() => !!accessToken.value)
  const currentUser = computed(() => user.value)
  const isAdmin = computed(() => {
    return user.value?.grupos?.includes('Administrador') || false
  })

  /**
   * Login con usuario y contraseña
   */
  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_URL}/token/`, {
        username,
        password,
      })

      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh

      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)

      // Obtener datos del usuario
      await fetchUserData()

      return { success: true }
    } catch (error) {
      console.error('Error en login:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al iniciar sesión',
      }
    }
  }

  /**
   * Obtener datos del usuario actual
   */
  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API_URL}/base/usuarios/me/`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      })

      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('Error al obtener datos del usuario:', error)
    }
  }

  /**
   * Refrescar el access token
   */
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      return false
    }

    try {
      const response = await axios.post(`${API_URL}/token/refresh/`, {
        refresh: refreshToken.value,
      })

      accessToken.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
      return true
    } catch (error) {
      console.error('Error al refrescar token:', error)
      logout()
      return false
    }
  }

  /**
   * Cerrar sesión
   */
  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  /**
   * Verificar si el usuario tiene un permiso específico
   */
  const hasPermission = (permission) => {
    if (isAdmin.value) return true

    // Permisos específicos según el rol
    const publicPermissions = [
      'reservas.view',
      'reservas.create',
      'reservas.edit',
      'informes.view',
      'agencias.view',
      'agencias.create',
      'agencias.edit',
      'hoteles.view',
      'gastos.view_own',
    ]

    return publicPermissions.includes(permission)
  }

  return {
    // Estado
    isAuthenticated,
    currentUser,
    isAdmin,
    accessToken,
    refreshToken,

    // Métodos
    login,
    logout,
    fetchUserData,
    refreshAccessToken,
    hasPermission,
  }
}
