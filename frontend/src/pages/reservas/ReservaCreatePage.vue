<template>
  <q-page class="q-pa-md">
    <page-title title="Nueva Reserva" subtitle="Crear nueva reserva" />

    <q-form @submit="saveReserva" class="q-mt-md">
      <q-stepper v-model="step" :grid="!$q.screen.lt.md" color="primary" animated>
        <q-step :name="1" title="Datos Principales" icon="info" :done="step > 1">
          <q-card flat bordered>
            <q-card-section>
              <div class="row q-col-gutter-md">
                <div class="col-12 col-md-4">
                  <date-picker
                    v-model="reserva.fecha"
                    label="Fecha *"
                    :rules="[(val) => !!val || 'La fecha es requerida']"
                  />
                </div>

                <div class="col-12 col-md-4">
                  <autocomplete-input
                    ref="clienteAutocompleteRef"
                    v-model="reserva.cliente"
                    label="Agencia *"
                    endpoint="base/clientes"
                    option-label="nombre"
                    :rules="[(val) => !!val || 'La agencia es requerida']"
                    :allow-create="true"
                    @create="openClienteDialog()"
                    @create-with-text="openClienteDialog"
                  />
                </div>

                <div class="col-12 col-md-4">
                  <q-input
                    v-model="reserva.pasajero"
                    label="Pasajero *"
                    outlined
                    dense
                    :rules="[(val) => !!val || 'El pasajero es requerido']"
                    @update:model-value="(val) => (reserva.pasajero = val.toUpperCase())"
                  />
                </div>

                <div class="col-12 col-md-3">
                  <q-select
                    v-model="reserva.estado"
                    :options="estadoOptions"
                    label="Estado *"
                    outlined
                    dense
                    emit-value
                    map-options
                    :rules="[(val) => val !== null || 'El estado es requerido']"
                  />
                </div>

                <div class="col-12 col-md-4">
                  <q-select
                    v-model="reserva.tipo_pago"
                    :options="tipoPagoOptions"
                    label="Tipo de Pago"
                    outlined
                    dense
                    clearable
                    emit-value
                    map-options
                  />
                </div>

                <div class="col-12 col-md-4">
                  <q-select
                    v-model="reserva.tipo_documento"
                    :options="tipoDocumentoOptions"
                    label="Tipo de Documento *"
                    outlined
                    dense
                    emit-value
                    map-options
                    :rules="[
                      (val) =>
                        (val !== null && val !== undefined) || 'El tipo de documento es requerido',
                    ]"
                  />
                </div>

                <div class="col-12">
                  <q-input
                    v-model="reserva.observaciones"
                    label="Observaciones"
                    outlined
                    dense
                    type="textarea"
                    rows="3"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>

          <div class="q-mt-md">
            <q-btn label="Siguiente" color="primary" @click="validarYAvanzar(2)" />
          </div>
        </q-step>

        <q-step :name="2" title="Servicios" icon="tour" :done="step > 2">
          <q-card flat bordered>
            <q-card-section>
              <div class="row justify-between items-center q-mb-md">
                <div class="text-subtitle2 text-grey-8">
                  {{ reserva.detalles.length }} servicio(s)
                </div>
                <q-btn
                  label="Agregar Servicio"
                  color="primary"
                  icon="add"
                  @click="addServicio"
                  size="sm"
                  unelevated
                />
              </div>

              <!-- Grid de Servicios -->
              <div v-if="reserva.detalles.length > 0" class="row q-col-gutter-md">
                <div
                  v-for="(detalle, index) in reserva.detalles"
                  :key="detalle.id"
                  class="col-12 col-md-6"
                >
                  <q-card flat bordered>
                    <q-card-section class="bg-primary text-white q-py-sm">
                      <div class="row items-center justify-between">
                        <div class="text-subtitle2">
                          <q-icon name="tour" class="q-mr-xs" />
                          Servicio #{{ index + 1 }}
                        </div>
                        <q-btn
                          flat
                          dense
                          round
                          icon="delete"
                          color="white"
                          @click="removeServicio(index)"
                          size="sm"
                        >
                          <q-tooltip>Eliminar servicio</q-tooltip>
                        </q-btn>
                      </div>
                    </q-card-section>

                    <q-card-section>
                      <autocomplete-input
                        v-model="detalle.servicio"
                        endpoint="base/servicios"
                        option-label="nombre"
                        label="Servicio *"
                        dense
                        class="q-mb-md"
                        @update:model-value="onServicioChange(detalle)"
                      >
                        <template v-slot:prepend>
                          <q-icon name="tour" />
                        </template>
                      </autocomplete-input>

                      <q-input
                        v-if="detalle.servicio?.mostrar_destinos"
                        v-model="detalle.destino"
                        label="Destino final"
                        dense
                        outlined
                        placeholder="Ej: Hotel, Aeropuerto"
                        hint="Especifica el destino final del servicio"
                        class="q-mb-md"
                      >
                        <template v-slot:prepend>
                          <q-icon name="place" color="primary" />
                        </template>
                      </q-input>

                      <autocomplete-input
                        v-model="detalle.recoger_en"
                        endpoint="base/lugares"
                        option-label="nombre"
                        label="Hotel/Lugar de recojo"
                        dense
                        class="q-mb-md"
                      >
                        <template v-slot:prepend>
                          <q-icon name="hotel" />
                        </template>
                      </autocomplete-input>

                      <q-select
                        v-model="detalle.idioma"
                        :options="idiomaOptions"
                        label="Idioma"
                        dense
                        outlined
                        map-options
                        class="q-mb-md"
                      >
                        <template v-slot:prepend>
                          <q-icon name="language" />
                        </template>
                      </q-select>

                      <q-input
                        v-model.number="detalle.numero_pax"
                        type="number"
                        label="Número de PAX"
                        dense
                        outlined
                        min="1"
                        class="q-mb-md"
                        @update:model-value="calcularSubtotalServicio(detalle)"
                      >
                        <template v-slot:prepend>
                          <q-icon name="people" />
                        </template>
                      </q-input>

                      <date-picker
                        v-model="detalle.cuando"
                        label="Fecha del servicio *"
                        dense
                        class="q-mb-sm"
                      >
                        <template v-slot:prepend>
                          <q-icon name="event" />
                        </template>
                      </date-picker>

                      <div
                        v-if="detalle.observacion_precio"
                        class="text-caption text-grey-7 q-mb-md"
                      >
                        <q-icon name="info" size="xs" />
                        {{ detalle.observacion_precio }}
                      </div>
                    </q-card-section>

                    <q-separator />

                    <q-card-section class="bg-grey-2">
                      <div class="row items-center justify-between">
                        <div class="text-body2 text-grey-8">Subtotal del servicio:</div>
                        <div class="text-h6 text-weight-bold text-positive">
                          S/ {{ parseFloat(detalle.total || 0).toFixed(2) }}
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>

              <!-- Estado vacío -->
              <q-card v-else flat bordered class="bg-grey-1">
                <q-card-section class="text-center q-py-lg">
                  <q-icon name="add_circle_outline" size="48px" color="grey-5" />
                  <div class="text-subtitle2 text-grey-7 q-mt-sm">No hay servicios agregados</div>
                  <div class="text-caption text-grey-6">
                    Haz clic en "Agregar Servicio" para comenzar
                  </div>
                </q-card-section>
              </q-card>

              <div class="q-mt-md text-right">
                <div class="text-h6">Subtotal Servicios: S/ {{ subtotalServicios.toFixed(2) }}</div>
              </div>
            </q-card-section>
          </q-card>

          <div class="q-mt-md q-gutter-sm">
            <q-btn label="Anterior" color="primary" flat @click="step = 1" />
            <q-btn label="Siguiente" color="primary" @click="validarYAvanzar(3)" />
          </div>
        </q-step>

        <q-step :name="3" title="Adicionales" icon="add_circle" :done="step > 3">
          <q-card flat bordered>
            <q-card-section>
              <div class="row justify-between items-center q-mb-md">
                <div class="text-subtitle2 text-grey-8">
                  {{ reserva.adicionales.length }} adicional(es)
                </div>
                <q-btn
                  label="Agregar Adicional"
                  color="primary"
                  icon="add"
                  @click="addAdicional"
                  size="sm"
                  unelevated
                />
              </div>

              <!-- Grid de Adicionales -->
              <div v-if="reserva.adicionales.length > 0" class="row q-col-gutter-md">
                <div
                  v-for="(adicional, index) in reserva.adicionales"
                  :key="adicional.id"
                  class="col-12 col-md-6"
                >
                  <q-card flat bordered>
                    <q-card-section class="bg-orange-8 text-white q-py-sm">
                      <div class="row items-center justify-between">
                        <div class="text-subtitle2">
                          <q-icon name="add_circle" class="q-mr-xs" />
                          Adicional #{{ index + 1 }}
                        </div>
                        <q-btn
                          flat
                          dense
                          round
                          icon="delete"
                          color="white"
                          @click="removeAdicional(index)"
                          size="sm"
                        >
                          <q-tooltip>Eliminar adicional</q-tooltip>
                        </q-btn>
                      </div>
                    </q-card-section>

                    <q-card-section>
                      <autocomplete-input
                        v-model="adicional.adicional"
                        endpoint="base/adicionales"
                        option-label="nombre"
                        label="Adicional *"
                        dense
                        class="q-mb-md"
                        @update:model-value="onAdicionalChange(adicional)"
                      >
                        <template v-slot:prepend>
                          <q-icon name="add_box" />
                        </template>
                      </autocomplete-input>

                      <div
                        v-if="adicional.observacion_precio"
                        class="text-caption text-grey-7 q-mb-md"
                      >
                        <q-icon name="info" size="xs" />
                        {{ adicional.observacion_precio }}
                      </div>

                      <q-input
                        v-model.number="adicional.cantidad"
                        type="number"
                        label="Cantidad"
                        dense
                        outlined
                        min="1"
                        class="q-mb-md"
                        @update:model-value="calcularSubtotalAdicional(adicional)"
                      >
                        <template v-slot:prepend>
                          <q-icon name="tag" />
                        </template>
                      </q-input>

                      <date-picker
                        v-model="adicional.cuando"
                        label="Fecha del adicional *"
                        dense
                        class="q-mb-md"
                      >
                        <template v-slot:prepend>
                          <q-icon name="event" />
                        </template>
                      </date-picker>

                      <div>
                        <q-checkbox
                          v-model="adicional.contable"
                          label="Contable"
                          color="primary"
                          @update:model-value="calcularTotal"
                        />
                        <div class="text-caption text-grey-6">
                          {{ adicional.contable ? 'Se suma al total' : 'No se suma al total' }}
                        </div>
                      </div>
                    </q-card-section>

                    <q-separator />

                    <q-card-section class="bg-grey-2">
                      <div class="row items-center justify-between">
                        <div class="text-body2 text-grey-8">Subtotal del adicional:</div>
                        <div class="text-h6 text-weight-bold text-positive">
                          S/ {{ parseFloat(adicional.total || 0).toFixed(2) }}
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>

              <!-- Estado vacío -->
              <q-card v-else flat bordered class="bg-grey-1">
                <q-card-section class="text-center q-py-lg">
                  <q-icon name="add_circle_outline" size="48px" color="grey-5" />
                  <div class="text-subtitle2 text-grey-7 q-mt-sm">No hay adicionales agregados</div>
                  <div class="text-caption text-grey-6">
                    Haz clic en "Agregar Adicional" para comenzar
                  </div>
                </q-card-section>
              </q-card>

              <div class="q-mt-md text-right">
                <div class="text-body1">
                  Subtotal Adicionales: S/ {{ subtotalAdicionales.toFixed(2) }}
                </div>
                <div class="text-body1">
                  Total No Contable: -S/ {{ totalNoContable.toFixed(2) }}
                </div>
              </div>
            </q-card-section>
          </q-card>

          <div class="q-mt-md q-gutter-sm">
            <q-btn label="Anterior" color="primary" flat @click="step = 2" />
            <q-btn label="Siguiente" color="primary" @click="validarYAvanzar(4)" />
          </div>
        </q-step>

        <q-step :name="4" title="Resumen" icon="check_circle">
          <q-card flat bordered>
            <q-card-section>
              <div class="row q-col-gutter-md">
                <div class="col-12 col-md-6">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-h6 q-mb-md">Datos Principales</div>
                      <div class="q-gutter-sm">
                        <div><strong>Fecha:</strong> {{ reserva.fecha }}</div>
                        <div><strong>Agencia:</strong> {{ reserva.cliente?.nombre || 'N/A' }}</div>
                        <div><strong>Pasajero:</strong> {{ reserva.pasajero }}</div>
                        <div><strong>Estado:</strong> {{ getEstadoLabel(reserva.estado) }}</div>
                        <div v-if="reserva.tipo_pago">
                          <strong>Tipo de Pago:</strong> {{ reserva.tipo_pago }}
                        </div>
                        <div v-if="reserva.tipo_documento">
                          <strong>Tipo de Documento:</strong> {{ reserva.tipo_documento }}
                        </div>
                        <div v-if="reserva.observaciones">
                          <strong>Observaciones:</strong> {{ reserva.observaciones }}
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>

                <div class="col-12 col-md-6">
                  <q-card flat bordered class="">
                    <q-card-section>
                      <div class="text-h6 q-mb-md">Totales</div>
                      <div class="q-gutter-sm">
                        <div class="text-h6">Servicios: S/ {{ subtotalServicios.toFixed(2) }}</div>
                        <div class="text-h6">
                          Adicionales: S/ {{ subtotalAdicionales.toFixed(2) }}
                        </div>
                        <div class="text-h6 text-negative">
                          No Contable: -S/ {{ totalNoContable.toFixed(2) }}
                        </div>
                        <q-separator dark class="q-my-md" />
                        <div class="text-h4">
                          <strong>TOTAL: S/ {{ parseFloat(reserva.total || 0).toFixed(2) }}</strong>
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>

                <div class="col-12" v-if="reserva.detalles.length > 0">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-h6 q-mb-md">Servicios ({{ reserva.detalles.length }})</div>
                      <q-list dense separator>
                        <q-item v-for="(detalle, index) in reserva.detalles" :key="index">
                          <q-item-section>
                            <q-item-label>{{ detalle.servicio?.nombre || 'N/A' }}</q-item-label>
                            <q-item-label caption>
                              <q-icon name="event" size="xs" />
                              {{ formatDate(detalle.cuando) }} -
                              {{ detalle.recoger_en?.nombre || 'N/A' }} -
                              {{ getIdiomaLabel(detalle.idioma) }} - {{ detalle.numero_pax }} pax
                              <span v-if="detalle.destino" class="text-primary">
                                → Destino: {{ detalle.destino }}
                              </span>
                            </q-item-label>
                            <q-item-label
                              caption
                              v-if="detalle.observacion_precio"
                              class="text-grey-7"
                            >
                              <q-icon name="info" size="xs" />
                              {{ detalle.observacion_precio }}
                            </q-item-label>
                          </q-item-section>
                          <q-item-section side>
                            <q-item-label
                              >S/ {{ parseFloat(detalle.total || 0).toFixed(2) }}</q-item-label
                            >
                          </q-item-section>
                        </q-item>
                      </q-list>
                    </q-card-section>
                  </q-card>
                </div>

                <div class="col-12" v-if="reserva.adicionales.length > 0">
                  <q-card flat bordered>
                    <q-card-section>
                      <div class="text-h6 q-mb-md">
                        Adicionales ({{ reserva.adicionales.length }})
                      </div>
                      <q-list dense separator>
                        <q-item v-for="(adicional, index) in reserva.adicionales" :key="index">
                          <q-item-section>
                            <q-item-label>{{ adicional.adicional?.nombre || 'N/A' }}</q-item-label>
                            <q-item-label caption>
                              <q-icon name="event" size="xs" />
                              {{ formatDate(adicional.cuando) }} - {{ adicional.cantidad }} x S/
                              {{ adicional.precio_aplicado || adicional.adicional?.precio || 0 }}
                              <q-badge
                                v-if="!adicional.contable"
                                color="negative"
                                label="No contable"
                                class="q-ml-sm"
                              />
                            </q-item-label>
                            <q-item-label
                              caption
                              v-if="adicional.observacion_precio"
                              class="text-grey-7"
                            >
                              <q-icon name="info" size="xs" />
                              {{ adicional.observacion_precio }}
                            </q-item-label>
                          </q-item-section>
                          <q-item-section side>
                            <q-item-label
                              >S/ {{ parseFloat(adicional.total || 0).toFixed(2) }}</q-item-label
                            >
                          </q-item-section>
                        </q-item>
                      </q-list>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <div class="q-mt-md q-gutter-sm">
            <q-btn label="Anterior" color="primary" flat @click="step = 3" />
            <q-btn label="Guardar" color="positive" type="submit" icon="save" />
            <q-btn label="Cancelar" color="negative" flat @click="goBack" />
          </div>
        </q-step>
      </q-stepper>
    </q-form>

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
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DatePicker from 'src/components/DatePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const $q = useQuasar()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const step = ref(1)
const showClienteDialog = ref(false)
const clienteAutocompleteRef = ref(null)

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

const openClienteDialog = (searchText = '') => {
  nuevoCliente.value = {
    nombre: searchText,
    telefonos: '',
  }
  showClienteDialog.value = true
}

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
  {
    value: '0',
    label: 'Boleta',
  },
  {
    value: '1',
    label: 'Factura',
  },
  {
    value: '2',
    label: 'Otros',
  },
]
const idiomaOptions = [
  {
    value: 'es',
    label: 'Español',
  },
  {
    value: 'en',
    label: 'Inglés',
  },
  { value: 'xx', label: 'Bilingüe' },
]

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

watch([subtotalServicios, subtotalAdicionales, totalNoContable], () => {
  calcularTotal()
})

function calcularTotal() {
  reserva.value.total = subtotalServicios.value + subtotalAdicionales.value - totalNoContable.value
}

function formatDate(dateString) {
  if (!dateString) return 'Sin fecha'
  const date = new Date(dateString + 'T00:00:00') // Evitar problemas de timezone
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

async function onServicioChange(detalle) {
  // Limpiar destino si el servicio no requiere destinos
  if (!detalle.servicio?.mostrar_destinos) {
    detalle.destino = null
  }

  // Buscar precio especial si hay cliente y servicio seleccionados
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

      // Filtrar por vigencia
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
        detalle.observacion_precio = `Precio especial para ${reserva.value.cliente.nombre} (S/ ${precioNormal.toFixed(2)} → S/ ${precioEspecial.toFixed(2)}, ahorro: ${porcentaje}%)${
          precioVigente.observaciones ? ' - ' + precioVigente.observaciones : ''
        }`
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

  calcularSubtotalServicio(detalle)
}

function calcularSubtotalServicio(detalle) {
  const precio = detalle.precio_aplicado || detalle.servicio?.precio || 0
  if (precio && detalle.numero_pax) {
    detalle.total = parseFloat(precio) * parseInt(detalle.numero_pax)
  } else {
    detalle.total = 0
  }
}

async function onAdicionalChange(adicional) {
  // Buscar precio especial si hay cliente y adicional seleccionados
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

      // Filtrar por vigencia
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
        adicional.observacion_precio = `Precio especial para ${reserva.value.cliente.nombre} (S/ ${precioNormal.toFixed(2)} → S/ ${precioEspecial.toFixed(2)}, ahorro: ${porcentaje}%)${
          precioVigente.observaciones ? ' - ' + precioVigente.observaciones : ''
        }`
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

  calcularSubtotalAdicional(adicional)
}

function calcularSubtotalAdicional(adicional) {
  const precio = adicional.precio_aplicado || adicional.adicional?.precio || 0
  if (precio && adicional.cantidad) {
    adicional.total = parseFloat(precio) * parseInt(adicional.cantidad)
    // Copiar el valor de contable del adicional seleccionado
    if (adicional.adicional.contable !== undefined) {
      adicional.contable = adicional.adicional.contable
    }
  } else {
    adicional.total = 0
  }
  calcularTotal()
}

function addServicio() {
  reserva.value.detalles.push({
    id: Date.now(),
    servicio: null,
    destino: null,
    recoger_en: null,
    idioma: { value: 'es', label: 'Español' },
    numero_pax: 1,
    cuando: reserva.value.fecha || null,
    precio_aplicado: null,
    observacion_precio: '',
    total: 0,
    seleccionado: false,
  })
}

function removeServicio(index) {
  reserva.value.detalles.splice(index, 1)
  calcularTotal()
}

function addAdicional() {
  reserva.value.adicionales.push({
    id: Date.now(),
    adicional: null,
    cantidad: 1,
    cuando: reserva.value.fecha || null,
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

function getEstadoLabel(value) {
  const option = estadoOptions.find((opt) => opt.value === value)
  return option ? option.label : 'N/A'
}

function getIdiomaLabel(value) {
  // Si es un objeto, retornar el label directamente
  if (typeof value === 'object' && value?.label) {
    return value.label
  }
  // Si es un string, buscar en las opciones
  const option = idiomaOptions.find((opt) => opt.value === value)
  return option ? option.label : value
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
            detalle.id < 1000000000000 && { id: parseInt(detalle.id) }), // Incluir ID solo si es válido (no temporal)
          servicio: parseInt(detalle.servicio.id),
          destino: detalle.destino || null,
          recoger_en: parseInt(detalle.recoger_en.id),
          cuando: detalle.cuando || reserva.value.fecha,
          idioma: detalle.idioma?.value || detalle.idioma || 'es',
          numero_pax: parseInt(detalle.numero_pax) || 1,
          precio_aplicado: detalle.precio_aplicado ? parseFloat(detalle.precio_aplicado) : null,
          observacion_precio: detalle.observacion_precio || '',
          total: parseFloat(detalle.total) || 0,
          seleccionado: Boolean(detalle.seleccionado), // Preservar valor exacto, no forzar a false
        })),
      adicionales_data: reserva.value.adicionales
        .filter((adicional) => adicional.adicional?.id)
        .map((adicional) => ({
          ...(adicional.id &&
            typeof adicional.id === 'number' &&
            adicional.id < 1000000000000 && { id: parseInt(adicional.id) }), // Incluir ID solo si es válido (no temporal)
          adicional: parseInt(adicional.adicional.id),
          cuando: adicional.cuando || reserva.value.fecha,
          cantidad: parseInt(adicional.cantidad) || 1,
          precio_aplicado: adicional.precio_aplicado ? parseFloat(adicional.precio_aplicado) : null,
          observacion_precio: adicional.observacion_precio || '',
          total: parseFloat(adicional.total) || 0,
        })),
    }

    await api.post('reservas/reservas/', data)
    notifySuccess('Reserva creada correctamente')
    router.push('/reservas')
  } catch (error) {
    notifyError('Error al guardar la reserva')
    console.error(error)
  }
}

async function createCliente() {
  try {
    const response = await api.post('base/clientes/', {
      nombre: nuevoCliente.value.nombre,
      telefonos: nuevoCliente.value.telefonos,
      activo: true,
    })

    reserva.value.cliente = response.data
    showClienteDialog.value = false
    nuevoCliente.value = { nombre: '', telefonos: '' }

    // Recargar opciones del autocomplete
    if (clienteAutocompleteRef.value) {
      await clienteAutocompleteRef.value.reload()
    }

    notifySuccess('Agencia creada correctamente')
  } catch (error) {
    notifyError('Error al crear la agencia')
    console.error(error)
  }
}

function validarYAvanzar(siguientePaso) {
  let valido = true
  let mensaje = ''

  if (siguientePaso === 2) {
    // Validar paso 1: Datos principales
    if (!reserva.value.fecha) {
      mensaje = 'La fecha es obligatoria'
      valido = false
    } else if (!reserva.value.cliente) {
      mensaje = 'La agencia es obligatoria'
      valido = false
    } else if (!reserva.value.pasajero || reserva.value.pasajero.trim() === '') {
      mensaje = 'El nombre del pasajero es obligatorio'
      valido = false
    } else if (!reserva.value.estado) {
      mensaje = 'El estado es obligatorio'
      valido = false
    } else if (
      reserva.value.tipo_documento === null ||
      reserva.value.tipo_documento === undefined
    ) {
      mensaje = 'El tipo de documento es obligatorio'
      valido = false
    }
  } else if (siguientePaso === 3) {
    // Validar paso 2: Servicios
    if (reserva.value.detalles.length > 0) {
      const errores = validarServicios()
      if (errores.length > 0) {
        mensaje = errores.join('\n')
        valido = false
      }
    }
    // Si no hay servicios, se puede avanzar
  } else if (siguientePaso === 4) {
    // Validar paso 3: Adicionales
    if (reserva.value.adicionales.length > 0) {
      const errores = validarAdicionales()
      if (errores.length > 0) {
        mensaje = errores.join('\n')
        valido = false
      }
    }
    // Si no hay adicionales, se puede avanzar
  }

  if (valido) {
    step.value = siguientePaso
  } else {
    $q.notify({
      type: 'negative',
      message: mensaje,
      position: 'top',
      timeout: 3000,
      multiLine: mensaje.includes('\n'),
    })
  }
}

function validarServicios() {
  const errores = []

  reserva.value.detalles.forEach((detalle, index) => {
    const numero = index + 1

    if (!detalle.servicio) {
      errores.push(`Servicio #${numero}: Debe seleccionar un servicio`)
    }

    if (!detalle.recoger_en) {
      errores.push(`Servicio #${numero}: Debe seleccionar un lugar de recojo`)
    }

    if (!detalle.numero_pax || detalle.numero_pax < 1) {
      errores.push(`Servicio #${numero}: El número de PAX debe ser mayor a 0`)
    }

    if (!detalle.cuando) {
      errores.push(`Servicio #${numero}: Debe seleccionar la fecha del servicio`)
    }

    // Validar destino solo si el servicio lo requiere
    if (detalle.servicio?.mostrar_destinos && (!detalle.destino || detalle.destino.trim() === '')) {
      errores.push(`Servicio #${numero}: Debe especificar el destino final`)
    }
  })

  return errores
}

function validarAdicionales() {
  const errores = []

  reserva.value.adicionales.forEach((adicional, index) => {
    const numero = index + 1

    if (!adicional.adicional) {
      errores.push(`Adicional #${numero}: Debe seleccionar un adicional`)
    }

    if (!adicional.cantidad || adicional.cantidad < 1) {
      errores.push(`Adicional #${numero}: La cantidad debe ser mayor a 0`)
    }

    if (!adicional.cuando) {
      errores.push(`Adicional #${numero}: Debe seleccionar la fecha del adicional`)
    }
  })

  return errores
}

function goBack() {
  router.push('/reservas')
}
</script>
