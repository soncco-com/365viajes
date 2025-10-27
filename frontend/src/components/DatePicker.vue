<template>
  <q-input
    v-model="formattedDate"
    :label="label"
    :outlined="outlined"
    :dense="dense"
    :rules="rules"
    :clearable="clearable"
    readonly
  >
    <template v-slot:prepend>
      <q-icon name="event" class="cursor-pointer">
        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
          <q-date v-model="model" @update:model-value="onUpdate" :mask="mask" :locale="locale">
            <div class="row items-center justify-end">
              <q-btn v-close-popup label="Cerrar" color="primary" flat />
            </div>
          </q-date>
        </q-popup-proxy>
      </q-icon>
    </template>
  </q-input>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },
  label: {
    type: String,
    default: 'Fecha',
  },
  outlined: {
    type: Boolean,
    default: true,
  },
  dense: {
    type: Boolean,
    default: true,
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  rules: {
    type: Array,
    default: () => [],
  },
  mask: {
    type: String,
    default: 'YYYY-MM-DD',
  },
  displayMask: {
    type: String,
    default: 'DD/MM/YYYY',
  },
})

const emit = defineEmits(['update:modelValue'])

const model = ref(props.modelValue)

const formattedDate = computed(() => {
  if (!model.value) return ''

  // Convertir de YYYY-MM-DD a DD/MM/YYYY para mostrar
  if (props.mask === 'YYYY-MM-DD' && props.displayMask === 'DD/MM/YYYY') {
    const parts = model.value.split('-')
    if (parts.length === 3) {
      return `${parts[2]}/${parts[1]}/${parts[0]}`
    }
  }

  return model.value
})

const locale = {
  days: 'Domingo_Lunes_Martes_Miércoles_Jueves_Viernes_Sábado'.split('_'),
  daysShort: 'Dom_Lun_Mar_Mié_Jue_Vie_Sáb'.split('_'),
  months:
    'Enero_Febrero_Marzo_Abril_Mayo_Junio_Julio_Agosto_Septiembre_Octubre_Noviembre_Diciembre'.split(
      '_',
    ),
  monthsShort: 'Ene_Feb_Mar_Abr_May_Jun_Jul_Ago_Sep_Oct_Nov_Dic'.split('_'),
  firstDayOfWeek: 1,
}

const onUpdate = (value) => {
  emit('update:modelValue', value)
}

// Sincronizar con v-model
watch(
  () => props.modelValue,
  (newVal) => {
    model.value = newVal
  },
)
</script>
