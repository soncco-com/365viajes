<template>
  <q-page class="q-pa-md">
    <page-title
      :title="isEditing ? 'Editar Reserva' : 'Nueva Reserva'"
      :subtitle="isEditing ? `Reserva #${reserva.numero || 'S/N'}` : 'Crear nueva reserva'"
    />

    <q-form @submit="saveReserva" class="q-mt-md">
      <q-stepper v-model="step" vertical color="primary" animated>
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
                    v-model="reserva.cliente"
                    label="Agencia *"
                    endpoint="base/clientes"
                    option-label="nombre"
                    :rules="[(val) => !!val || 'La agencia es requerida']"
                  >
                    <template #after>
                      <q-btn
                        round
                        dense
                        flat
                        icon="add"
                        color="primary"
                        @click="showClienteDialog = true"
                      >
                        <q-tooltip>Crear nueva agencia</q-tooltip>
                      </q-btn>
                    </template>
                  </autocomplete-input>
                </div>

                <div class="col-12 col-md-4">
                  <q-input
                    v-model="reserva.pasajero"
                    label="Pasajero *"
                    outlined
                    dense
                    :rules="[(val) => !!val || 'El pasajero es requerido']"
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

                <div class="col-12 col-md-3">
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

                <div class="col-12 col-md-3">
                  <q-select
                    v-model="reserva.tipo_documento"
                    :options="tipoDocumentoOptions"
                    label="Tipo de Documento"
                    outlined
                    dense
                    clearable
                    emit-value
                    map-options
                  />
                </div>

                <div class="col-12 col-md-3">
                  <q-input
                    v-model="reserva.total"
                    label="Total"
                    outlined
                    dense
                    readonly
                    prefix="S/"
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
            <q-btn label="Siguiente" color="primary" @click="step = 2" />
          </div>
        </q-step>

        <q-step :name="2" title="Servicios" icon="tour" :done="step > 2">
          <q-card flat bordered>
            <q-card-section>
              <div class="q-mb-md">
                <q-btn
                  label="Agregar Servicio"
                  color="primary"
                  icon="add"
                  @click="addServicio"
                  size="sm"
                />
              </div>

              <q-table
                :rows="reserva.detalles"
                :columns="serviciosColumns"
                row-key="id"
                flat
                bordered
                dense
              >
                <template v-slot:body-cell-servicio="props">
                  <q-td :props="props">
                    <autocomplete-input
                      v-model="props.row.servicio"
                      endpoint="base/servicios"
                      option-label="nombre"
                      dense
                      hide-bottom-space
                      @update:model-value="calcularSubtotalServicio(props.row)"
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-lugar="props">
                  <q-td :props="props">
                    <autocomplete-input
                      v-model="props.row.recoger_en"
                      endpoint="base/lugares"
                      option-label="nombre"
                      dense
                      hide-bottom-space
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-cuando="props">
                  <q-td :props="props">
                    <q-input
                      v-model="props.row.cuando"
                      type="time"
                      dense
                      outlined
                      hide-bottom-space
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-idioma="props">
                  <q-td :props="props">
                    <q-select
                      v-model="props.row.idioma"
                      :options="idiomaOptions"
                      dense
                      outlined
                      hide-bottom-space
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-numero_pax="props">
                  <q-td :props="props">
                    <q-input
                      v-model.number="props.row.numero_pax"
                      type="number"
                      dense
                      outlined
                      hide-bottom-space
                      min="1"
                      @update:model-value="calcularSubtotalServicio(props.row)"
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-subtotal="props">
                  <q-td :props="props">
                    <div class="text-weight-medium">
                      S/ {{ props.row.total?.toFixed(2) || '0.00' }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-acciones="props">
                  <q-td :props="props">
                    <q-btn
                      flat
                      round
                      dense
                      color="negative"
                      icon="delete"
                      @click="removeServicio(props.rowIndex)"
                      size="sm"
                    />
                  </q-td>
                </template>
              </q-table>

              <div class="q-mt-md text-right">
                <div class="text-h6">Subtotal Servicios: S/ {{ subtotalServicios.toFixed(2) }}</div>
              </div>
            </q-card-section>
          </q-card>

          <div class="q-mt-md q-gutter-sm">
            <q-btn label="Anterior" color="primary" flat @click="step = 1" />
            <q-btn label="Siguiente" color="primary" @click="step = 3" />
          </div>
        </q-step>

        <q-step :name="3" title="Adicionales" icon="add_circle" :done="step > 3">
          <q-card flat bordered>
            <q-card-section>
              <div class="q-mb-md">
                <q-btn
                  label="Agregar Adicional"
                  color="primary"
                  icon="add"
                  @click="addAdicional"
                  size="sm"
                />
              </div>

              <q-table
                :rows="reserva.adicionales"
                :columns="adicionalesColumns"
                row-key="id"
                flat
                bordered
                dense
              >
                <template v-slot:body-cell-adicional="props">
                  <q-td :props="props">
                    <autocomplete-input
                      v-model="props.row.adicional"
                      endpoint="base/adicionales"
                      option-label="nombre"
                      dense
                      hide-bottom-space
                      @update:model-value="calcularSubtotalAdicional(props.row)"
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-cuando="props">
                  <q-td :props="props">
                    <q-input
                      v-model="props.row.cuando"
                      type="time"
                      dense
                      outlined
                      hide-bottom-space
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-cantidad="props">
                  <q-td :props="props">
                    <q-input
                      v-model.number="props.row.cantidad"
                      type="number"
                      dense
                      outlined
                      hide-bottom-space
                      min="1"
                      @update:model-value="calcularSubtotalAdicional(props.row)"
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-contable="props">
                  <q-td :props="props">
                    <q-checkbox
                      v-model="props.row.contable"
                      dense
                      @update:model-value="calcularTotal"
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-subtotal="props">
                  <q-td :props="props">
                    <div class="text-weight-medium">
                      S/ {{ props.row.subtotal?.toFixed(2) || '0.00' }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-acciones="props">
                  <q-td :props="props">
                    <q-btn
                      flat
                      round
                      dense
                      color="negative"
                      icon="delete"
                      @click="removeAdicional(props.rowIndex)"
                      size="sm"
                    />
                  </q-td>
                </template>
              </q-table>

              <div class="q-mt-md text-right">
                <div class="text-body1">
                  Subtotal Adicionales: S/ {{ subtotalAdicionales.toFixed(2) }}
                </div>
                <div class="text-body1 text-negative">
                  Total No Contable: -S/ {{ totalNoContable.toFixed(2) }}
                </div>
              </div>
            </q-card-section>
          </q-card>

          <div class="q-mt-md q-gutter-sm">
            <q-btn label="Anterior" color="primary" flat @click="step = 2" />
            <q-btn label="Siguiente" color="primary" @click="step = 4" />
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
                  <q-card flat bordered class="bg-primary text-white">
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
                          <strong>TOTAL: S/ {{ reserva.total?.toFixed(2) || '0.00' }}</strong>
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
                              {{ detalle.recoger_en?.nombre || 'N/A' }} - {{ detalle.cuando }} -
                              {{ detalle.idioma }} - {{ detalle.numero_pax }} pax
                            </q-item-label>
                          </q-item-section>
                          <q-item-section side>
                            <q-item-label
                              >S/ {{ detalle.total?.toFixed(2) || '0.00' }}</q-item-label
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
                              {{ adicional.cuando }} - {{ adicional.cantidad }} x S/
                              {{ adicional.adicional?.precio || 0 }}
                              <q-badge
                                v-if="!adicional.contable"
                                color="negative"
                                label="No contable"
                                class="q-ml-sm"
                              />
                            </q-item-label>
                          </q-item-section>
                          <q-item-section side>
                            <q-item-label
                              >S/ {{ adicional.subtotal?.toFixed(2) || '0.00' }}</q-item-label
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

    <q-dialog v-model="showClienteDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Nueva Agencia</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input v-model="nuevoCliente.nombre" label="Nombre *" outlined dense />
          <q-input
            v-model="nuevoCliente.telefono"
            label="Teléfono"
            outlined
            dense
            class="q-mt-sm"
          />
          <q-input
            v-model="nuevoCliente.email"
            label="Email"
            type="email"
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
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DatePicker from 'src/components/DatePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const step = ref(1)
const isEditing = computed(() => !!route.params.id)
const showClienteDialog = ref(false)

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
  telefono: '',
  email: '',
})

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

const serviciosColumns = [
  { name: 'servicio', label: 'Servicio', field: 'servicio', align: 'left' },
  { name: 'lugar', label: 'Lugar', field: 'recoger_en', align: 'left' },
  { name: 'cuando', label: 'Hora', field: 'cuando', align: 'center' },
  { name: 'idioma', label: 'Idioma', field: 'idioma', align: 'center' },
  { name: 'numero_pax', label: 'PAX', field: 'numero_pax', align: 'center' },
  { name: 'subtotal', label: 'Subtotal', field: 'total', align: 'right' },
  { name: 'acciones', label: 'Acciones', align: 'center' },
]

const adicionalesColumns = [
  { name: 'adicional', label: 'Adicional', field: 'adicional', align: 'left' },
  { name: 'cuando', label: 'Hora', field: 'cuando', align: 'center' },
  { name: 'cantidad', label: 'Cantidad', field: 'cantidad', align: 'center' },
  { name: 'contable', label: 'Contable', field: 'contable', align: 'center' },
  { name: 'subtotal', label: 'Subtotal', field: 'subtotal', align: 'right' },
  { name: 'acciones', label: 'Acciones', align: 'center' },
]

const subtotalServicios = computed(() => {
  return reserva.value.detalles.reduce((sum, detalle) => sum + (detalle.total || 0), 0)
})

const subtotalAdicionales = computed(() => {
  return reserva.value.adicionales.reduce((sum, adicional) => sum + (adicional.subtotal || 0), 0)
})

const totalNoContable = computed(() => {
  return reserva.value.adicionales
    .filter((adicional) => !adicional.contable)
    .reduce((sum, adicional) => sum + (adicional.subtotal || 0), 0)
})

watch([subtotalServicios, subtotalAdicionales, totalNoContable], () => {
  calcularTotal()
})

function calcularTotal() {
  reserva.value.total = subtotalServicios.value + subtotalAdicionales.value - totalNoContable.value
}

function calcularSubtotalServicio(detalle) {
  if (detalle.servicio && detalle.numero_pax) {
    detalle.total = detalle.servicio.precio * detalle.numero_pax
  } else {
    detalle.total = 0
  }
  calcularTotal()
}

function calcularSubtotalAdicional(adicional) {
  if (adicional.adicional && adicional.cantidad) {
    adicional.subtotal = adicional.adicional.precio * adicional.cantidad
  } else {
    adicional.subtotal = 0
  }
  calcularTotal()
}

function addServicio() {
  reserva.value.detalles.push({
    id: Date.now(),
    servicio: null,
    recoger_en: null,
    cuando: '',
    idioma: 'Español',
    numero_pax: 1,
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
    cuando: '',
    cantidad: 1,
    contable: true,
    subtotal: 0,
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

async function loadReserva() {
  try {
    const response = await api.get(`reservas/reservas/${route.params.id}/`)
    reserva.value = {
      ...response.data,
      detalles: response.data.detalles || [],
      adicionales: response.data.adicionales || [],
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
      cliente: reserva.value.cliente?.id,
      pasajero: reserva.value.pasajero,
      estado: reserva.value.estado,
      tipo_pago: reserva.value.tipo_pago,
      tipo_documento: reserva.value.tipo_documento,
      total: reserva.value.total,
      observaciones: reserva.value.observaciones,
      detalles: reserva.value.detalles.map((detalle) => ({
        id: detalle.id > 1000000000000 ? null : detalle.id,
        servicio: detalle.servicio?.id,
        recoger_en: detalle.recoger_en?.id,
        cuando: detalle.cuando,
        idioma: detalle.idioma,
        numero_pax: detalle.numero_pax,
        total: detalle.total,
        seleccionado: detalle.seleccionado,
      })),
      adicionales: reserva.value.adicionales.map((adicional) => ({
        id: adicional.id > 1000000000000 ? null : adicional.id,
        adicional: adicional.adicional?.id,
        cuando: adicional.cuando,
        cantidad: adicional.cantidad,
        contable: adicional.contable,
        subtotal: adicional.subtotal,
      })),
    }

    if (isEditing.value) {
      await api.put(`reservas/reservas/${route.params.id}/`, data)
      notifySuccess('Reserva actualizada correctamente')
    } else {
      await api.post('reservas/reservas/', data)
      notifySuccess('Reserva creada correctamente')
    }

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
      telefono: nuevoCliente.value.telefono,
      email: nuevoCliente.value.email,
      activo: true,
    })

    reserva.value.cliente = response.data
    showClienteDialog.value = false
    nuevoCliente.value = { nombre: '', telefono: '', email: '' }
    notifySuccess('Agencia creada correctamente')
  } catch (error) {
    notifyError('Error al crear la agencia')
    console.error(error)
  }
}

function goBack() {
  router.push('/reservas')
}

onMounted(() => {
  if (isEditing.value) {
    loadReserva()
  }
})
</script>
