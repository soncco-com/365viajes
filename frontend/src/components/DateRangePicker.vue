<template>
  <div class="row q-gutter-md">
    <DatePicker
      v-model="desde"
      label="Desde"
      :outlined="outlined"
      :dense="dense"
      @update:model-value="onUpdateDesde"
      class="col"
    />

    <DatePicker
      v-model="hasta"
      label="Hasta"
      :outlined="outlined"
      :dense="dense"
      @update:model-value="onUpdateHasta"
      class="col"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import DatePicker from './DatePicker.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ desde: null, hasta: null }),
  },
  outlined: {
    type: Boolean,
    default: true,
  },
  dense: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const desde = ref(props.modelValue?.desde || null)
const hasta = ref(props.modelValue?.hasta || null)

const emitUpdate = () => {
  emit('update:modelValue', {
    desde: desde.value,
    hasta: hasta.value,
  })
}

const onUpdateDesde = (value) => {
  desde.value = value
  emitUpdate()
}

const onUpdateHasta = (value) => {
  hasta.value = value
  emitUpdate()
}

// Sincronizar con v-model
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      desde.value = newVal.desde
      hasta.value = newVal.hasta
    }
  },
  { deep: true },
)
</script>
