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
    use-input
    :input-debounce="inputDebounce"
    @filter="filterFn"
    @update:model-value="onUpdate"
    option-value="id"
    :option-label="optionLabel"
    emit-value
    map-options
    fill-input
    :menu-offset="[0, 8]"
    behavior="menu"
    :popup-content-class="'autocomplete-popup'"
  >
    <template v-slot:no-option>
      <q-item>
        <q-item-section class="text-grey">
          {{ noOptionsText }}
        </q-item-section>
      </q-item>
    </template>

    <template v-if="allowCreate" v-slot:after>
      <q-btn flat dense round icon="add" color="primary" @click.stop="$emit('create')" size="sm">
        <q-tooltip>Crear nuevo</q-tooltip>
      </q-btn>
    </template>

    <template v-slot:option="scope">
      <q-item v-bind="scope.itemProps">
        <q-item-section>
          <q-item-label>{{ scope.opt[optionLabel] }}</q-item-label>
          <q-item-label v-if="optionSubLabel && scope.opt[optionSubLabel]" caption>
            {{ scope.opt[optionSubLabel] }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </template>
  </q-select>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'

const props = defineProps({
  modelValue: {
    type: [Number, String, Object],
    default: null,
  },
  label: {
    type: String,
    required: true,
  },
  endpoint: {
    type: String,
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
  },
  optionLabel: {
    type: String,
    default: 'nombre',
  },
  optionSubLabel: {
    type: String,
    default: null,
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
  filterActivos: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue', 'create', 'filter'])

const api = useApi()
const model = ref(props.modelValue)
const filteredOptions = ref([])
const allOptions = ref([])
const loading = ref(false)

const loadOptions = async () => {
  if (!props.endpoint) {
    allOptions.value = props.options
    filteredOptions.value = props.options
    return
  }

  loading.value = true
  try {
    const params = {}
    if (props.filterActivos) {
      params.activo = true
    }

    const response = await api.get(props.endpoint, { params })
    allOptions.value = response.data.results || response.data
    filteredOptions.value = allOptions.value
  } catch (error) {
    console.error('Error loading autocomplete options:', error)
    allOptions.value = []
    filteredOptions.value = []
  } finally {
    loading.value = false
  }
}

const filterFn = (val, update) => {
  update(() => {
    if (val === '') {
      filteredOptions.value = allOptions.value
    } else {
      const needle = val.toLowerCase()
      filteredOptions.value = allOptions.value.filter(
        (v) => v[props.optionLabel] && v[props.optionLabel].toLowerCase().indexOf(needle) > -1,
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

// Actualizar opciones cuando cambian las props
watch(
  () => props.options,
  (newOptions) => {
    if (!props.endpoint) {
      allOptions.value = newOptions
      filteredOptions.value = newOptions
    }
  },
)

// Recargar si el endpoint cambia
watch(
  () => props.endpoint,
  () => {
    if (props.endpoint) {
      loadOptions()
    }
  },
)

onMounted(() => {
  if (props.endpoint) {
    loadOptions()
  } else {
    allOptions.value = props.options
    filteredOptions.value = props.options
  }
})

// Exponer método para recargar opciones
defineExpose({
  reload: loadOptions,
})
</script>

<style lang="scss">
.autocomplete-popup {
  max-height: 300px;
}
</style>
