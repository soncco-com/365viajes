<template>
  <q-card flat bordered>
    <q-card-section>
      <div class="row justify-between items-center q-mb-md">
        <div class="text-subtitle2 text-grey-8">{{ adicionales.length }} adicional(es)</div>
        <q-btn
          label="Agregar Adicional"
          color="primary"
          icon="add"
          @click="$emit('add-adicional')"
          size="sm"
          unelevated
        />
      </div>

      <!-- Grid de Adicionales -->
      <div v-if="adicionales.length > 0" class="row q-col-gutter-md">
        <div v-for="(adicional, index) in adicionales" :key="adicional.id" class="col-12 col-md-6">
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
                  @click="$emit('remove-adicional', index)"
                  size="sm"
                >
                  <q-tooltip>Eliminar adicional</q-tooltip>
                </q-btn>
              </div>
            </q-card-section>

            <q-card-section>
              <autocomplete-input
                :model-value="adicional.adicional"
                @update:model-value="$emit('update-adicional', index, $event)"
                endpoint="base/adicionales"
                option-label="nombre"
                label="Adicional *"
                dense
                class="q-mb-md"
              >
                <template v-slot:prepend>
                  <q-icon name="add_box" />
                </template>
              </autocomplete-input>

              <div v-if="adicional.observacion_precio" class="text-caption text-grey-7 q-mb-md">
                <q-icon name="info" size="xs" />
                {{ adicional.observacion_precio }}
              </div>

              <q-input
                :model-value="adicional.cantidad"
                @update:model-value="$emit('update-cantidad', index, $event)"
                type="number"
                label="Cantidad"
                dense
                outlined
                min="1"
                class="q-mb-md"
              >
                <template v-slot:prepend>
                  <q-icon name="tag" />
                </template>
              </q-input>

              <date-picker
                :model-value="adicional.cuando"
                @update:model-value="$emit('update-cuando', index, $event)"
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
                  :model-value="adicional.contable"
                  @update:model-value="$emit('update-contable', index, $event)"
                  label="Contable"
                  color="primary"
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
          <div class="text-caption text-grey-6">Haz clic en "Agregar Adicional" para comenzar</div>
        </q-card-section>
      </q-card>

      <div class="q-mt-md text-right">
        <div class="text-body1">Subtotal Adicionales: S/ {{ subtotal.toFixed(2) }}</div>
        <div class="text-body1">Total No Contable: -S/ {{ totalNoContable.toFixed(2) }}</div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import DatePicker from 'src/components/DatePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

defineProps({
  adicionales: {
    type: Array,
    required: true,
  },
  subtotal: {
    type: Number,
    required: true,
  },
  totalNoContable: {
    type: Number,
    required: true,
  },
})

defineEmits([
  'add-adicional',
  'remove-adicional',
  'update-adicional',
  'update-cantidad',
  'update-cuando',
  'update-contable',
])
</script>
