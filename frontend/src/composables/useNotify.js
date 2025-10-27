/**
 * Composable para sistema centralizado de notificaciones
 */
import { Notify, Dialog, Loading } from 'quasar'

export function useNotify() {
  /**
   * Notificación de éxito
   */
  const success = (message, options = {}) => {
    Notify.create({
      type: 'positive',
      message,
      position: 'top',
      timeout: 2500,
      ...options,
    })
  }

  /**
   * Notificación de error
   */
  const error = (message, options = {}) => {
    Notify.create({
      type: 'negative',
      message,
      position: 'top',
      timeout: 3500,
      ...options,
    })
  }

  /**
   * Notificación de advertencia
   */
  const warning = (message, options = {}) => {
    Notify.create({
      type: 'warning',
      message,
      position: 'top',
      timeout: 3000,
      ...options,
    })
  }

  /**
   * Notificación informativa
   */
  const info = (message, options = {}) => {
    Notify.create({
      type: 'info',
      message,
      position: 'top',
      timeout: 2500,
      ...options,
    })
  }

  /**
   * Diálogo de confirmación
   */
  const confirm = (message, title = 'Confirmar') => {
    return new Promise((resolve) => {
      Dialog.create({
        title,
        message,
        cancel: {
          label: 'Cancelar',
          color: 'negative',
          flat: true,
        },
        ok: {
          label: 'Aceptar',
          color: 'primary',
        },
        persistent: false,
      })
        .onOk(() => resolve(true))
        .onCancel(() => resolve(false))
        .onDismiss(() => resolve(false))
    })
  }

  /**
   * Diálogo de alerta
   */
  const alert = (message, title = 'Atención') => {
    return Dialog.create({
      title,
      message,
      ok: {
        label: 'Aceptar',
        color: 'primary',
      },
    })
  }

  /**
   * Mostrar loading
   */
  const showLoading = (message = 'Cargando...') => {
    Loading.show({
      message,
      spinnerColor: 'primary',
    })
  }

  /**
   * Ocultar loading
   */
  const hideLoading = () => {
    Loading.hide()
  }

  return {
    notifySuccess: success,
    notifyError: error,
    notifyWarning: warning,
    notifyInfo: info,
    success,
    error,
    warning,
    info,
    confirm,
    alert,
    showLoading,
    hideLoading,
  }
}
