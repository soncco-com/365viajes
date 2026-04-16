<template>
  <q-card flat bordered>
    <q-card-section>
      <div class="row justify-between items-center q-mb-md">
        <div class="text-subtitle2 text-grey-8">{{ detalles.length }} servicio(s)</div>
        <q-btn
          label="Agregar Servicio"
          color="primary"
          icon="add"
          @click="$emit('add-servicio')"
          size="sm"
          unelevated
        />
      </div>

      <!-- Grid de Servicios -->
      <div v-if="detalles.length > 0" class="row q-col-gutter-md">
        <div v-for="(detalle, index) in detalles" :key="detalle.id" class="col-12 col-md-6">
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
                  @click="$emit('remove-servicio', index)"
                  size="sm"
                >
                  <q-tooltip>Eliminar servicio</q-tooltip>
                </q-btn>
              </div>
            </q-card-section>

            <q-card-section>
              <autocomplete-input
                :model-value="detalle.servicio"
                @update:model-value="$emit('update-servicio', index, $event)"
                endpoint="base/servicios"
                option-label="nombre"
                label="Servicio *"
                dense
                class="q-mb-md"
              >
                <template v-slot:prepend>
                  <q-icon name="tour" />
                </template>
              </autocomplete-input>

              <autocomplete-input
                :model-value="detalle.recoger_en"
                @update:model-value="$emit('update-recoger-en', index, $event)"
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
                :model-value="detalle.idioma"
                @update:model-value="$emit('update-idioma', index, $event)"
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
                :model-value="detalle.numero_pax"
                @update:model-value="$emit('update-numero-pax', index, $event)"
                type="number"
                label="Número de PAX"
                dense
                outlined
                min="1"
                class="q-mb-md"
              >
                <template v-slot:prepend>
                  <q-icon name="people" />
                </template>
              </q-input>

              <date-picker
                :model-value="detalle.cuando"
                @update:model-value="$emit('update-cuando', index, $event)"
                label="Fecha del servicio *"
                dense
                class="q-mb-sm"
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
              </date-picker>

              <q-input
                v-if="detalle.servicio?.mostrar_destinos"
                :model-value="detalle.destino"
                @update:model-value="$emit('update-destino', index, $event)"
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

              <q-input
                :model-value="detalle.observaciones"
                @update:model-value="$emit('update-observaciones', index, $event)"
                label="Observaciones"
                dense
                outlined
                type="textarea"
                autogrow
                class="q-mb-md"
              >
                <template v-slot:prepend>
                  <q-icon name="notes" />
                </template>
              </q-input>

              <div v-if="detalle.observacion_precio" class="text-caption text-grey-7 q-mb-md">
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
          <div class="text-caption text-grey-6">Haz clic en "Agregar Servicio" para comenzar</div>
        </q-card-section>
      </q-card>

      <div class="q-mt-md text-right">
        <div class="text-h6">Subtotal Servicios: S/ {{ subtotal.toFixed(2) }}</div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import DatePicker from 'src/components/DatePicker.vue'
import AutocompleteInput from 'src/components/AutocompleteInput.vue'

defineProps({
  detalles: {
    type: Array,
    required: true,
  },
  idiomaOptions: {
    type: Array,
    required: true,
  },
  subtotal: {
    type: Number,
    required: true,
  },
})

defineEmits([
  'add-servicio',
  'remove-servicio',
  'update-servicio',
  'update-destino',
  'update-recoger-en',
  'update-idioma',
  'update-numero-pax',
  'update-cuando',
  'update-observaciones',
])
</script>
