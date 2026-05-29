<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <q-btn flat dense round icon="arrow_back" @click="$router.back()" class="q-mr-md" />
      <page-title
        title="Detalle de Orden de Servicio"
        :subtitle="`Orden #${ordenId} - ${orden?.fecha || ''}`"
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
            <div class="text-grey-7">Chofer</div>
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
              <q-td key="reserva_id" :props="props">
                {{ props.row.reserva_detalle_info?.reserva_id }}
              </q-td>
              <q-td key="fecha" :props="props">
                {{ formatDate(props.row.reserva_detalle_info?.cuando) }}
              </q-td>
              <q-td key="pasajero" :props="props">
                {{ props.row.reserva_detalle_info?.reserva_pasajero }}
              </q-td>
              <q-td key="lugar" :props="props">
                {{ props.row.reserva_detalle_info?.lugar_nombre }}
              </q-td>
              <q-td key="numero_pax" :props="props" class="text-center">
                {{ props.row.reserva_detalle_info?.numero_pax }}
              </q-td>
              <q-td key="idioma" :props="props" class="text-center">
                {{ props.row.reserva_detalle_info?.idioma_display }}
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
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'
import Sortable from 'sortablejs'

const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const ordenId = ref(route.params.id)
const orden = ref(null)
const loading = ref(false)
const tableRef = ref(null)
let sortableInstance = null

const columns = [
  {
    name: 'drag',
    label: '',
    field: 'drag',
    align: 'center',
    style: 'width: 40px',
  },
  {
    name: 'reserva_id',
    label: 'ID Reserva',
    field: (row) => row.reserva_detalle_info?.reserva_id,
    align: 'left',
  },
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'fecha',
    align: 'left',
  },
  {
    name: 'pasajero',
    label: 'Pasajero',
    field: (row) => row.reserva_detalle_info?.reserva_pasajero,
    align: 'left',
  },
  {
    name: 'lugar',
    label: 'Lugar Recojo',
    field: (row) => row.reserva_detalle_info?.lugar_nombre,
    align: 'left',
  },
  {
    name: 'numero_pax',
    label: 'PAX',
    field: (row) => row.reserva_detalle_info?.numero_pax,
    align: 'center',
  },
  {
    name: 'idioma',
    label: 'Idioma',
    field: (row) => row.reserva_detalle_info?.idioma_display,
    align: 'center',
  },
  {
    name: 'actions',
    label: 'Acciones',
    field: 'actions',
    align: 'center',
  },
]

const initSortable = () => {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
  nextTick(() => {
    const tbody = tableRef.value?.$el?.querySelector('tbody')
    if (!tbody) return
    sortableInstance = Sortable.create(tbody, {
      animation: 150,
      handle: '.drag-handle',
      ghostClass: 'sortable-ghost',
      onEnd: async (evt) => {
        if (evt.oldIndex === evt.newIndex) return
        // Reordenar el array local
        const detalles = [...orden.value.detalles]
        const [moved] = detalles.splice(evt.oldIndex, 1)
        detalles.splice(evt.newIndex, 0, moved)
        orden.value.detalles = detalles
        // Guardar en backend
        try {
          await api.post(`reservas/ordenes-servicio/${ordenId.value}/reordenar/`, {
            detalle_ids: detalles.map((d) => d.id),
          })
        } catch (error) {
          console.error(error)
          notifyError('Error al guardar el orden')
          await loadOrden()
        }
        initSortable()
      },
    })
  })
}

watch(
  () => orden.value?.detalles,
  () => initSortable(),
  { flush: 'post' },
)

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const [year, month, day] = dateStr.split('-')
  return `${day}/${month}/${year}`
}

const loadOrden = async () => {
  loading.value = true
  try {
    const response = await api.get(`reservas/ordenes-servicio/${ordenId.value}/`)
    orden.value = response.data
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
