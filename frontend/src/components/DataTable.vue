<template>
  <q-table
    :rows="rows"
    :columns="columns"
    :loading="loading"
    :filter="filter"
    :pagination="pagination"
    @request="onRequest"
    row-key="id"
    binary-state-sort
    flat
    bordered
    class="data-table-custom"
  >
    <!-- Slot para filtros personalizados -->
    <template v-slot:top>
      <div class="row q-gutter-md full-width items-center">
        <slot name="filters"></slot>

        <q-space />

        <!-- Buscador por defecto -->
        <q-input
          v-if="searchable"
          v-model="filter"
          dense
          debounce="300"
          placeholder="Buscar..."
          outlined
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>

        <!-- Slot personalizado para botones en la parte superior derecha -->
        <slot name="top-right"></slot>

        <!-- Botón de crear (si no se usa el slot top-right) -->
        <q-btn
          v-if="createButton && !$slots['top-right']"
          color="primary"
          icon="add"
          :label="createLabel"
          @click="$emit('create')"
        />
      </div>
    </template>

    <!-- Slot para acciones por fila -->
    <template v-slot:body-cell-actions="props">
      <q-td :props="props">
        <slot name="actions" :row="props.row">
          <q-btn-dropdown flat dense icon="more_vert" dropdown-icon="none">
            <q-list>
              <q-item
                v-if="!props.row.hideEdit"
                clickable
                v-close-popup
                @click="$emit('edit', props.row)"
              >
                <q-item-section avatar>
                  <q-icon name="edit" color="primary" />
                </q-item-section>
                <q-item-section>Editar</q-item-section>
              </q-item>

              <q-item
                v-if="!props.row.hideDelete"
                clickable
                v-close-popup
                @click="$emit('delete', props.row)"
              >
                <q-item-section avatar>
                  <q-icon name="delete" color="negative" />
                </q-item-section>
                <q-item-section>Eliminar</q-item-section>
              </q-item>

              <slot name="extra-actions" :row="props.row"></slot>
            </q-list>
          </q-btn-dropdown>
        </slot>
      </q-td>
    </template>

    <!-- Slots para personalización de celdas -->
    <template
      v-for="slot in Object.keys($slots).filter((name) => name.startsWith('body-cell-'))"
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
  initialPagination: {
    type: Object,
    default: () => ({
      sortBy: null,
      descending: false,
      page: 1,
      rowsPerPage: 10,
    }),
  },
})

const emit = defineEmits(['request', 'create', 'edit', 'delete', 'update:filter'])

const filter = ref('')
const pagination = ref(props.initialPagination)

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
