<template>
  <div class="p-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Clientas</h1>
        <p class="text-sm text-gray-500 mt-1">{{ clients.length }} clientas registradas</p>
      </div>

      <!-- New Client / Appointment Buttons -->
      <div class="flex items-center gap-2">
        <button @click="showNewAppointment = true" class="btn-secondary text-xs px-3 py-1.5">
          + Nueva cita
        </button>
        <button @click="showNewClient = true" class="btn-primary text-xs px-3 py-1.5">
          + Nueva clienta
        </button>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="card p-4 mb-6">
      <div class="flex items-center gap-3">
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="Buscar clientas..."
          class="flex-1 outline-none text-sm text-gray-900 placeholder-gray-400"
        />
      </div>
    </div>

    <!-- Clients Grid -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <div v-else-if="filteredClients.length === 0" class="flex flex-col items-center justify-center py-12">
      <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <p class="text-sm text-gray-500">No hay clientas registradas</p>
    </div>

    <div v-else class="grid grid-cols-3 gap-6">
      <!-- Client Card -->
      <div 
        v-for="client in filteredClients" 
        :key="client.id"
        class="card p-6 hover:shadow-md transition-shadow duration-200 cursor-pointer"
        @click="showClientDetail(client)"
      >
        <!-- Avatar -->
        <div class="w-12 h-12 rounded-full bg-primary-200 flex items-center justify-center text-primary-700 font-semibold text-lg mb-4">
          {{ getInitials(client.name) }}
        </div>

        <!-- Name -->
        <h3 class="text-base font-semibold text-gray-900">{{ client.name }}</h3>

        <!-- Phone -->
        <p v-if="client.phone" class="text-sm text-gray-500 mt-1">📱 {{ client.phone }}</p>

        <!-- Stats -->
        <div class="flex items-center gap-4 mt-4 pt-4 border-t border-gray-100">
          <!-- Appointments count -->
          <div class="text-center">
            <p class="text-lg font-bold text-gray-900">{{ client.appointments_count }}</p>
            <p class="text-xs text-gray-500">Citas</p>
          </div>

          <!-- Divider -->
          <div class="w-px h-8 bg-gray-200"></div>

          <!-- Last appointment -->
          <div class="text-center">
            <p v-if="client.last_appointment_date" class="text-sm font-medium text-gray-900">{{ formatDate(client.last_appointment_date) }}</p>
            <p v-else class="text-xs text-gray-400">Sin citas</p>
          </div>
        </div>

        <!-- Loyalty Progress Bar -->
        <LoyaltyProgressBar 
          :client="client" 
          :rules="loyaltyRules" 
          class="mt-3"
        />

        <!-- Actions -->
        <div class="flex items-center gap-2 mt-4 pt-4 border-t border-gray-100">
          <button 
            @click.stop="showNewAppointment = true; selectedClient = client"
            class="btn-primary text-xs px-3 py-1.5 flex-1"
          >
            + Nueva cita
          </button>
          <button 
            @click.stop="editClient(client)"
            class="btn-secondary text-xs px-2 py-1.5"
          >
            Editar
          </button>
          <button 
            @click.stop="deleteClientConfirm(client)"
            class="text-xs text-red-600 hover:text-red-700 font-medium px-2 py-1 rounded-md hover:bg-red-50 transition-colors duration-150"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- New/Edit Client Modal -->
    <div 
      v-if="showNewClient || showEditClient"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-gray-900">{{ showEditClient ? 'Editar Clienta' : 'Nueva Clienta' }}</h2>
          <button @click="closeModal" class="p-1.5 rounded-md hover:bg-gray-100 transition-colors duration-150">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="saveClient" class="space-y-4">
          <!-- Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Nombre *</label>
            <input 
              v-model="clientForm.name"
              type="text"
              required
              placeholder="Nombre de la clienta..."
              class="input-field"
            />
          </div>

          <!-- Phone -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Teléfono</label>
            <input 
              v-model="clientForm.phone"
              type="tel"
              placeholder="Número de teléfono..."
              class="input-field"
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
            <input 
              v-model="clientForm.email"
              type="email"
              placeholder="correo@ejemplo.com..."
              class="input-field"
            />
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Notas</label>
            <textarea 
              v-model="clientForm.notes"
              rows="3"
              placeholder="Notas adicionales..."
              class="input-field resize-none"
            ></textarea>
          </div>

          <!-- Submit Button -->
          <button type="submit" :disabled="savingClient" class="btn-primary w-full py-2.5">
            <span v-if="!savingClient">{{ showEditClient ? 'Guardar cambios' : 'Crear clienta' }}</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Guardando...
            </span>
          </button>
        </form>
      </div>
    </div>

    <!-- Client Detail Modal -->
    <div 
      v-if="showClientDetailModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showClientDetailModal = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Detalle de Clienta</h2>
          <button @click="showClientDetailModal = false" class="p-1.5 rounded-md hover:bg-gray-100 transition-colors duration-150">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Client Info -->
        <div v-if="selectedClient" class="space-y-4">
          <!-- Avatar and Name -->
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-full bg-primary-200 flex items-center justify-center text-primary-700 font-semibold text-xl">
              {{ getInitials(selectedClient.name) }}
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ selectedClient.name }}</h3>
              <p v-if="selectedClient.phone" class="text-sm text-gray-500">📱 {{ selectedClient.phone }}</p>
              <p v-if="selectedClient.email" class="text-sm text-gray-500">✉️ {{ selectedClient.email }}</p>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-3 gap-4 p-4 rounded-lg bg-gray-50 border border-gray-100">
            <div class="text-center">
              <p class="text-xl font-bold text-gray-900">{{ selectedClient.appointments_count }}</p>
              <p class="text-xs text-gray-500">Citas totales</p>
            </div>
            <div class="text-center">
              <p v-if="selectedClient.last_appointment_date" class="text-sm font-medium text-gray-900">{{ formatDate(selectedClient.last_appointment_date) }}</p>
              <p v-else class="text-xs text-gray-400">Sin citas</p>
              <p class="text-xs text-gray-500">Última cita</p>
            </div>
            <div class="text-center">
              <p class="text-xl font-bold text-gray-900">{{ selectedClient.created_at ? formatDate(selectedClient.created_at.split('T')[0]) : '-' }}</p>
              <p class="text-xs text-gray-500">Desde</p>
            </div>
          </div>

          <!-- Loyalty Progress Bar -->
          <LoyaltyProgressBar 
            :client="selectedClient" 
            :rules="loyaltyRules" 
          />

          <!-- Notes -->
          <div 
            v-if="selectedClient.notes"
            class="flex items-start gap-3 p-4 rounded-lg bg-gray-50 border border-gray-100"
          >
            <svg class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            <p class="text-sm text-gray-700">{{ selectedClient.notes }}</p>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-3 pt-2">
            <button 
              @click="showNewAppointment = true; showClientDetailModal = false"
              class="btn-primary flex-1 py-2.5"
            >
              + Nueva cita
            </button>
            <button 
              @click="editClient(selectedClient)"
              class="btn-secondary flex-1 py-2.5"
            >
              Editar clienta
            </button>
            <button 
              @click="deleteClientConfirm(selectedClient)"
              class="text-sm text-red-600 hover:text-red-700 font-medium px-4 py-2 rounded-md hover:bg-red-50 transition-colors duration-150"
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div 
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showDeleteConfirm = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Confirmar eliminación</h2>
          <button @click="showDeleteConfirm = false" class="p-1.5 rounded-md hover:bg-gray-100 transition-colors duration-150">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Warning -->
        <p class="text-sm text-gray-700 mb-4">
          ¿Estás segura de que quieres eliminar a <strong>{{ selectedClient?.name }}</strong>? Esta acción no se puede deshacer.
        </p>

        <!-- Actions -->
        <div class="flex items-center gap-3">
          <button 
            @click="showDeleteConfirm = false"
            class="btn-secondary flex-1 py-2.5"
          >
            Cancelar
          </button>
          <button 
            @click="deleteClient(selectedClient?.id)"
            :disabled="deletingClient"
            class="btn-danger flex-1 py-2.5"
          >
            <span v-if="!deletingClient">Eliminar</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Eliminando...
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- New Appointment Modal using AppointmentForm component -->
    <AppointmentForm
      v-if="showNewAppointment"
      :clients="clients"
      :services="services"
      :preselectedClientId="selectedClient?.id || null"
      @close="showNewAppointment = false"
      @created="handleAppointmentCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '../api'
import AppointmentForm from '../components/AppointmentForm.vue'
import LoyaltyProgressBar from '../components/LoyaltyProgressBar.vue'

// Clients data
const clients = ref<any[]>([])
const services = ref<any[]>([])
const loyaltyRules = ref<any[]>([])
const loading = ref(true)
const savingClient = ref(false)
const deletingClient = ref(false)

// Search query
const searchQuery = ref('')

// Modal states
const showNewClient = ref(false)
const showEditClient = ref(false)
const showClientDetailModal = ref(false)
const showDeleteConfirm = ref(false)
const showNewAppointment = ref(false)
const selectedClient = ref<any>(null)

// Client form data
const clientForm = ref({
  name: '',
  phone: '',
  email: '',
  notes: '',
})

// Filtered clients (by search)
const filteredClients = computed(() => {
  if (!searchQuery.value) return clients.value
  
  const query = searchQuery.value.toLowerCase()
  return clients.value.filter((client: any) => 
    client.name.toLowerCase().includes(query) ||
    (client.phone && client.phone.includes(query)) ||
    (client.email && client.email.toLowerCase().includes(query))
  )
})

// Get initials from name
function getInitials(name: string): string {
  const parts = name.split(' ')
  if (parts.length === 1) return parts[0]?.charAt(0)?.toUpperCase() || '?'
  return ((parts[0]?.charAt(0) || '') + (parts[parts.length - 1]?.charAt(0) || '')).toUpperCase()
}

// Format date for display
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })
}

// Close all modals
function closeModal() {
  showNewClient.value = false
  showEditClient.value = false
  resetForm()
}

// Reset form data
function resetForm() {
  clientForm.value = {
    name: '',
    phone: '',
    email: '',
    notes: '',
  }
}

// Show client detail
function showClientDetail(client: any) {
  selectedClient.value = client
  showClientDetailModal.value = true
}

// Edit client
function editClient(client: any) {
  selectedClient.value = client
  showEditClient.value = true
  
  // Populate form with client data
  clientForm.value = {
    name: client.name,
    phone: client.phone || '',
    email: client.email || '',
    notes: client.notes || '',
  }
  
  showClientDetailModal.value = false
}

// Confirm delete client
function deleteClientConfirm(client: any) {
  selectedClient.value = client
  showDeleteConfirm.value = true
}

// Delete client
async function deleteClient(id?: string) {
  if (!id) return
  
  deletingClient.value = true
  try {
    await api.clients.delete(id)
    showDeleteConfirm.value = false
    selectedClient.value = null
    
    // Reload data
    await loadClients()
  } catch (error) {
    console.error('Error deleting client:', error)
  } finally {
    deletingClient.value = false
  }
}

// Save client (create or update)
async function saveClient() {
  savingClient.value = true
  try {
    if (showEditClient.value && selectedClient.value?.id) {
      // Update existing client
      await api.clients.update(selectedClient.value.id, {
        name: clientForm.value.name,
        phone: clientForm.value.phone || null,
        email: clientForm.value.email || null,
        notes: clientForm.value.notes || null,
      })
    } else {
      // Create new client
      await api.clients.create({
        name: clientForm.value.name,
        phone: clientForm.value.phone || null,
        email: clientForm.value.email || null,
        notes: clientForm.value.notes || null,
      })
    }

    // Close modal and reload data
    closeModal()
    await loadClients()
  } catch (error) {
    console.error('Error saving client:', error)
  } finally {
    savingClient.value = false
  }
}

// Load clients, services and loyalty rules
async function loadClients() {
  loading.value = true
  try {
    const [clientsResponse, servicesResponse] = await Promise.all([
      api.clients.list(),
      api.services.list(),
    ])

    clients.value = clientsResponse.data?.items || []
    services.value = servicesResponse.data?.items || []
    
    // Load loyalty rules for progress bar display
    try {
      const rulesResponse = await api.loyalty.listRules()
      loyaltyRules.value = rulesResponse.data?.rules || []
      
      // Enrich rules with service names for display
      if (services.value.length > 0) {
        loyaltyRules.value = loyaltyRules.value.map((rule: any) => ({
          ...rule,
          service_filter_name: rule.service_filter 
            ? services.value.find((s: any) => s.id === rule.service_filter)?.name || ''
            : '',
        }))
      }
    } catch (err) {
      console.error('Error loading loyalty rules:', err)
    }
  } catch (error) {
    console.error('Error loading clients:', error)
  } finally {
    loading.value = false
  }
}

// Handle appointment created from AppointmentForm component
async function handleAppointmentCreated() {
  showNewAppointment.value = false
  await loadClients()
}

onMounted(() => {
  loadClients()
})
</script>