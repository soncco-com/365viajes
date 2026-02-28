<template>
  <q-card flat bordered>
    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-4">
          <date-picker
            :model-value="reserva.fecha"
            @update:model-value="$emit('update:fecha', $event)"
            label="Fecha *"
            :rules="[(val) => !!val || 'La fecha es requerida']"
          />
        </div>

        <div class="col-12 col-md-4">
          <autocomplete-input
            :model-value="reserva.cliente"
            @update:model-value="$emit('update:cliente', $event)"
            label="Agencia *"
            endpoint="base/clientes"
            option-label="nombre"
            :rules="[(val) => !!val || 'La agencia es requerida']"
            :allow-create="true"
            @create="$emit('open-cliente-dialog')"
            @create-with-text="$emit('open-cliente-dialog', $event)"
          />
        </div>

        <div class="col-12 col-md-4">
          <q-input
            :model-value="reserva.pasajero"
            @update:model-value="$emit('update:pasajero', $event.toUpperCase())"
            label="Pasajero *"
            outlined
            dense
            :rules="[(val) => !!val || 'El pasajero es requerido']"
          />
        </div>

        <div class="col-12 col-md-3">
          <q-select
            :model-value="reserva.estado"
            @update:model-value="$emit('update:estado', $event)"
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
            :model-value="reserva.tipo_pago"
            @update:model-value="$emit('update:tipo_pago', $event)"
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
            :model-value="reserva.tipo_documento"
            @update:model-value="$emit('update:tipo_documento', $event)"
            :options="tipoDocumentoOptions"
            label="Tipo de Documento *"
            outlined
            dense
            emit-value
            map-options
            :rules="[
              (val) => (val !== null && val !== undefined) || 'El tipo de documento es requerido',
            ]"
          />
        </div>

        <div class="col-12">
          <q-input
            :model-value="reserva.observaciones"
            @update:model-value="$emit('update:observaciones', $event)"
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
</template>

<script setup>
import DatePicker from 'src/components/DatePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

defineProps({
  reserva: {
    type: Object,
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
})

defineEmits([
  'update:fecha',
  'update:cliente',
  'update:pasajero',
  'update:estado',
  'update:tipo_pago',
  'update:tipo_documento',
  'update:observaciones',
  'open-cliente-dialog',
])
</script>
