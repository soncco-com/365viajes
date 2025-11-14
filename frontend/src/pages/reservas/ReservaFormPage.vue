<template>
  <q-page class="q-pa-md">
    <page-title
      :title="isEditing ? 'Editar Reserva' : 'Nueva Reserva'"
      :subtitle="isEditing ? `Reserva #${reserva.numero || 'S/N'}` : 'Crear nueva reserva'"
    />

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
                    label="Tipo de Documento"
                    outlined
                    dense
                    clearable
                    emit-value
                    map-options
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
                :grid="$q.screen.lt.md"
              >
                <template v-slot:body-cell-servicio="props">
                  <q-td :props="props">
                    <autocomplete-input
                      v-model="props.row.servicio"
                      endpoint="base/servicios"
                      option-label="nombre"
                      label="Servicio"
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
                      label="Hotel"
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
                      map-options
                    />
                  </q-td>
                </template>

                <template v-slot:body-cell-numero_pax="props">
                  <q-td :props="props">
                    <div class="text-center text-weight-medium">
                      {{ props.row.numero_pax }}
                    </div>
                  </q-td>
                </template>

                <template v-slot:body-cell-subtotal="props">
                  <q-td :props="props">
                    <div class="text-weight-medium">
                      S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}
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

                <!-- Vista GRID para móviles -->
                <template v-slot:item="props">
                  <div class="q-pa-xs col-12">
                    <q-card flat bordered>
                      <q-card-section class="q-pb-none">
                        <div class="text-weight-bold text-primary q-mb-md">
                          Servicio #{{ props.rowIndex + 1 }}
                        </div>
                      </q-card-section>

                      <q-card-section class="q-pt-sm">
                        <div class="q-gutter-md">
                          <autocomplete-input
                            v-model="props.row.servicio"
                            endpoint="base/servicios"
                            option-label="nombre"
                            label="Servicio *"
                            dense
                            @update:model-value="calcularSubtotalServicio(props.row)"
                          />

                          <autocomplete-input
                            v-model="props.row.recoger_en"
                            endpoint="base/lugares"
                            option-label="nombre"
                            label="Lugar"
                            dense
                          />

                          <div class="row q-col-gutter-md">
                            <div class="col-6">
                              <q-input
                                v-model="props.row.cuando"
                                type="time"
                                label="Hora"
                                dense
                                outlined
                              />
                            </div>
                            <div class="col-6">
                              <q-select
                                v-model="props.row.idioma"
                                :options="idiomaOptions"
                                label="Idioma"
                                dense
                                outlined
                                map-options
                              />
                            </div>
                          </div>

                          <div class="row q-col-gutter-md items-center">
                            <div class="col-6">
                              <q-input
                                v-model.number="props.row.numero_pax"
                                type="number"
                                label="PAX"
                                dense
                                outlined
                                min="1"
                                @update:model-value="calcularSubtotalServicio(props.row)"
                              />
                            </div>
                            <div class="col-6">
                              <div class="text-center">
                                <div class="text-caption text-grey-7">Subtotal</div>
                                <div class="text-weight-bold text-h6 text-primary">
                                  S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </q-card-section>

                      <q-separator />

                      <q-card-actions align="right">
                        <q-btn
                          flat
                          color="negative"
                          icon="delete"
                          label="Eliminar"
                          @click="removeServicio(props.rowIndex)"
                        />
                      </q-card-actions>
                    </q-card>
                  </div>
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
                :grid="$q.screen.lt.md"
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
                      S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}
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

                <!-- Vista GRID para móviles -->
                <template v-slot:item="props">
                  <div class="q-pa-xs col-12">
                    <q-card flat bordered>
                      <q-card-section class="q-pb-none">
                        <div class="text-weight-bold text-primary q-mb-md">
                          Adicional #{{ props.rowIndex + 1 }}
                        </div>
                      </q-card-section>

                      <q-card-section class="q-pt-sm">
                        <div class="q-gutter-md">
                          <autocomplete-input
                            v-model="props.row.adicional"
                            endpoint="base/adicionales"
                            option-label="nombre"
                            label="Adicional *"
                            dense
                            @update:model-value="calcularSubtotalAdicional(props.row)"
                          />

                          <div class="row q-col-gutter-md">
                            <div class="col-6">
                              <q-input
                                v-model="props.row.cuando"
                                type="time"
                                label="Hora"
                                dense
                                outlined
                              />
                            </div>
                            <div class="col-6">
                              <q-input
                                v-model.number="props.row.cantidad"
                                type="number"
                                label="Cantidad"
                                dense
                                outlined
                                min="1"
                                @update:model-value="calcularSubtotalAdicional(props.row)"
                              />
                            </div>
                          </div>

                          <div class="row q-col-gutter-md items-center">
                            <div class="col-6">
                              <q-checkbox
                                v-model="props.row.contable"
                                label="Contable"
                                dense
                                @update:model-value="calcularTotal"
                              />
                            </div>
                            <div class="col-6">
                              <div class="text-center">
                                <div class="text-caption text-grey-7">Subtotal</div>
                                <div class="text-weight-bold text-h6 text-primary">
                                  S/ {{ parseFloat(props.row.total || 0).toFixed(2) }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </q-card-section>

                      <q-separator />

                      <q-card-actions align="right">
                        <q-btn
                          flat
                          color="negative"
                          icon="delete"
                          label="Eliminar"
                          @click="removeAdicional(props.rowIndex)"
                        />
                      </q-card-actions>
                    </q-card>
                  </div>
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
                              {{ detalle.recoger_en?.nombre || 'N/A' }} - {{ detalle.cuando }} -
                              {{ getIdiomaLabel(detalle.idioma) }} - {{ detalle.numero_pax }} pax
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import DatePicker from 'src/components/DatePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const step = ref(1)
const isEditing = computed(() => !!route.params.id)
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

const serviciosColumns = [
  { name: 'servicio', label: 'Servicio', field: 'servicio', align: 'left' },
  { name: 'lugar', label: 'Lugar', field: 'recoger_en', align: 'left' },
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
  { name: 'subtotal', label: 'Subtotal', field: 'total', align: 'right' },
  { name: 'acciones', label: 'Acciones', align: 'center' },
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

function calcularSubtotalServicio(detalle) {
  if (detalle.servicio?.precio && detalle.numero_pax) {
    detalle.total = parseFloat(detalle.servicio.precio) * parseInt(detalle.numero_pax)
  } else {
    detalle.total = 0
  }
}

function calcularSubtotalAdicional(adicional) {
  if (adicional.adicional?.precio && adicional.cantidad) {
    adicional.total = parseFloat(adicional.adicional.precio) * parseInt(adicional.cantidad)
  } else {
    adicional.total = 0
  }
}

function addServicio() {
  reserva.value.detalles.push({
    id: Date.now(),
    servicio: null,
    recoger_en: null,
    cuando: '',
    idioma: { value: 'es', label: 'Español' },
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

async function loadReserva() {
  try {
    const response = await api.get(`reservas/reservas/${route.params.id}/`)

    // Cargar objetos completos para servicio y lugar en cada detalle
    const detallesPromises = (response.data.detalles || []).map(async (detalle) => {
      const [servicioRes, lugarRes] = await Promise.all([
        detalle.servicio ? api.get(`base/servicios/${detalle.servicio}/`) : Promise.resolve(null),
        detalle.recoger_en ? api.get(`base/lugares/${detalle.recoger_en}/`) : Promise.resolve(null),
      ])

      return {
        ...detalle,
        servicio: servicioRes?.data || null,
        recoger_en: lugarRes?.data || null,
        idioma: idiomaOptions.find((opt) => opt.value === detalle.idioma) || {
          value: 'es',
          label: 'Español',
        },
      }
    })

    // Cargar objetos completos para adicional en cada adicional
    const adicionalesPromises = (response.data.adicionales_detalle || []).map(async (adicional) => {
      const adicionalRes = adicional.adicional
        ? await api.get(`base/adicionales/${adicional.adicional}/`)
        : null

      return {
        ...adicional,
        adicional: adicionalRes?.data || null,
      }
    })

    // Cargar objeto completo del cliente
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
          ...(detalle.id && { id: parseInt(detalle.id) }), // Incluir ID si existe (para edición)
          servicio: parseInt(detalle.servicio.id),
          recoger_en: parseInt(detalle.recoger_en.id),
          cuando: reserva.value.fecha,
          idioma: detalle.idioma?.value || detalle.idioma || 'es',
          numero_pax: parseInt(detalle.numero_pax) || 1,
          total: parseFloat(detalle.total) || 0,
          seleccionado: detalle.seleccionado || false,
        })),
      adicionales_data: reserva.value.adicionales
        .filter((adicional) => adicional.adicional?.id)
        .map((adicional) => ({
          ...(adicional.id && { id: parseInt(adicional.id) }), // Incluir ID si existe (para edición)
          adicional: parseInt(adicional.adicional.id),
          cuando: reserva.value.fecha,
          cantidad: parseInt(adicional.cantidad) || 1,
          total: parseFloat(adicional.total) || 0,
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

function goBack() {
  router.push('/reservas')
}

onMounted(() => {
  if (isEditing.value) {
    loadReserva()
  }
})
</script>
