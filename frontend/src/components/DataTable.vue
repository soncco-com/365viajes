<template>
  <q-table
    v-model:pagination="internalPagination"
    :rows="rows"
    :columns="columns"
    :loading="loading"
    :filter="filter"
    :rows-number="rowsNumber"
    @request="onRequest"
    row-key="id"
    binary-state-sort
    flat
    bordered
    :grid="$q.screen.lt.md"
    class="data-table-custom"
    :no-data-label="noDataLabel"
  >
    <!-- Slot para filtros personalizados -->
    <template v-slot:top>
      <div class="row full-width items-center">
        <div
          class="col-12"
          v-if="$slots.filters || searchable || $slots['top-right'] || createButton"
        >
          <div class="row q-col-gutter-md items-center">
            <!-- Filtros personalizados -->
            <div v-if="$slots.filters" class="col-12 col-md">
              <slot name="filters"></slot>
            </div>

            <!-- Buscador por defecto -->
            <div v-if="searchable" class="col-12 col-md-auto">
              <q-input
                v-model="filter"
                dense
                debounce="300"
                placeholder="Buscar..."
                outlined
                style="min-width: 200px"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>

            <!-- Slot personalizado para botones en la parte superior derecha -->
            <div v-if="$slots['top-right'] || createButton" class="col-12 col-md-auto">
              <slot name="top-right">
                <!-- Botón de crear (si no se usa el slot top-right) -->
                <q-btn
                  v-if="createButton"
                  color="primary"
                  icon="add"
                  :label="$q.screen.gt.xs ? createLabel : ''"
                  @click="$emit('create')"
                  :class="$q.screen.xs ? 'full-width' : ''"
                />
              </slot>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Vista GRID para móviles -->
    <template v-slot:item="props">
      <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4">
        <q-card flat bordered>
          <q-card-section>
            <slot name="grid-item" :row="props.row" :cols="props.cols">
              <!-- Layout por defecto si no se personaliza -->
              <div v-for="col in props.cols.filter((c) => c.name !== 'actions')" :key="col.name">
                <div class="text-caption text-grey-7">{{ col.label }}</div>
                <div class="text-body2 q-mb-sm">
                  <!-- Renderizar slots personalizados para badges/etc -->
                  <component
                    :is="$slots[`body-cell-${col.name}`] ? 'div' : col.format ? 'div' : 'span'"
                  >
                    <slot
                      :name="`body-cell-${col.name}`"
                      :row="props.row"
                      :value="col.value"
                      :props="{ row: props.row, value: col.value }"
                    >
                      {{ col.value }}
                    </slot>
                  </component>
                </div>
              </div>
            </slot>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <!-- Renderizar los botones de acción del slot body-cell-actions -->
            <slot name="body-cell-actions" :row="props.row" :rowIndex="props.rowIndex">
              <q-btn flat dense round icon="edit" color="primary">
                <q-tooltip>Editar</q-tooltip>
              </q-btn>
            </slot>
          </q-card-actions>
        </q-card>
      </div>
    </template>

    <!-- Slot para acciones por fila (tabla desktop) -->
    <template v-slot:body-cell-actions="slotProps">
      <slot name="body-cell-actions" v-bind="slotProps"></slot>
    </template>

    <!-- Slots para personalización de celdas (tabla desktop) -->
    <template
      v-for="slot in Object.keys($slots).filter(
        (name) => name.startsWith('body-cell-') && name !== 'body-cell-actions',
      )"
      v-slot:[slot]="props"
    >
      <slot :name="slot" v-bind="props"></slot>
    </template>

    <!-- Slot para totales -->
    <template v-if="showTotals" v-slot:bottom-row>
      <slot name="totals"></slot>
    </template>
  </q-table>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  createButton: {
    type: Boolean,
    default: false,
  },
  createLabel: {
    type: String,
    default: 'Crear',
  },
  showTotals: {
    type: Boolean,
    default: false,
  },
  noDataLabel: {
    type: String,
    default: 'No hay registros disponibles',
  },
  initialPagination: {
    type: Object,
    default: () => ({
      sortBy: null,
      descending: false,
      page: 1,
      rowsPerPage: 10,
      rowsNumber: 0,
    }),
  },
  pagination: {
    type: Object,
    default: null,
  },
  rowsNumber: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['request', 'create', 'edit', 'delete', 'update:filter'])

const filter = ref('')
const internalPagination = ref({ ...props.initialPagination })

// Sincronizar paginación interna con la prop cuando cambie
watch(
  () => props.pagination,
  (newVal) => {
    if (newVal) {
      internalPagination.value = { ...newVal }
    }
  },
  { deep: true, immediate: true },
)

const onRequest = (requestProps) => {
  emit('request', requestProps)
}

// Emitir cambios en el filtro
watch(filter, (newVal) => {
  emit('update:filter', newVal)
})
</script>

<style lang="scss" scoped>
.data-table-custom {
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
}
</style>
