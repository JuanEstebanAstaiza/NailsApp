<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg">
      <!-- Header -->
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-800">
          {{ isEditing ? 'Editar Cita' : 'Nueva Cita' }}
        </h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit">
        <!-- Client -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Clienta *</label>
          <select
            v-model="form.client_id"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            required
          >
            <option value="">Seleccionar clienta</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.name }} ({{ client.appointments_count || 0 }} citas)
            </option>
          </select>
        </div>

        <!-- Service -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Servicio *</label>
          <select
            v-model="form.service_id"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            required
          >
            <option value="">Seleccionar servicio</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }} - ${{ service.price.toFixed(2) }} ({{ service.duration }} min)
            </option>
          </select>
        </div>

        <!-- Date -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
          <input
            v-model="form.date"
            type="date"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            required
          />
        </div>

        <!-- Time -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Hora *</label>
          <input
            v-model="form.time"
            type="time"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            required
          />
        </div>

        <!-- Duration (auto-filled from service) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Duración</label>
          <input
            :value="selectedServiceDuration ? `${selectedServiceDuration} min` : ''"
            disabled
            class="w-full border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 text-gray-500"
          />
        </div>

        <!-- Status -->
        <div v-if="isEditing" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select
            v-model="form.status"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          >
            <option value="scheduled">Programada</option>
            <option value="completed">Completada</option>
            <option value="cancelled">Cancelada</option>
          </select>
        </div>

        <!-- Notes -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Notas (opcional)</label>
          <textarea
            v-model="form.notes"
            rows="3"
            placeholder="Ej: Clienta prefiere esmalte nude, alergia a acetona..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
          ></textarea>
        </div>

        <!-- Loyalty discount preview -->
        <div v-if="loyaltyDiscount > 0 && !isEditing" class="mb-4 bg-green-50 border border-green-200 rounded-lg p-3">
          <p class="text-sm text-green-700 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267C11.93 11.66 12 11.886 12 12s-.07.34-.433.582zM11 15.849v-1.698c.22.071.412.164.567.267C11.93 14.66 12 14.886 12 15s-.07.34-.433.582zM8 12a2 2 0 114 0H8z" />
            </svg>
            ¡Descuento de fidelización aplicado! {{ loyaltyDiscount }}%
          </p>
          <p class="text-xs text-green-600 mt-1">
            Precio original: ${{ selectedServicePrice?.toFixed(2) || '0.00' }} → 
            Con descuento: ${{ (selectedServicePrice ? selectedServicePrice * (1 - loyaltyDiscount / 100) : 0).toFixed(2) }}
          </p>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 justify-end">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-pink-500 hover:bg-pink-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isEditing ? 'Actualizar' : 'Crear Cita' }}
          </button>
        </div>
      </form>

      <!-- Error message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3 mt-4">
        <p class="text-sm text-red-700">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api'

const props = defineProps({
  appointment: { type: Object, default: null },
  clients: { type: Array, required: true },
  services: { type: Array, required: true },
  rules: { type: Array, default: () => [] },
  preselectedClientId: { type: String, default: null }
})

const emit = defineEmits(['close', 'created', 'updated'])

const isEditing = computed(() => !!props.appointment)

const form = ref({
  client_id: props.preselectedClientId || '',
  service_id: '',
  date: new Date().toISOString().split('T')[0],
  time: '10:00',
  status: 'scheduled',
  notes: ''
})

// Watch for preselectedClientId changes
watch(() => props.preselectedClientId, (newClientId) => {
  if (!isEditing.value && newClientId) {
    form.value.client_id = newClientId
  }
})

const loading = ref(false)
const error = ref('')

// Computed values for auto-fill and loyalty preview
const selectedServiceDuration = computed(() => {
  if (!form.value.service_id) return null
  const service = props.services.find(s => s.id === form.value.service_id)
  return service ? service.duration : null
})

const selectedServicePrice = computed(() => {
  if (!form.value.service_id) return null
  const service = props.services.find(s => s.id === form.value.service_id)
  return service ? service.price : null
})

// Loyalty discount calculation - uses props.rules first, falls back to local rules ref
const loyaltyDiscount = computed(() => {
  if (isEditing.value || !form.value.client_id || !form.value.service_id) return 0
  
  const client = props.clients.find(c => c.id === form.value.client_id)
  if (!client || !client.appointments_count) return 0
  
  // Use props.rules if available, otherwise use local rules ref
  const currentRules = (props.rules && props.rules.length > 0) ? props.rules : rules.value
  
  // Check for punch-card rules
  const punchCardRules = currentRules.filter(r => 
    r.type === 'punch-card' && 
    (r.client_id === null || r.client_id === client.id) &&
    (r.service_filter === null || r.service_filter === form.value.service_id) &&
    client.appointments_count >= r.trigger_count
  )
  
  if (punchCardRules.length > 0) {
    return punchCardRules[0].reward_value // Return the discount percentage
  }
  
  // Check for rebooking rules
  const rebookingRules = currentRules.filter(r => 
    r.type === 'rebooking' && 
    (r.client_id === null || r.client_id === client.id) &&
    client.last_appointment_date &&
    Math.floor((new Date() - new Date(client.last_appointment_date)) / (1000 * 60 * 60 * 24)) <= (r.rebooking_days || 7)
  )
  
  if (rebookingRules.length > 0) {
    return rebookingRules[0].reward_value // Return the discount percentage
  }
  
  return 0
})

// Load loyalty rules for preview (fallback when props.rules not provided)
const rules = ref([])
async function loadLoyaltyRules() {
  try {
    const response = await api.loyalty.listRules()
    rules.value = response.data || []
  } catch (err) {
    console.error('Error al cargar reglas de fidelización:', err)
  }
}

// Watch for service changes to auto-fill duration
watch(() => form.value.service_id, (newServiceId) => {
  const service = props.services.find(s => s.id === newServiceId)
  if (service && !isEditing.value) {
    // Auto-set time based on previous appointment end time or default
    form.value.duration = service.duration
  }
})

// Initialize form for editing
watch(() => props.appointment, (newAppointment) => {
  if (newAppointment) {
    form.value = {
      client_id: newAppointment.client_id || '',
      service_id: newAppointment.service_id || '',
      date: newAppointment.date || new Date().toISOString().split('T')[0],
      time: newAppointment.time || '10:00',
      status: newAppointment.status || 'scheduled',
      notes: newAppointment.notes || ''
    }
  }
}, { immediate: true })

async function handleSubmit() {
  if (!form.value.client_id || !form.value.service_id || !form.value.date || !form.value.time) {
    error.value = 'Por favor completa todos los campos requeridos'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const data = { ...form.value }
    
    if (isEditing.value) {
      await api.appointments.update(props.appointment.id, data)
      emit('updated')
    } else {
      await api.appointments.create(data)
      emit('created')
    }
    
    emit('close')
  } catch (err) {
    error.value = isEditing.value ? 'Error al actualizar la cita' : 'Error al crear la cita'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Only load rules from API if props.rules is not provided
  if (!props.rules || props.rules.length === 0) {
    loadLoyaltyRules()
  }
})

// Watch for rules prop changes
watch(() => props.rules, (newRules) => {
  if (newRules && newRules.length > 0) {
    rules.value = newRules
  }
}, { deep: true })
</script>