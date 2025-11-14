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
          <div class="col-12 col-md-4">
            <div class="text-grey-7">Chofer</div>
            <div class="text-h6">{{ orden.chofer_nombre }}</div>
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
          <template v-slot:body-cell-fecha="props">
            <q-td :props="props">
              {{ formatDate(props.row.reserva_detalle_info?.cuando) }}
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
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
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import PageTitle from 'src/components/PageTitle.vue'

const route = useRoute()
const router = useRouter()
const api = useApi()
const { notifySuccess, notifyError, confirm } = useNotify()

const ordenId = ref(route.params.id)
const orden = ref(null)
const loading = ref(false)

const columns = [
  {
    name: 'reserva_id',
    label: 'ID Reserva',
    field: (row) => row.reserva_detalle_info?.reserva_id,
    align: 'left',
  },
  {
    name: 'reserva_numero',
    label: 'Número Reserva',
    field: (row) => row.reserva_detalle_info?.pertenece_a,
    align: 'left',
  },
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'fecha',
    align: 'left',
  },
  {
    name: 'servicio',
    label: 'Servicio',
    field: (row) => row.reserva_detalle_info?.servicio_nombre,
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
