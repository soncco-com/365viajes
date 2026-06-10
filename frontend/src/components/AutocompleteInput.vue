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
    :menu-offset="[0, 8]"
    behavior="menu"
    :popup-content-class="'autocomplete-popup'"
  >
    <template v-slot:no-option>
      <q-item v-if="allowCreate && currentSearchText" clickable @click="handleCreateNew">
        <q-item-section avatar>
          <q-icon name="add_circle" color="primary" />
        </q-item-section>
        <q-item-section>
          <q-item-label>Crear "{{ currentSearchText }}"</q-item-label>
          <q-item-label caption>Click para crear nueva opción</q-item-label>
        </q-item-section>
      </q-item>
      <q-item v-else>
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

const emit = defineEmits(['update:modelValue', 'create', 'create-with-text', 'filter'])

const api = useApi()
const model = ref(props.modelValue)
const filteredOptions = ref([])
const allOptions = ref([])
const loading = ref(false)
const currentSearchText = ref('')
const resolvingValue = ref(false)

const findOptionByValue = (value) => {
  if (value === null || value === undefined || value === '') {
    return null
  }

  return allOptions.value.find((option) => option?.id === value) || null
}

const addOptionIfMissing = (option) => {
  if (!option?.id) {
    return
  }

  if (!allOptions.value.some((existingOption) => existingOption?.id === option.id)) {
    allOptions.value = [...allOptions.value, option]
  }

  if (!filteredOptions.value.some((existingOption) => existingOption?.id === option.id)) {
    filteredOptions.value = [...filteredOptions.value, option]
  }
}

const resolveOptionById = async (value) => {
  if (!props.endpoint || value === null || value === undefined || value === '' || resolvingValue.value) {
    return null
  }

  resolvingValue.value = true
  try {
    const response = await api.get(`${props.endpoint}${value}/`)
    const option = response.data
    addOptionIfMissing(option)
    return option
  } catch (error) {
    console.error('Error resolving autocomplete option:', error)
    return null
  } finally {
    resolvingValue.value = false
  }
}

const syncModelValue = async (value) => {
  if (value && typeof value === 'object') {
    model.value = value
    return
  }

  const localOption = findOptionByValue(value)
  if (localOption) {
    model.value = localOption
    return
  }

  model.value = value

  const remoteOption = await resolveOptionById(value)
  if (remoteOption) {
    model.value = remoteOption
  }
}

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
    await syncModelValue(props.modelValue)
  } catch (error) {
    console.error('Error loading autocomplete options:', error)
    allOptions.value = []
    filteredOptions.value = []
  } finally {
    loading.value = false
  }
}

const filterFn = async (val, update, abort) => {
  currentSearchText.value = val

  // Si hay endpoint, buscar en el servidor
  if (props.endpoint) {
    if (val.length < 1) {
      update(() => {
        filteredOptions.value = allOptions.value
      })
      return
    }

    try {
      loading.value = true
      const params = { search: val }
      if (props.filterActivos) {
        params.activo = true
      }

      const response = await api.get(props.endpoint, { params })
      const results = response.data.results || response.data

      update(() => {
        filteredOptions.value = results
      })
    } catch (error) {
      console.error('Error searching options:', error)
      abort()
    } finally {
      loading.value = false
    }
  } else {
    // Filtrado local para opciones estáticas
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
  }

  emit('filter', val)
}

const handleCreateNew = () => {
  emit('create-with-text', currentSearchText.value)
}

const onUpdate = (value) => {
  emit('update:modelValue', value)
}

// Sincronizar con v-model
watch(
  () => props.modelValue,
  (newVal) => {
    syncModelValue(newVal)
  },
)

// Actualizar opciones cuando cambian las props
watch(
  () => props.options,
  (newOptions) => {
    if (!props.endpoint) {
      allOptions.value = newOptions
      filteredOptions.value = newOptions
      syncModelValue(props.modelValue)
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
    syncModelValue(props.modelValue)
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
