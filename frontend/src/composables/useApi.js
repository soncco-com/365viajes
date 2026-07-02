/**
 * Composable para realizar llamadas a la API
 * Incluye interceptores para JWT y manejo de errores
 */
import axios from 'axios'
import { useAuth } from './useAuth'
import { Notify } from 'quasar'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Crear instancia de axios
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const normalizeApiUrl = (url) => {
  if (!url || /^https?:\/\//i.test(url)) {
    return url
  }

  const [pathWithQuery, hash = ''] = url.split('#')
  const [path, query = ''] = pathWithQuery.split('?')

  if (!path || path.endsWith('/')) {
    return url
  }

  return `${path}/${query ? `?${query}` : ''}${hash ? `#${hash}` : ''}`
}

// Interceptor de request para agregar token
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuth()
    config.url = normalizeApiUrl(config.url)
    if (accessToken.value) {
      config.headers.Authorization = `Bearer ${accessToken.value}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Interceptor de response para manejar errores y refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Si es error 401 y no hemos intentado refrescar
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const { refreshAccessToken } = useAuth()
      const refreshed = await refreshAccessToken()

      if (refreshed) {
        // Reintentar request original con nuevo token
        const { accessToken } = useAuth()
        originalRequest.headers.Authorization = `Bearer ${accessToken.value}`
        return apiClient(originalRequest)
      }
    }

    // Mostrar notificación de error
    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Error en la petición'

    Notify.create({
      type: 'negative',
      message: errorMessage,
      position: 'top',
    })

    return Promise.reject(error)
  },
)

export function useApi() {
  /**
   * GET request
   */
  const get = async (url, config = {}) => {
    try {
      const response = await apiClient.get(url, config)
      return { data: response.data, success: true }
    } catch (error) {
      return { data: null, success: false, error }
    }
  }

  /**
   * POST request
   */
  const post = async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.post(url, data, config)
      return { data: response.data, success: true }
    } catch (error) {
      return { data: null, success: false, error }
    }
  }

  /**
   * PUT request
   */
  const put = async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.put(url, data, config)
      return { data: response.data, success: true }
    } catch (error) {
      return { data: null, success: false, error }
    }
  }

  /**
   * PATCH request
   */
  const patch = async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.patch(url, data, config)
      return { data: response.data, success: true }
    } catch (error) {
      return { data: null, success: false, error }
    }
  }

  /**
   * DELETE request
   */
  const del = async (url, config = {}) => {
    try {
      const response = await apiClient.delete(url, config)
      return { data: response.data, success: true }
    } catch (error) {
      return { data: null, success: false, error }
    }
  }

  /**
   * Descargar archivo
   */
  const download = async (url, filename = 'archivo.pdf') => {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob',
      })

      const blob = new Blob([response.data], {
        type: response.headers['content-type'],
      })
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = filename
      link.click()
      window.URL.revokeObjectURL(link.href)

      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  /**
   * Obtener PDF como blob para visualización
   */
  const getPdf = async (url) => {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob',
      })

      return {
        data: new Blob([response.data], { type: 'application/pdf' }),
        success: true,
      }
    } catch (error) {
      return { data: null, success: false, error }
    }
  }

  return {
    get,
    post,
    put,
    patch,
    delete: del,
    download,
    getPdf,
    apiClient, // Exportar cliente para usos especiales
  }
}
