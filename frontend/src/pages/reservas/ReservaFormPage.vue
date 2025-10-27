<template>
  <q-page class="q-pa-md">
    <page-title
      :title="isEditing ? 'Editar Reserva' : 'Nueva Reserva'"
      :subtitle="isEditing ? `Reserva #${reserva.numero || 'S/N'}` : 'Crear nueva reserva'"
    />

    <q-form @submit="saveReserva" class="q-mt-md">
      <!-- Datos principales -->
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Datos de la Reserva</div>

          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-4">
              <date-picker
                v-model="reserva.fecha"
                label="Fecha"
                :rules="[(val) => !!val || 'La fecha es requerida']"
                required
              />
            </div>

            <div class="col-12 col-md-4">
              <autocomplete-input
                v-model="reserva.cliente"
                label="Agencia"
                endpoint="base/clientes"
                option-label="nombre"
                option-value="id"
                :rules="[(val) => !!val || 'La agencia es requerida']"
                required
              />
            </div>

            <div class="col-12 col-md-4">
              <q-input
                v-model="reserva.pasajero"
                label="Pasajero"
                filled
                :rules="[(val) => !!val || 'El pasajero es requerido']"
                required
              />
            </div>

            <div class="col-12 col-md-6">
              <q-input
                v-model="reserva.observaciones"
                label="Observaciones"
                filled
                type="textarea"
                rows="3"
              />
            </div>

            <div class="col-12 col-md-3">
              <q-select
                v-model="reserva.estado"
                label="Estado"
                :options="estadoOptions"
                emit-value
                map-options
                filled
                :rules="[(val) => (val !== null && val !== undefined) || 'El estado es requerido']"
                required
              />
            </div>

            <div class="col-12 col-md-3" v-if="isEditing && reserva.numero">
              <q-input v-model="reserva.numero" label="Número" filled readonly bg-color="grey-3" />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Detalles de servicios -->
      <q-card flat bordered class="q-mt-md">
        <q-card-section>
          <div class="row items-center q-mb-md">
            <div class="text-h6 col">Servicios</div>
            <q-btn
              color="primary"
              icon="add"
              label="Agregar Servicio"
              size="sm"
              @click="addDetalle"
            />
          </div>

          <q-table
            :rows="reserva.detalles"
            :columns="detallesColumns"
            row-key="temp_id"
            flat
            bordered
            :hide-pagination="true"
            :rows-per-page-options="[0]"
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="servicio" :props="props">
                  <autocomplete-input
                    v-model="props.row.servicio"
                    endpoint="base/servicios"
                    option-label="nombre"
                    option-value="id"
                    dense
                    @update:model-value="updateDetalleSubtotal(props.row)"
                  />
                </q-td>
                <q-td key="lugar" :props="props">
                  <autocomplete-input
                    v-model="props.row.lugar"
                    endpoint="base/lugares"
                    option-label="nombre"
                    option-value="id"
                    dense
                  />
                </q-td>
                <q-td key="numero_pax" :props="props">
                  <q-input
                    v-model.number="props.row.numero_pax"
                    type="number"
                    dense
                    filled
                    min="1"
                    @update:model-value="updateDetalleSubtotal(props.row)"
                  />
                </q-td>
                <q-td key="precio_unitario" :props="props">
                  <q-input
                    v-model.number="props.row.precio_unitario"
                    type="number"
                    dense
                    filled
                    prefix="S/"
                    readonly
                    bg-color="grey-3"
                  />
                </q-td>
                <q-td key="subtotal" :props="props">
                  <span class="text-weight-bold">
                    S/ {{ props.row.subtotal?.toFixed(2) || '0.00' }}
                  </span>
                </q-td>
                <q-td key="actions" :props="props">
                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    color="negative"
                    size="sm"
                    @click="removeDetalle(props.rowIndex)"
                  />
                </q-td>
              </q-tr>
            </template>

            <template v-slot:bottom-row>
              <q-tr>
                <q-td colspan="4" class="text-right text-weight-bold"> Subtotal Servicios: </q-td>
                <q-td colspan="2" class="text-weight-bold text-primary">
                  S/ {{ subtotalServicios.toFixed(2) }}
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- Adicionales -->
      <q-card flat bordered class="q-mt-md">
        <q-card-section>
          <div class="row items-center q-mb-md">
            <div class="text-h6 col">Adicionales</div>
            <q-btn
              color="primary"
              icon="add"
              label="Agregar Adicional"
              size="sm"
              @click="addAdicional"
            />
          </div>

          <q-table
            :rows="reserva.adicionales"
            :columns="adicionalesColumns"
            row-key="temp_id"
            flat
            bordered
            :hide-pagination="true"
            :rows-per-page-options="[0]"
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="adicional" :props="props">
                  <autocomplete-input
                    v-model="props.row.adicional"
                    endpoint="base/adicionales"
                    option-label="nombre"
                    option-value="id"
                    dense
                    @update:model-value="updateAdicionalSubtotal(props.row)"
                  />
                </q-td>
                <q-td key="cantidad" :props="props">
                  <q-input
                    v-model.number="props.row.cantidad"
                    type="number"
                    dense
                    filled
                    min="1"
                    @update:model-value="updateAdicionalSubtotal(props.row)"
                  />
                </q-td>
                <q-td key="precio_unitario" :props="props">
                  <q-input
                    v-model.number="props.row.precio_unitario"
                    type="number"
                    dense
                    filled
                    prefix="S/"
                    readonly
                    bg-color="grey-3"
                  />
                </q-td>
                <q-td key="contable" :props="props">
                  <q-checkbox
                    v-model="props.row.contable"
                    dense
                    @update:model-value="calculateTotal"
                  />
                </q-td>
                <q-td key="subtotal" :props="props">
                  <span class="text-weight-bold">
                    S/ {{ props.row.subtotal?.toFixed(2) || '0.00' }}
                  </span>
                </q-td>
                <q-td key="actions" :props="props">
                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    color="negative"
                    size="sm"
                    @click="removeAdicional(props.rowIndex)"
                  />
                </q-td>
              </q-tr>
            </template>

            <template v-slot:bottom-row>
              <q-tr>
                <q-td colspan="4" class="text-right text-weight-bold"> Subtotal Adicionales: </q-td>
                <q-td colspan="2" class="text-weight-bold text-primary">
                  S/ {{ subtotalAdicionales.toFixed(2) }}
                </q-td>
              </q-tr>
              <q-tr v-if="totalNoContable > 0">
                <q-td colspan="4" class="text-right text-weight-bold text-negative">
                  Total No Contable (descuento):
                </q-td>
                <q-td colspan="2" class="text-weight-bold text-negative">
                  - S/ {{ totalNoContable.toFixed(2) }}
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- Total -->
      <q-card flat bordered class="q-mt-md bg-grey-2">
        <q-card-section>
          <div class="row justify-end">
            <div class="col-12 col-md-4">
              <div class="text-h4 text-right text-primary">
                Total: S/ {{ reserva.total?.toFixed(2) || '0.00' }}
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Botones de acción -->
      <div class="row q-mt-md q-gutter-sm justify-end">
        <q-btn label="Cancelar" color="grey" flat @click="$router.push('/reservas')" />
        <q-btn label="Guardar" type="submit" color="primary" :loading="saving" :disable="saving" />
      </div>
    </q-form>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'
import DatePicker from 'src/components/DatePicker.vue'

const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const reservaId = route.params.id
const isEditing = computed(() => !!reservaId)
const saving = ref(false)

let detalleCounter = 0
let adicionalCounter = 0

const estadoOptions = [
  { label: 'Pagado', value: '0' },
  { label: 'Deuda', value: '1' },
]

const reserva = ref({
  fecha: new Date().toISOString().split('T')[0],
  cliente: null,
  pasajero: '',
  observaciones: '',
  estado: '1',
  numero: null,
  total: 0,
  detalles: [],
  adicionales: [],
})

const detallesColumns = [
  { name: 'servicio', label: 'Servicio', field: 'servicio', align: 'left', style: 'width: 30%' },
  { name: 'lugar', label: 'Hotel', field: 'lugar', align: 'left', style: 'width: 25%' },
  { name: 'numero_pax', label: 'PAX', field: 'numero_pax', align: 'center', style: 'width: 10%' },
  {
    name: 'precio_unitario',
    label: 'Precio',
    field: 'precio_unitario',
    align: 'right',
    style: 'width: 12%',
  },
  { name: 'subtotal', label: 'Subtotal', field: 'subtotal', align: 'right', style: 'width: 13%' },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center', style: 'width: 10%' },
]

const adicionalesColumns = [
  { name: 'adicional', label: 'Adicional', field: 'adicional', align: 'left', style: 'width: 35%' },
  { name: 'cantidad', label: 'Cantidad', field: 'cantidad', align: 'center', style: 'width: 15%' },
  {
    name: 'precio_unitario',
    label: 'Precio',
    field: 'precio_unitario',
    align: 'right',
    style: 'width: 15%',
  },
  { name: 'contable', label: 'Contable', field: 'contable', align: 'center', style: 'width: 10%' },
  { name: 'subtotal', label: 'Subtotal', field: 'subtotal', align: 'right', style: 'width: 15%' },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center', style: 'width: 10%' },
]

const subtotalServicios = computed(() => {
  return reserva.value.detalles.reduce((sum, detalle) => sum + (detalle.subtotal || 0), 0)
})

const subtotalAdicionales = computed(() => {
  return reserva.value.adicionales.reduce((sum, adicional) => sum + (adicional.subtotal || 0), 0)
})

const totalNoContable = computed(() => {
  return reserva.value.adicionales
    .filter((a) => !a.contable)
    .reduce((sum, adicional) => sum + (adicional.subtotal || 0), 0)
})

const addDetalle = () => {
  reserva.value.detalles.push({
    temp_id: ++detalleCounter,
    servicio: null,
    lugar: null,
    numero_pax: 1,
    precio_unitario: 0,
    subtotal: 0,
  })
}

const removeDetalle = (index) => {
  reserva.value.detalles.splice(index, 1)
  calculateTotal()
}

const addAdicional = () => {
  reserva.value.adicionales.push({
    temp_id: ++adicionalCounter,
    adicional: null,
    cantidad: 1,
    precio_unitario: 0,
    contable: true,
    subtotal: 0,
  })
}

const removeAdicional = (index) => {
  reserva.value.adicionales.splice(index, 1)
  calculateTotal()
}

const updateDetalleSubtotal = async (detalle) => {
  if (detalle.servicio) {
    try {
      const response = await api.get(`base/servicios/${detalle.servicio}/`)
      detalle.precio_unitario = parseFloat(response.data.precio)
    } catch (error) {
      console.error('Error al obtener precio del servicio:', error)
    }
  }

  detalle.subtotal = (detalle.numero_pax || 0) * (detalle.precio_unitario || 0)
  calculateTotal()
}

const updateAdicionalSubtotal = async (adicional) => {
  if (adicional.adicional) {
    try {
      const response = await api.get(`base/adicionales/${adicional.adicional}/`)
      adicional.precio_unitario = parseFloat(response.data.precio)
      adicional.contable = response.data.contable
    } catch (error) {
      console.error('Error al obtener precio del adicional:', error)
    }
  }

  adicional.subtotal = (adicional.cantidad || 0) * (adicional.precio_unitario || 0)
  calculateTotal()
}

const calculateTotal = () => {
  reserva.value.total = subtotalServicios.value + subtotalAdicionales.value - totalNoContable.value
}

const loadReserva = async () => {
  try {
    const response = await api.get(`reservas/reservas/${reservaId}/`)
    const data = response.data

    reserva.value = {
      fecha: data.fecha,
      cliente: data.cliente,
      pasajero: data.pasajero,
      observaciones: data.observaciones || '',
      estado: data.estado,
      numero: data.numero,
      total: parseFloat(data.total),
      detalles: data.detalles.map((d) => ({
        id: d.id,
        temp_id: ++detalleCounter,
        servicio: d.servicio,
        lugar: d.lugar,
        numero_pax: d.numero_pax,
        precio_unitario: parseFloat(d.precio_unitario || 0),
        subtotal: parseFloat(d.subtotal || 0),
      })),
      adicionales: data.adicionales.map((a) => ({
        id: a.id,
        temp_id: ++adicionalCounter,
        adicional: a.adicional,
        cantidad: a.cantidad,
        precio_unitario: parseFloat(a.precio_unitario || 0),
        contable: a.contable,
        subtotal: parseFloat(a.subtotal || 0),
      })),
    }
  } catch (error) {
    notifyError('Error al cargar la reserva')
    console.error(error)
    router.push('/reservas')
  }
}

const saveReserva = async () => {
  if (!reserva.value.detalles.length) {
    notifyError('Debe agregar al menos un servicio')
    return
  }

  saving.value = true

  try {
    const payload = {
      fecha: reserva.value.fecha,
      cliente: reserva.value.cliente,
      pasajero: reserva.value.pasajero,
      observaciones: reserva.value.observaciones,
      estado: reserva.value.estado,
      total: reserva.value.total,
      detalles: reserva.value.detalles.map((d) => ({
        id: d.id,
        servicio: d.servicio,
        lugar: d.lugar,
        numero_pax: d.numero_pax,
      })),
      adicionales: reserva.value.adicionales.map((a) => ({
        id: a.id,
        adicional: a.adicional,
        cantidad: a.cantidad,
      })),
    }

    if (isEditing.value) {
      await api.put(`reservas/reservas/${reservaId}/`, payload)
      notifySuccess('Reserva actualizada correctamente')
    } else {
      await api.post('reservas/reservas/', payload)
      notifySuccess('Reserva creada correctamente')
    }

    router.push('/reservas')
  } catch (error) {
    notifyError('Error al guardar la reserva')
    console.error(error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (isEditing.value) {
    loadReserva()
  } else {
    addDetalle()
  }
})
</script>
