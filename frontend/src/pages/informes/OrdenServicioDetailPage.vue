<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <q-btn flat dense round icon="arrow_back" @click="$router.back()" class="q-mr-md" />
      <page-title
        title="Detalle de Orden de Servicio"
        :subtitle="`Orden #${ordenId} - ${formatDate(orden?.fecha)}`"
      />
    </div>

    <q-card v-if="orden" class="q-mb-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-3">
            <div class="text-grey-7">Servicio</div>
            <div class="text-h6">{{ orden.servicio_nombre }}</div>
          </div>
          <div class="col-12 col-md-2">
            <div class="text-grey-7">Idioma</div>
            <div class="text-h6">{{ orden.idioma_display }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-grey-7">Guía</div>
            <div class="text-h6">{{ orden.guia_nombre }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-grey-7">Conductor</div>
            <div class="text-h6">{{ orden.chofer_nombre }}</div>
          </div>
          <div class="col-12 col-md-3">
            <div class="text-grey-7">Responsable</div>
            <div class="text-h6">{{ orden.responsable_nombre || 'No asignado' }}</div>
          </div>
        </div>
        <div class="row q-col-gutter-md q-mt-md" v-if="orden.observaciones">
          <div class="col-12">
            <div class="text-grey-7">Observaciones</div>
            <div class="text-body1">{{ orden.observaciones }}</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">Detalles de Reservas ({{ orden?.detalles?.length || 0 }})</div>
        <q-table
          ref="tableRef"
          :rows="orden?.detalles || []"
          :columns="columns"
          row-key="id"
          flat
          bordered
          dense
          :loading="loading"
          :pagination="{ rowsPerPage: 0 }"
          hide-pagination
          no-data-label="No hay detalles"
        >
          <template v-slot:body="props">
            <q-tr :props="props" :data-id="props.row.id" class="sortable-row cursor-grab">
              <q-td key="drag" :props="props" class="drag-handle">
                <q-icon name="drag_indicator" size="sm" color="grey-6" />
              </q-td>
              <q-td
                v-for="column in serviceColumns"
                :key="column.name"
                :props="props"
                :class="getColumnClass(column)"
                :style="column.style"
              >
                {{ getColumnValue(props.row, column) }}
              </q-td>
              <q-td key="actions" :props="props" class="text-center">
                <q-btn
                  flat
                  dense
                  round
                  icon="delete"
                  color="negative"
                  @click="deleteDetalle(props.row)"
                  :disable="(orden?.detalles?.length || 0) <= 1"
                >
                  <q-tooltip>
                    {{
                      (orden?.detalles?.length || 0) <= 1
                        ? 'Debe quedar al menos un detalle'
                        : 'Eliminar detalle'
                    }}
                  </q-tooltip>
                </q-btn>
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import Sortable from 'sortablejs'
import { formatDateOnly as formatDate } from 'src/utils/date'

const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const ordenId = ref(route.params.id)
const orden = ref(null)
const configuredColumns = ref([])
const loading = ref(false)
const tableRef = ref(null)
let sortableInstance = null

const defaultServiceColumns = [
  { clave: 'pax', etiqueta: 'PAX', ancho: 5, orden: 0, visible: true },
  { clave: 'hotel', etiqueta: 'Hotel', ancho: 18, orden: 1, visible: true },
  { clave: 'pasajero', etiqueta: 'Pasajero', ancho: 20, orden: 2, visible: true },
  { clave: 'agencia', etiqueta: 'Agencia', ancho: 14, orden: 3, visible: true },
  { clave: 'destino', etiqueta: 'Destino', ancho: 12, orden: 4, visible: true },
  { clave: 'ingresos', etiqueta: 'Ingresos', ancho: 7, orden: 5, visible: true },
  { clave: 'almuerzo', etiqueta: 'Almuerzo', ancho: 7, orden: 6, visible: true },
  { clave: 'adicionales', etiqueta: 'Adicionales', ancho: 12, orden: 7, visible: true },
  { clave: 'observaciones', etiqueta: 'Obs.', ancho: 10, orden: 8, visible: true },
]

const serviceColumns = computed(() => {
  const source = configuredColumns.value.length ? configuredColumns.value : defaultServiceColumns
  return [...source]
    .filter((column) => column.visible)
    .sort((a, b) => a.orden - b.orden)
    .map((column) => {
      const isCentered = ['pax', 'ingresos', 'almuerzo'].includes(column.clave)
      return {
        name: column.clave,
        label: column.etiqueta,
        field: (row) => row.column_values?.[column.clave] || '',
        align: isCentered ? 'center' : 'left',
        style: `width: ${column.ancho}%; max-width: ${column.ancho}%; white-space: pre-line;`,
        headerStyle: `width: ${column.ancho}%; max-width: ${column.ancho}%;`,
      }
    })
})

const columns = computed(() => [
  {
    name: 'drag',
    label: '',
    field: 'drag',
    align: 'center',
    style: 'width: 40px',
    headerStyle: 'width: 40px',
  },
  ...serviceColumns.value,
  {
    name: 'actions',
    label: 'Acciones',
    field: 'actions',
    align: 'center',
    style: 'width: 80px',
    headerStyle: 'width: 80px',
  },
])

const getColumnValue = (row, column) => {
  const value = row.column_values?.[column.name]
  return value === null || value === undefined || value === '' ? '-' : value
}

const getColumnClass = (column) => ({
  'text-center': column.align === 'center',
  'column-value': true,
})

const loadColumnas = async (servicioId) => {
  configuredColumns.value = []
  if (!servicioId) return

  const response = await api.get('base/orden-servicio-columnas/', {
    params: { servicio: servicioId, visible: true, page_size: 20 },
  })

  if (!response.success) {
    notifyError('Error al cargar configuración de columnas')
    return
  }

  configuredColumns.value = response.data.results ?? response.data
}

const destroySortable = () => {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
}

const initSortable = () => {
  destroySortable()
  nextTick(() => {
    const tbody = tableRef.value?.$el?.querySelector('tbody')
    if (!tbody) return

    sortableInstance = Sortable.create(tbody, {
      animation: 150,
      handle: '.drag-handle',
      ghostClass: 'sortable-ghost',
      onEnd: async (evt) => {
        if (evt.oldIndex === evt.newIndex) return

        const orderedIds = Array.from(tbody.querySelectorAll('tr.sortable-row'))
          .map((row) => row.dataset.id)
          .filter(Boolean)

        const detallesById = new Map(
          orden.value.detalles.map((detalle) => [String(detalle.id), detalle]),
        )
        const detalles = orderedIds.map((id) => detallesById.get(id)).filter(Boolean)

        if (detalles.length !== orden.value.detalles.length) {
          notifyError('No se pudo determinar el nuevo orden')
          await loadOrden()
          return
        }

        // Guardar en backend
        try {
          const response = await api.post(
            `reservas/ordenes-servicio/${ordenId.value}/reordenar/`,
            {
              detalle_ids: detalles.map((d) => d.id),
            },
          )
          if (!response.success) {
            throw response.error
          }
          orden.value.detalles = detalles
        } catch (error) {
          console.error(error)
          notifyError('Error al guardar el orden')
          await loadOrden()
        }
      },
    })
  })
}

watch(
  () => orden.value?.detalles,
  () => initSortable(),
  { flush: 'post' },
)

const loadOrden = async () => {
  loading.value = true
  try {
    const response = await api.get(`reservas/ordenes-servicio/${ordenId.value}/`)
    orden.value = response.data
    await loadColumnas(response.data?.servicio)
  } catch (error) {
    console.error(error)
    notifyError('Error al cargar la orden')
    router.back()
  } finally {
    loading.value = false
  }
}

const deleteDetalle = async (detalle) => {
  if ((orden.value?.detalles?.length || 0) <= 1) {
    notifyError('Debe quedar al menos un detalle en la orden')
    return
  }

  if (
    !(await confirm(
      '¿Eliminar este detalle de la orden? La reserva quedará disponible para asignación.',
      'Confirmar eliminación',
    ))
  ) {
    return
  }

  loading.value = true
  try {
    await api.delete(`reservas/ordenes-servicio/${ordenId.value}/eliminar_detalle/`, {
      data: { detalle_id: detalle.id },
    })
    notifySuccess('Detalle eliminado correctamente')
    await loadOrden()
  } catch (error) {
    console.error(error)
    notifyError('Error al eliminar el detalle')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOrden()
})

onBeforeUnmount(() => {
  destroySortable()
})
</script>

<style scoped>
.drag-handle {
  cursor: grab;
}
.drag-handle:active {
  cursor: grabbing;
}
.sortable-ghost {
  opacity: 0.4;
  background: #e3f2fd;
}
.cursor-grab {
  cursor: default;
}
</style>
