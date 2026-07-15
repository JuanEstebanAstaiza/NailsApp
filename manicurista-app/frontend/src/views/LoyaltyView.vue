<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Fidelización</h1>
      <button
        @click="showCreateModal = true"
        class="bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Nueva Regla
      </button>
    </div>

    <!-- Loyalty Types Info -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div class="bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl border border-pink-200 p-5">
        <h3 class="font-semibold text-gray-800 mb-2 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-pink-500" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          Punch Card (Tarjeta de Sellos)
        </h3>
        <p class="text-sm text-gray-600">Clienta gana un sello por cada cita. Después de X citas, obtiene una recompensa.</p>
      </div>

      <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-200 p-5">
        <h3 class="font-semibold text-gray-800 mb-2 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
            <path d="M8 16.028a1 1 0 100 1.944 1 1 0 000-1.944zM7 15a3 3 0 100-6 3 3 0 000 6zM12 15a3 3 0 100-6 3 3 0 000 6zM11.944 8A1 1 0 1013.888 8a1 1 0 00-1.944 0z" />
          </svg>
          Rebooking Incentive
        </h3>
        <p class="text-sm text-gray-600">Clienta obtiene descuento si rebook dentro de un window específico después de su última cita.</p>
      </div>

      <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200 p-5">
        <h3 class="font-semibold text-gray-800 mb-2 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267C11.93 11.66 12 11.886 12 12s-.07.34-.433.582zM11 15.849v-1.698c.22.071.412.164.567.267C11.93 14.66 12 14.886 12 15s-.07.34-.433.582zM8 12a2 2 0 114 0H8z" />
          </svg>
          Points-Based (Puntos)
        </h3>
        <p class="text-sm text-gray-600">Clienta gana puntos por cada servicio. Acumula puntos para recompensas.</p>
      </div>
    </div>

    <!-- Loyalty Rules List -->
    <div class="space-y-4">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">Reglas Activas</h2>

      <div
        v-for="rule in rules"
        :key="rule.id"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow"
      >
        <!-- Rule header -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <!-- Type badge -->
            <span
              class="px-3 py-1 rounded-full text-xs font-semibold"
              :class="{
                'bg-pink-100 text-pink-700': rule.type === 'punch-card',
                'bg-blue-100 text-blue-700': rule.type === 'rebooking',
                'bg-green-100 text-green-700': rule.type === 'points',
                'bg-purple-100 text-purple-700': rule.type === 'tiered'
              }"
            >
              {{ getTypeLabel(rule.type) }}
            </span>

            <!-- Global vs Client-specific -->
            <span
              class="px-2 py-1 rounded-full text-xs font-medium"
              :class="rule.client_id ? 'bg-gray-100 text-gray-600' : 'bg-yellow-100 text-yellow-700'"
            >
              {{ rule.client_id ? 'Para clienta específica' : 'Global (todas las clientas)' }}
            </span>

            <!-- Client name if specific -->
            <span v-if="rule.client_id" class="text-sm text-gray-600">
              → {{ getClientName(rule.client_id) }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="editRule(rule)"
              class="text-blue-500 hover:text-blue-600 text-sm flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
            <button
              @click="deleteRule(rule)"
              class="text-red-500 hover:text-red-600 text-sm flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Rule details -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <p class="text-xs text-gray-500 mb-1">Trigger</p>
            <p class="text-sm font-medium text-gray-800">{{ rule.trigger_count }} citas</p>
          </div>

          <div v-if="rule.service_filter_name">
            <p class="text-xs text-gray-500 mb-1">Servicio</p>
            <p class="text-sm font-medium text-gray-800">{{ rule.service_filter_name }}</p>
          </div>

          <div>
            <p class="text-xs text-gray-500 mb-1">Recompensa</p>
            <p class="text-sm font-medium text-gray-800">{{ getRewardLabel(rule) }}</p>
          </div>

          <div v-if="rule.type === 'rebooking' && rule.rebooking_days">
            <p class="text-xs text-gray-500 mb-1">Window</p>
            <p class="text-sm font-medium text-gray-800">{{ rule.rebooking_days }} días</p>
          </div>
        </div>

        <!-- Progress bar for punch-card -->
        <div v-if="rule.type === 'punch-card' && getClientProgress(rule.client_id)" class="mt-3">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-gray-500">Progreso</span>
            <span class="text-xs font-medium text-pink-600">{{ getClientProgress(rule.client_id) }}/{{ rule.trigger_count }}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-gradient-to-r from-pink-400 to-pink-600 h-2 rounded-full transition-all"
              :style="{ width: `${(getClientProgress(rule.client_id) / rule.trigger_count) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Rebooking eligibility -->
        <div v-if="rule.type === 'rebooking' && getRebookingStatus(rule.client_id)" class="mt-3">
          <span
            class="text-xs font-medium px-2 py-1 rounded-full"
            :class="getRebookingStatus(rule.client_id) === 'Eligible' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
          >
            {{ getRebookingStatus(rule.client_id) }}
          </span>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-if="rules.length === 0"
        class="text-center py-12 bg-white rounded-xl border border-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        <p class="text-gray-500 text-lg">No hay reglas de fidelización configuradas</p>
        <button
          @click="showCreateModal = true"
          class="mt-4 bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Crear primera regla
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || showEditModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeModals()"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg">
        <h2 class="text-xl font-bold text-gray-800 mb-4">
          {{ showEditModal ? 'Editar Regla' : 'Nueva Regla de Fidelización' }}
        </h2>

        <!-- Type -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
          <select
            v-model="form.type"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          >
            <option value="">Seleccionar tipo</option>
            <option value="punch-card">Punch Card (Tarjeta de Sellos)</option>
            <option value="rebooking">Rebooking Incentive</option>
            <option value="points">Points-Based (Puntos)</option>
          </select>
        </div>

        <!-- Global vs Client-specific -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Aplicar a</label>
          <select
            v-model="form.client_id"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          >
            <option :value="null">Global (todas las clientas)</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.name }}
            </option>
          </select>
        </div>

        <!-- Trigger Count -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Número de citas necesarias</label>
          <input
            v-model.number="form.trigger_count"
            type="number"
            placeholder="8"
            min="1"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>

        <!-- Service Filter -->
        <div v-if="form.type === 'punch-card'" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Servicio (opcional - dejar vacío para todos)</label>
          <select
            v-model="form.service_filter"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          >
            <option :value="null">Todos los servicios</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>

        <!-- Reward Type -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de recompensa</label>
          <select
            v-model="form.reward_type"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          >
            <option value="">Seleccionar tipo</option>
            <option value="discount">Descuento (%)</option>
            <option value="free-service">Servicio Gratis</option>
            <option value="upgrade">Upgrade (valor fijo)</option>
          </select>
        </div>

        <!-- Reward Value -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Valor de recompensa</label>
          <input
            v-model.number="form.reward_value"
            type="number"
            placeholder="15.0"
            min="0"
            step="0.5"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>

        <!-- Rebooking Days -->
        <div v-if="form.type === 'rebooking'" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Window de rebooking (días)</label>
          <input
            v-model.number="form.rebooking_days"
            type="number"
            placeholder="7"
            min="1"
            max="30"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 justify-end">
          <button
            @click="closeModals()"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="showEditModal ? updateRule() : createRule()"
            class="px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded-lg transition-colors"
          >
            {{ showEditModal ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showDeleteModal = false"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm">
        <h2 class="text-lg font-bold text-gray-800 mb-2">Eliminar Regla</h2>
        <p class="text-gray-600 mb-4">¿Estás segura de eliminar esta regla de fidelización?</p>
        <div class="flex gap-3 justify-end">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="confirmDeleteRule()"
            class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-pink-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Error message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
      <p class="text-red-700">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const rules = ref([])
const clients = ref([])
const services = ref([])
const loading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedRule = ref(null)

const form = ref({
  type: '',
  client_id: null,
  trigger_count: 8,
  service_filter: null,
  reward_type: 'discount',
  reward_value: 15.0,
  rebooking_days: 7
})

async function loadRules() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.loyalty.listRules()
    rules.value = response.data || []
  } catch (err) {
    error.value = 'Error al cargar las reglas de fidelización'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadClients() {
  try {
    const response = await api.clients.list({ limit: 100 })
    clients.value = response.data || []
  } catch (err) {
    console.error('Error al cargar clientas:', err)
  }
}

async function loadServices() {
  try {
    const response = await api.services.list()
    services.value = response.data || []
  } catch (err) {
    console.error('Error al cargar servicios:', err)
  }
}

function getClientName(clientId) {
  const client = clients.value.find(c => c.id === clientId)
  return client ? client.name : 'Cliente desconocido'
}

function getServiceName(serviceId) {
  const service = services.value.find(s => s.id === serviceId)
  return service ? service.name : null
}

function getClientProgress(clientId) {
  if (!clientId) return null
  const client = clients.value.find(c => c.id === clientId)
  return client ? client.appointments_count || 0 : 0
}

function getRebookingStatus(clientId) {
  if (!clientId) return null
  const client = clients.value.find(c => c.id === clientId)
  if (!client || !client.last_appointment_date) return 'Sin citas previas'
  
  const lastDate = new Date(client.last_appointment_date)
  const today = new Date()
  const daysSince = Math.floor((today - lastDate) / (1000 * 60 * 60 * 24))
  
  if (daysSince <= 7) return 'Eligible'
  return 'No elegible'
}

function getTypeLabel(type) {
  const labels = {
    'punch-card': 'Punch Card',
    'rebooking': 'Rebooking',
    'points': 'Points',
    'tiered': 'Tiered'
  }
  return labels[type] || type
}

function getRewardLabel(rule) {
  if (!rule.reward_type) return '-'
  
  switch (rule.reward_type) {
    case 'discount':
      return `${rule.reward_value}% descuento`
    case 'free-service':
      return 'Servicio gratis'
    case 'upgrade':
      return `$${rule.reward_value} upgrade`
    default:
      return '-'
  }
}

async function createRule() {
  if (!form.value.type || !form.value.trigger_count || !form.value.reward_type) {
    error.value = 'Por favor completa todos los campos requeridos'
    return
  }
  
  try {
    const response = await api.loyalty.createRule(form.value)
    rules.value.push(response.data)
    closeModals()
    resetForm()
  } catch (err) {
    error.value = 'Error al crear la regla de fidelización'
    console.error(err)
  }
}

async function updateRule() {
  if (!selectedRule.value || !form.value.type || !form.value.trigger_count) {
    return
  }
  
  try {
    const response = await api.loyalty.updateRule(selectedRule.value.id, form.value)
    const index = rules.value.findIndex(r => r.id === selectedRule.value.id)
    if (index !== -1) {
      rules.value[index] = response.data
    }
    closeModals()
    resetForm()
  } catch (err) {
    error.value = 'Error al actualizar la regla de fidelización'
    console.error(err)
  }
}

async function deleteRule(rule) {
  selectedRule.value = rule
  showDeleteModal.value = true
}

async function confirmDeleteRule() {
  if (!selectedRule.value) return
  
  try {
    await api.loyalty.deleteRule(selectedRule.value.id)
    rules.value = rules.value.filter(r => r.id !== selectedRule.value.id)
    showDeleteModal.value = false
    resetForm()
  } catch (err) {
    error.value = 'Error al eliminar la regla de fidelización'
    console.error(err)
  }
}

function editRule(rule) {
  selectedRule.value = rule
  form.value = { ...rule }
  showEditModal.value = true
}

function closeModals() {
  showCreateModal.value = false
  showEditModal.value = false
}

function resetForm() {
  form.value = {
    type: '',
    client_id: null,
    trigger_count: 8,
    service_filter: null,
    reward_type: 'discount',
    reward_value: 15.0,
    rebooking_days: 7
  }
}

onMounted(() => {
  loadRules()
  loadClients()
  loadServices()
})
</script>