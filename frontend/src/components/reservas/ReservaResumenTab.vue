<template>
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
                  <strong>Tipo de Pago:</strong> {{ getTipoPagoLabel(reserva.tipo_pago) }}
                </div>
                <div v-if="reserva.tipo_documento">
                  <strong>Tipo de Documento:</strong>
                  {{ getTipoDocumentoLabel(reserva.tipo_documento) }}
                </div>
                <div v-if="reserva.observaciones">
                  <strong>Observaciones:</strong> {{ reserva.observaciones }}
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6 q-mb-md">Totales</div>
              <div class="q-gutter-sm">
                <div class="text-h6">Servicios: S/ {{ subtotalServicios.toFixed(2) }}</div>
                <div class="text-h6">Adicionales: S/ {{ subtotalAdicionales.toFixed(2) }}</div>
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
                      {{ formatDate(detalle.cuando) }} - {{ detalle.recoger_en?.nombre || 'N/A' }} -
                      {{ getIdiomaLabel(detalle.idioma) }} - {{ detalle.numero_pax }} pax
                      <span v-if="detalle.destino" class="text-primary">
                        → Destino: {{ detalle.destino }}
                      </span>
                    </q-item-label>
                    <q-item-label caption v-if="detalle.observacion_precio" class="text-grey-7">
                      <q-icon name="info" size="xs" />
                      {{ detalle.observacion_precio }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-item-label>S/ {{ parseFloat(detalle.total || 0).toFixed(2) }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12" v-if="reserva.adicionales.length > 0">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6 q-mb-md">Adicionales ({{ reserva.adicionales.length }})</div>
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
                    <q-item-label caption v-if="adicional.observacion_precio" class="text-grey-7">
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
</template>

<script setup>
const props = defineProps({
  reserva: {
    type: Object,
    required: true,
  },
  subtotalServicios: {
    type: Number,
    required: true,
  },
  subtotalAdicionales: {
    type: Number,
    required: true,
  },
  totalNoContable: {
    type: Number,
    required: true,
  },
  estadoOptions: {
    type: Array,
    required: true,
  },
  tipoPagoOptions: {
    type: Array,
    required: true,
  },
  tipoDocumentoOptions: {
    type: Array,
    required: true,
  },
  idiomaOptions: {
    type: Array,
    required: true,
  },
  formatDate: {
    type: Function,
    required: true,
  },
})

const getEstadoLabel = (valor) => {
  const option = props.estadoOptions.find((o) => o.value === valor)
  return option?.label || valor
}

const getTipoPagoLabel = (valor) => {
  const option = props.tipoPagoOptions.find((o) => o.value === valor)
  return option?.label || valor
}

const getTipoDocumentoLabel = (valor) => {
  const option = props.tipoDocumentoOptions.find((o) => o.value === valor)
  return option?.label || valor
}

const getIdiomaLabel = (valor) => {
  const option = props.idiomaOptions.find((o) => o.value === valor)
  return option?.label || valor
}
</script>
