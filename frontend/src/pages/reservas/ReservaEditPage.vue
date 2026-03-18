<template>
  <q-page class="q-pa-md">
    <page-title title="Editar Reserva" :subtitle="`Reserva #${reserva.numero || 'S/N'}`" />

    <q-form @submit.prevent="saveReserva" class="q-mt-md">
      <q-tabs
        v-model="tab"
        dense
        class="bg-grey-2 text-primary"
        active-color="primary"
        indicator-color="primary"
        align="justify"
      >
        <q-tab :name="1" label="Datos Principales" icon="info" />
        <q-tab :name="2" label="Servicios" icon="tour" />
        <q-tab :name="3" label="Adicionales" icon="add_circle" />
        <q-tab :name="4" label="Resumen" icon="check_circle" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated class="q-mt-md">
        <q-tab-panel :name="1">
          <reserva-datos-tab
            :reserva="reserva"
            :estado-options="estadoOptions"
            :tipo-pago-options="tipoPagoOptions"
            :tipo-documento-options="tipoDocumentoOptions"
            @update:fecha="reserva.fecha = $event"
            @update:cliente="reserva.cliente = $event"
            @update:pasajero="reserva.pasajero = $event"
            @update:estado="reserva.estado = $event"
            @update:tipo_pago="reserva.tipo_pago = $event"
            @update:tipo_documento="reserva.tipo_documento = $event"
            @update:observaciones="reserva.observaciones = $event"
            @open-cliente-dialog="openClienteDialog"
          />
        </q-tab-panel>

        <q-tab-panel :name="2">
          <reserva-servicios-tab
            :detalles="reserva.detalles"
            :idioma-options="idiomaOptions"
            :subtotal="subtotalServicios"
            @add-servicio="addServicio"
            @remove-servicio="removeServicio"
            @update-servicio="updateServicio"
            @update-destino="updateDestino"
            @update-recoger-en="updateRecogerEn"
            @update-idioma="updateIdioma"
            @update-numero-pax="updateNumeroPax"
            @update-cuando="updateCuando"
            @update-observaciones="updateObservaciones"
          />
        </q-tab-panel>

        <q-tab-panel :name="3">
          <reserva-adicionales-tab
            :adicionales="reserva.adicionales"
            :subtotal="subtotalAdicionales"
            :total-no-contable="totalNoContable"
            @add-adicional="addAdicional"
            @remove-adicional="removeAdicional"
            @update-adicional="updateAdicional"
            @update-cantidad="updateCantidad"
            @update-cuando="updateCuandoAdicional"
            @update-contable="updateContable"
          />
        </q-tab-panel>

        <q-tab-panel :name="4">
          <reserva-resumen-tab
            :reserva="reserva"
            :subtotal-servicios="subtotalServicios"
            :subtotal-adicionales="subtotalAdicionales"
            :total-no-contable="totalNoContable"
            :estado-options="estadoOptions"
            :tipo-pago-options="tipoPagoOptions"
            :tipo-documento-options="tipoDocumentoOptions"
            :idioma-options="idiomaOptions"
            :format-date="formatDate"
          />
        </q-tab-panel>
      </q-tab-panels>
    </q-form>

    <!-- Botón flotante de guardar -->
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="save" color="positive" @click="saveReserva" size="lg">
        <q-tooltip>Guardar cambios</q-tooltip>
      </q-btn>
    </q-page-sticky>

    <!-- Botón flotante de cancelar -->
    <q-page-sticky position="bottom-left" :offset="[18, 18]">
      <q-btn fab icon="close" color="negative" flat @click="goBack" size="md">
        <q-tooltip>Cancelar</q-tooltip>
      </q-btn>
    </q-page-sticky>

    <!-- Dialog para crear cliente -->
    <q-dialog v-model="showClienteDialog" :maximized="$q.screen.xs">
      <q-card :style="$q.screen.gt.xs ? 'min-width: 400px; max-width: 500px' : ''">
        <q-card-section>
          <div class="text-h6">Nueva Agencia</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input v-model="nuevoCliente.nombre" label="Nombre *" outlined dense />
          <q-input
            v-model="nuevoCliente.telefonos"
            label="Teléfonos"
            outlined
            dense
            class="q-mt-sm"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="primary" v-close-popup />
          <q-btn label="Guardar" color="primary" @click="createCliente" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import ReservaDatosTab from 'src/components/reservas/ReservaDatosTab.vue'
import ReservaServiciosTab from 'src/components/reservas/ReservaServiciosTab.vue'
import ReservaAdicionalesTab from 'src/components/reservas/ReservaAdicionalesTab.vue'
import ReservaResumenTab from 'src/components/reservas/ReservaResumenTab.vue'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const tab = ref(1)
const showClienteDialog = ref(false)

// Opciones
const estadoOptions = [
  { label: 'Pagado', value: '0' },
  { label: 'Deuda', value: '1' },
]

const tipoPagoOptions = [
  { value: '0', label: 'Efectivo' },
  { value: '1', label: 'Depósito' },
  { value: '2', label: 'Otro' },
]

const tipoDocumentoOptions = [
  { value: 'boleta', label: 'Boleta' },
  { value: 'factura', label: 'Factura' },
  { value: 'ninguno', label: 'Ninguno' },
]

const idiomaOptions = [
  { value: 'es', label: 'Español' },
  { value: 'en', label: 'Inglés' },
  { value: 'pt', label: 'Portugués' },
  { value: 'fr', label: 'Francés' },
  { value: 'de', label: 'Alemán' },
  { value: 'it', label: 'Italiano' },
  { value: 'zh', label: 'Chino' },
  { value: 'ja', label: 'Japonés' },
  { value: 'ko', label: 'Coreano' },
  { value: 'otro', label: 'Otro' },
]

const reserva = ref({
  fecha: null,
  cliente: null,
  pasajero: '',
  estado: '1',
  tipo_pago: null,
  tipo_documento: null,
  total: 0,
  observaciones: '',
  detalles: [],
  adicionales: [],
})

const nuevoCliente = ref({
  nombre: '',
  telefonos: '',
})

// Computeds
const subtotalServicios = computed(() => {
  return reserva.value.detalles.reduce((sum, detalle) => sum + (parseFloat(detalle.total) || 0), 0)
})

const subtotalAdicionales = computed(() => {
  return reserva.value.adicionales.reduce(
    (sum, adicional) => sum + (parseFloat(adicional.total) || 0),
    0,
  )
})

const totalNoContable = computed(() => {
  return reserva.value.adicionales
    .filter((adicional) => !adicional.contable)
    .reduce((sum, adicional) => sum + (parseFloat(adicional.total) || 0), 0)
})

// Funciones de servicios
async function aplicarPrecioEspecialServicio(detalle) {
  if (detalle.servicio?.id && reserva.value.cliente?.id) {
    try {
      const response = await api.get('base/servicio-precios-especiales/', {
        params: {
          servicio: detalle.servicio.id,
          cliente: reserva.value.cliente.id,
          activo: true,
        },
      })

      const preciosEspeciales = response.data.results || []
      const today = new Date().toISOString().split('T')[0]

      const precioVigente = preciosEspeciales.find((precio) => {
        const desde = precio.fecha_desde
        const hasta = precio.fecha_hasta
        if (!desde) return false
        if (desde > today) return false
        if (hasta && hasta < today) return false
        return true
      })

      if (precioVigente) {
        const precioNormal = parseFloat(detalle.servicio.precio)
        const precioEspecial = parseFloat(precioVigente.precio)
        const ahorro = precioNormal - precioEspecial
        const porcentaje = ((ahorro / precioNormal) * 100).toFixed(1)
        detalle.precio_aplicado = precioEspecial
        detalle.observacion_precio = `Precio especial para ${reserva.value.cliente.nombre} (S/ ${precioNormal.toFixed(2)} → S/ ${precioEspecial.toFixed(2)}, ahorro: ${porcentaje}%)${precioVigente.observaciones ? ' - ' + precioVigente.observaciones : ''}`
      } else {
        detalle.precio_aplicado = parseFloat(detalle.servicio.precio)
        detalle.observacion_precio = `Precio estándar: S/ ${detalle.servicio.precio} por PAX`
      }
    } catch (error) {
      console.error('Error al consultar precios especiales:', error)
      detalle.precio_aplicado = parseFloat(detalle.servicio.precio)
      detalle.observacion_precio = `Precio estándar: S/ ${detalle.servicio.precio} por PAX`
    }
  } else if (detalle.servicio?.precio) {
    detalle.precio_aplicado = parseFloat(detalle.servicio.precio)
    detalle.observacion_precio = `Precio estándar: S/ ${detalle.servicio.precio} por PAX`
  }
}

async function aplicarPrecioEspecialAdicional(adicional) {
  if (adicional.adicional?.id && reserva.value.cliente?.id) {
    try {
      const response = await api.get('base/adicional-precios-especiales/', {
        params: {
          adicional: adicional.adicional.id,
          cliente: reserva.value.cliente.id,
          activo: true,
        },
      })

      const preciosEspeciales = response.data.results || []
      const today = new Date().toISOString().split('T')[0]

      const precioVigente = preciosEspeciales.find((precio) => {
        const desde = precio.fecha_desde
        const hasta = precio.fecha_hasta
        if (!desde) return false
        if (desde > today) return false
        if (hasta && hasta < today) return false
        return true
      })

      if (precioVigente) {
        const precioNormal = parseFloat(adicional.adicional.precio)
        const precioEspecial = parseFloat(precioVigente.precio)
        const ahorro = precioNormal - precioEspecial
        const porcentaje = ((ahorro / precioNormal) * 100).toFixed(1)
        adicional.precio_aplicado = precioEspecial
        adicional.observacion_precio = `Precio especial para ${reserva.value.cliente.nombre} (S/ ${precioNormal.toFixed(2)} → S/ ${precioEspecial.toFixed(2)}, ahorro: ${porcentaje}%)${precioVigente.observaciones ? ' - ' + precioVigente.observaciones : ''}`
      } else {
        adicional.precio_aplicado = parseFloat(adicional.adicional.precio)
        adicional.observacion_precio = `Precio estándar: S/ ${adicional.adicional.precio} por unidad`
      }
    } catch (error) {
      console.error('Error al consultar precios especiales:', error)
      adicional.precio_aplicado = parseFloat(adicional.adicional.precio)
      adicional.observacion_precio = `Precio estándar: S/ ${adicional.adicional.precio} por unidad`
    }
  } else if (adicional.adicional?.precio) {
    adicional.precio_aplicado = parseFloat(adicional.adicional.precio)
    adicional.observacion_precio = `Precio estándar: S/ ${adicional.adicional.precio} por unidad`
  }
}

// Re-calcular precios especiales cuando cambia el cliente
watch(
  () => reserva.value.cliente?.id,
  async (newClienteId, oldClienteId) => {
    if (newClienteId === oldClienteId) return
    for (const detalle of reserva.value.detalles) {
      if (detalle.servicio?.id) {
        await aplicarPrecioEspecialServicio(detalle)
        calcularSubtotalServicio(detalle)
      }
    }
    for (const adicional of reserva.value.adicionales) {
      if (adicional.adicional?.id) {
        await aplicarPrecioEspecialAdicional(adicional)
        calcularSubtotalAdicional(adicional)
      }
    }
  },
)

function addServicio() {
  reserva.value.detalles.push({
    id: Date.now(),
    servicio: null,
    destino: null,
    recoger_en: null,
    cuando: reserva.value.fecha,
    idioma: { value: 'es', label: 'Español' },
    numero_pax: 1,
    precio_aplicado: null,
    observacion_precio: '',
    observaciones: '',
    total: 0,
  })
}

function removeServicio(index) {
  reserva.value.detalles.splice(index, 1)
  calcularTotal()
}

async function updateServicio(index, value) {
  reserva.value.detalles[index].servicio = value
  if (!value?.id) return
  await aplicarPrecioEspecialServicio(reserva.value.detalles[index])
  calcularSubtotalServicio(reserva.value.detalles[index])
}

function updateDestino(index, value) {
  reserva.value.detalles[index].destino = value
}

function updateRecogerEn(index, value) {
  reserva.value.detalles[index].recoger_en = value
}

function updateIdioma(index, value) {
  reserva.value.detalles[index].idioma = value
}

function updateNumeroPax(index, value) {
  reserva.value.detalles[index].numero_pax = value
  calcularSubtotalServicio(reserva.value.detalles[index])
}

function updateCuando(index, value) {
  reserva.value.detalles[index].cuando = value
}

function updateObservaciones(index, value) {
  reserva.value.detalles[index].observaciones = value
}

function calcularSubtotalServicio(detalle) {
  const precio = parseFloat(detalle.precio_aplicado || detalle.servicio?.precio || 0)
  const pax = parseInt(detalle.numero_pax) || 1
  detalle.total = precio * pax
  calcularTotal()
}

// Funciones de adicionales
function addAdicional() {
  reserva.value.adicionales.push({
    id: Date.now(),
    adicional: null,
    cuando: reserva.value.fecha,
    cantidad: 1,
    contable: true,
    precio_aplicado: null,
    observacion_precio: '',
    total: 0,
  })
}

function removeAdicional(index) {
  reserva.value.adicionales.splice(index, 1)
  calcularTotal()
}

async function updateAdicional(index, value) {
  reserva.value.adicionales[index].adicional = value
  if (value?.contable !== undefined) {
    reserva.value.adicionales[index].contable = value.contable
  }
  if (!value?.id) return
  await aplicarPrecioEspecialAdicional(reserva.value.adicionales[index])
  calcularSubtotalAdicional(reserva.value.adicionales[index])
}

function updateCantidad(index, value) {
  reserva.value.adicionales[index].cantidad = value
  calcularSubtotalAdicional(reserva.value.adicionales[index])
}

function updateCuandoAdicional(index, value) {
  reserva.value.adicionales[index].cuando = value
}

function updateContable(index, value) {
  reserva.value.adicionales[index].contable = value
  calcularTotal()
}

function calcularSubtotalAdicional(adicional) {
  const precio = parseFloat(adicional.precio_aplicado || adicional.adicional?.precio || 0)
  const cantidad = parseInt(adicional.cantidad) || 1
  adicional.total = precio * cantidad
  calcularTotal()
}

function calcularTotal() {
  const subtotalServ = reserva.value.detalles.reduce(
    (sum, detalle) => sum + (parseFloat(detalle.total) || 0),
    0,
  )
  const subtotalAdic = reserva.value.adicionales.reduce(
    (sum, adicional) => sum + (parseFloat(adicional.total) || 0),
    0,
  )
  const noContable = reserva.value.adicionales
    .filter((adicional) => !adicional.contable)
    .reduce((sum, adicional) => sum + (parseFloat(adicional.total) || 0), 0)

  reserva.value.total = subtotalServ + subtotalAdic - noContable
}

// Funciones de cliente
function openClienteDialog(searchText = '') {
  nuevoCliente.value = {
    nombre: searchText,
    telefonos: '',
  }
  showClienteDialog.value = true
}

async function createCliente() {
  if (!nuevoCliente.value.nombre) {
    notifyError('El nombre es requerido')
    return
  }

  try {
    const response = await api.post('base/clientes/', {
      nombre: nuevoCliente.value.nombre,
      telefonos: nuevoCliente.value.telefonos,
      activo: true,
    })

    reserva.value.cliente = response.data
    showClienteDialog.value = false
    notifySuccess('Agencia creada correctamente')
  } catch (error) {
    notifyError('Error al crear la agencia')
    console.error(error)
  }
}

// Funciones de carga y guardado
async function loadReserva() {
  try {
    const response = await api.get(`reservas/reservas/${route.params.id}/`)

    // Cargar objetos completos
    const detallesPromises = (response.data.detalles || []).map(async (detalle) => {
      const [servicioRes, lugarRes] = await Promise.all([
        detalle.servicio ? api.get(`base/servicios/${detalle.servicio}/`) : Promise.resolve(null),
        detalle.recoger_en ? api.get(`base/lugares/${detalle.recoger_en}/`) : Promise.resolve(null),
      ])

      return {
        ...detalle,
        servicio: servicioRes?.data || null,
        destino: detalle.destino || null,
        recoger_en: lugarRes?.data || null,
        cuando: detalle.cuando || null,
        idioma: idiomaOptions.find((opt) => opt.value === detalle.idioma) || {
          value: 'es',
          label: 'Español',
        },
        precio_aplicado: detalle.precio_aplicado || null,
        observacion_precio: detalle.observacion_precio || '',
        seleccionado: detalle.seleccionado || false,
      }
    })

    const adicionalesPromises = (response.data.adicionales_detalle || []).map(async (adicional) => {
      const adicionalRes = adicional.adicional
        ? await api.get(`base/adicionales/${adicional.adicional}/`)
        : null

      return {
        ...adicional,
        adicional: adicionalRes?.data || null,
        cuando: adicional.cuando || null,
        contable: adicionalRes?.data?.contable !== undefined ? adicionalRes.data.contable : true,
        precio_aplicado: adicional.precio_aplicado || null,
        observacion_precio: adicional.observacion_precio || '',
      }
    })

    const clienteRes = response.data.cliente
      ? await api.get(`base/clientes/${response.data.cliente}/`)
      : null

    const [detalles, adicionales] = await Promise.all([
      Promise.all(detallesPromises),
      Promise.all(adicionalesPromises),
    ])

    reserva.value = {
      ...response.data,
      cliente: clienteRes?.data || null,
      detalles,
      adicionales,
    }
    calcularTotal()
  } catch (error) {
    notifyError('Error al cargar la reserva')
    console.error(error)
  }
}

async function saveReserva() {
  try {
    const data = {
      fecha: reserva.value.fecha,
      cliente: reserva.value.cliente?.id ? parseInt(reserva.value.cliente.id) : null,
      pasajero: reserva.value.pasajero,
      estado: reserva.value.estado,
      tipo_pago: reserva.value.tipo_pago,
      tipo_documento: reserva.value.tipo_documento,
      total: parseFloat(reserva.value.total) || 0,
      observaciones: reserva.value.observaciones,
      detalles_data: reserva.value.detalles
        .filter((detalle) => detalle.servicio?.id && detalle.recoger_en?.id)
        .map((detalle) => ({
          ...(detalle.id &&
            typeof detalle.id === 'number' &&
            detalle.id < 1000000000000 && { id: parseInt(detalle.id) }),
          servicio: parseInt(detalle.servicio.id),
          destino: detalle.destino || null,
          recoger_en: parseInt(detalle.recoger_en.id),
          cuando: detalle.cuando || reserva.value.fecha,
          idioma: detalle.idioma?.value || detalle.idioma || 'es',
          numero_pax: parseInt(detalle.numero_pax) || 1,
          precio_aplicado: detalle.precio_aplicado ? parseFloat(detalle.precio_aplicado) : null,
          observacion_precio: detalle.observacion_precio || '',
          observaciones: detalle.observaciones || '',
          total: parseFloat(detalle.total) || 0,
        })),
      adicionales_data: reserva.value.adicionales
        .filter((adicional) => adicional.adicional?.id)
        .map((adicional) => ({
          ...(adicional.id &&
            typeof adicional.id === 'number' &&
            adicional.id < 1000000000000 && { id: parseInt(adicional.id) }),
          adicional: parseInt(adicional.adicional.id),
          contable: adicional.contable,
          cuando: adicional.cuando || reserva.value.fecha,
          cantidad: parseInt(adicional.cantidad) || 1,
          precio_aplicado: adicional.precio_aplicado ? parseFloat(adicional.precio_aplicado) : null,
          observacion_precio: adicional.observacion_precio || '',
          total: parseFloat(adicional.total) || 0,
        })),
    }

    await api.put(`reservas/reservas/${route.params.id}/`, data)
    notifySuccess('Reserva actualizada correctamente')
    router.push('/reservas')
  } catch (error) {
    notifyError('Error al guardar la reserva')
    console.error(error)
  }
}

function goBack() {
  router.push('/reservas')
}

function formatDate(dateString) {
  if (!dateString) return 'Sin fecha'
  const date = new Date(dateString + 'T00:00:00')
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(() => {
  loadReserva()
})
</script>
