<template>
  <q-page class="q-pa-md">
    <page-title title="Usuarios" subtitle="Gestión de usuarios del sistema" />

    <data-table
      :rows="usuarios"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.gt.xs ? 'Nuevo Usuario' : ''"
          @click="openDialog()"
          :class="$q.screen.xs ? 'full-width' : ''"
        />
      </template>

      <template v-slot:body-cell-is_active="props">
        <q-td :props="props">
          <q-badge :color="props.row.is_active ? 'positive' : 'negative'">
            {{ props.row.is_active ? 'Activo' : 'Inactivo' }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-groups="props">
        <q-td :props="props">
          <q-badge v-for="group in props.row.grupos" :key="group.id" color="info" class="q-mr-xs">
            {{ group.name }}
          </q-badge>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense round icon="edit" color="primary" @click="openDialog(props.row)">
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </data-table>

    <q-dialog v-model="showDialog" persistent :maximized="$q.screen.xs">
      <q-card :style="$q.screen.gt.xs ? 'min-width: 700px; max-width: 700px' : ''">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Editar Usuario' : 'Nuevo Usuario' }}</div>
        </q-card-section>

        <q-card-section class="q-pa-md">
          <q-form @submit="saveUsuario" class="q-gutter-md">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-input
                  v-model="form.username"
                  label="Nombre de usuario *"
                  outlined
                  dense
                  :rules="[(val) => !!val || 'Requerido']"
                />
              </div>

              <div class="col-12 col-md-6">
                <q-input v-model="form.email" label="Email" type="email" outlined dense />
              </div>

              <div class="col-12 col-md-6">
                <q-input v-model="form.first_name" label="Nombre" outlined dense />
              </div>

              <div class="col-12 col-md-6">
                <q-input v-model="form.last_name" label="Apellido" outlined dense />
              </div>

              <div class="col-12">
                <q-input
                  v-model="form.password"
                  label="Contraseña"
                  type="password"
                  outlined
                  dense
                  :rules="isEditing ? [] : [(val) => !!val || 'Requerido']"
                  :hint="isEditing ? 'Dejar vacío para no cambiar' : ''"
                />
              </div>

              <div class="col-12">
                <q-select
                  v-model="form.groups"
                  :options="grupos"
                  option-value="id"
                  option-label="name"
                  label="Grupos"
                  outlined
                  dense
                  multiple
                  emit-value
                  map-options
                  use-chips
                />
              </div>

              <div class="col-12 col-md-6">
                <q-toggle v-model="form.is_active" label="Activo" />
              </div>

              <div class="col-12 col-md-6">
                <q-toggle v-model="form.is_staff" label="Staff (acceso admin)" />
              </div>
            </div>

            <div class="row q-gutter-sm justify-end q-mt-md">
              <q-btn label="Cancelar" color="grey" flat @click="showDialog = false" />
              <q-btn label="Guardar" type="submit" color="primary" :loading="saving" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useNotify } from 'src/composables/useNotify'
import { useQuasar } from 'quasar'
import PageTitle from 'src/components/PageTitle.vue'
import DataTable from 'src/components/DataTable.vue'

const $q = useQuasar()
const api = useApi()
const { notifySuccess, notifyError } = useNotify()

const usuarios = ref([])
const grupos = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  groups: [],
  is_active: true,
  is_staff: false,
})

const columns = [
  { name: 'username', label: 'Usuario', field: 'username', align: 'left', sortable: true },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'first_name', label: 'Nombre', field: 'first_name', align: 'left' },
  { name: 'last_name', label: 'Apellido', field: 'last_name', align: 'left' },
  { name: 'groups', label: 'Grupos', field: 'groups', align: 'left' },
  { name: 'is_active', label: 'Estado', field: 'is_active', align: 'center', sortable: true },
  { name: 'actions', label: 'Acciones', field: 'actions', align: 'center' },
]

const pagination = ref({
  sortBy: 'username',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
})

const loadUsuarios = async (props) => {
  loading.value = true
  try {
    const { page, rowsPerPage, sortBy, descending } = props?.pagination || pagination.value
    const params = { page, page_size: rowsPerPage, ordering: (descending ? '-' : '') + sortBy }
    const response = await api.get('base/usuarios/', { params })
    usuarios.value = response.data.results
    pagination.value = {
      ...pagination.value,
      page,
      rowsPerPage,
      sortBy,
      descending,
      rowsNumber: response.data.count,
    }
  } finally {
    loading.value = false
  }
}

const loadGrupos = async () => {
  try {
    const response = await api.get('base/grupos/')
    grupos.value = response.data
  } catch {
    notifyError('Error al cargar grupos')
  }
}

const onRequest = (props) => loadUsuarios(props)

const openDialog = (usuario = null) => {
  isEditing.value = !!usuario
  if (usuario) {
    form.value = {
      id: usuario.id,
      username: usuario.username,
      email: usuario.email || '',
      first_name: usuario.first_name || '',
      last_name: usuario.last_name || '',
      password: '',
      groups: usuario.grupos?.map((g) => g.id) || [],
      is_active: usuario.is_active,
      is_staff: usuario.is_staff,
    }
  } else {
    form.value = {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      groups: [],
      is_active: true,
      is_staff: false,
    }
  }
  showDialog.value = true
}

const saveUsuario = async () => {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (isEditing.value && !payload.password) {
      delete payload.password
    }

    if (isEditing.value) {
      await api.put(`base/usuarios/${form.value.id}/`, payload)
      notifySuccess('Usuario actualizado')
    } else {
      await api.post('base/usuarios/', payload)
      notifySuccess('Usuario creado')
    }
    showDialog.value = false
    loadUsuarios()
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadUsuarios()
  loadGrupos()
})
</script>
