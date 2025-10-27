<template>
  <q-select
    v-model="model"
    :options="filteredOptions"
    :label="label"
    :loading="loading"
    :outlined="outlined"
    :dense="dense"
    :clearable="clearable"
    :rules="rules"
    :use-input="useInput"
    :input-debounce="inputDebounce"
    @filter="filterFn"
    @update:model-value="onUpdate"
    option-value="id"
    :option-label="optionLabel"
    emit-value
    map-options
    :behavior="behavior"
  >
    <template v-slot:no-option>
      <q-item>
        <q-item-section class="text-grey">
          {{ noOptionsText }}
        </q-item-section>
      </q-item>
    </template>

    <template v-if="allowCreate" v-slot:append>
      <q-btn flat dense icon="add" color="primary" @click.stop="$emit('create')">
        <q-tooltip>Crear nuevo</q-tooltip>
      </q-btn>
    </template>

    <template v-if="$slots.option" v-slot:option="scope">
      <slot name="option" v-bind="scope"></slot>
    </template>
  </q-select>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Number, String, Object],
    default: null,
  },
  label: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    default: () => [],
  },
  optionLabel: {
    type: String,
    default: 'nombre',
  },
  loading: {
    type: Boolean,
    default: false,
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
  useInput: {
    type: Boolean,
    default: true,
  },
  inputDebounce: {
    type: Number,
    default: 300,
  },
  allowCreate: {
    type: Boolean,
    default: false,
  },
  noOptionsText: {
    type: String,
    default: 'Sin opciones',
  },
  behavior: {
    type: String,
    default: 'dialog',
  },
})

const emit = defineEmits(['update:modelValue', 'create', 'filter'])

const model = ref(props.modelValue)
const filteredOptions = ref(props.options)

const filterFn = (val, update) => {
  update(() => {
    if (val === '') {
      filteredOptions.value = props.options
    } else {
      const needle = val.toLowerCase()
      filteredOptions.value = props.options.filter(
        (v) => v[props.optionLabel].toLowerCase().indexOf(needle) > -1,
      )
    }
  })

  emit('filter', val)
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

// Actualizar opciones cuando cambian
watch(
  () => props.options,
  (newOptions) => {
    filteredOptions.value = newOptions
  },
)

onMounted(() => {
  filteredOptions.value = props.options
})
</script>
