<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Servicios</h1>
      <button
        @click="showCreateModal = true"
        class="bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Nuevo Servicio
      </button>
    </div>

    <!-- Services Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="service in services"
        :key="service.id"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
        @click="selectService(service)"
      >
        <!-- Color indicator -->
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-4 h-4 rounded-full border border-gray-300"
            :style="{ backgroundColor: service.color || '#E5E7EB' }"
          ></div>
          <span class="text-sm text-gray-500 capitalize">{{ service.category }}</span>
        </div>

        <!-- Service name -->
        <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ service.name }}</h3>

        <!-- Duration and price -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
            <span>{{ service.duration }} min</span>
          </div>
          <span class="text-lg font-bold text-pink-500">${{ service.price.toFixed(2) }}</span>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 mt-4 pt-3 border-t border-gray-100">
          <button
            @click.stop="editService(service)"
            class="text-blue-500 hover:text-blue-600 text-sm flex items-center gap-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
            Editar
          </button>
          <button
            @click.stop="deleteService(service)"
            class="text-red-500 hover:text-red-600 text-sm flex items-center gap-1 ml-auto"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            Eliminar
          </button>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-if="services.length === 0"
        class="col-span-full text-center py-12 bg-white rounded-xl border border-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
          <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
        </svg>
        <p class="text-gray-500 text-lg">No hay servicios configurados</p>
        <button
          @click="showCreateModal = true"
          class="mt-4 bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Crear primer servicio
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || showEditModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeModals()"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-gray-800 mb-4">
          {{ showEditModal ? 'Editar Servicio' : 'Nuevo Servicio' }}
        </h2>

        <!-- Category -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
          <select
            v-model="form.category"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          >
            <option value="">Seleccionar categoría</option>
            <option value="manicure">Manicure</option>
            <option value="pedicure">Pedicure</option>
            <option value="nail-art">Nail Art</option>
            <option value="acrylic">Acrílico</option>
            <option value="gel">Gel</option>
            <option value="other">Otro</option>
          </select>
        </div>

        <!-- Name -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Servicio</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Ej: Manicure Clásico"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>

        <!-- Duration -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Duración (minutos)</label>
          <input
            v-model.number="form.duration"
            type="number"
            placeholder="30"
            min="5"
            step="5"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>

        <!-- Price -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Precio ($)</label>
          <input
            v-model.number="form.price"
            type="number"
            placeholder="25.00"
            min="0"
            step="0.50"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          />
        </div>

        <!-- Color -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
          <div class="flex items-center gap-3">
            <input
              v-model="form.color"
              type="color"
              class="w-12 h-12 rounded-lg border border-gray-300 cursor-pointer"
            />
            <span class="text-sm text-gray-500">{{ form.color }}</span>
          </div>
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
            @click="showEditModal ? updateService() : createService()"
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
        <h2 class="text-lg font-bold text-gray-800 mb-2">Eliminar Servicio</h2>
        <p class="text-gray-600 mb-4">¿Estás segura de eliminar "{{ selectedService?.name }}"?</p>
        <div class="flex gap-3 justify-end">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="confirmDeleteService()"
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

const services = ref([])
const loading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedService = ref(null)

const form = ref({
  name: '',
  category: '',
  duration: 30,
  price: 25.00,
  color: '#E5E7EB'
})

async function loadServices() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/api/services/')
    services.value = response.data
  } catch (err) {
    error.value = 'Error al cargar los servicios'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function createService() {
  if (!form.value.name || !form.value.duration || form.value.price === undefined) {
    error.value = 'Por favor completa todos los campos requeridos'
    return
  }
  
  try {
    const response = await api.post('/api/services/', form.value)
    services.value.push(response.data)
    closeModals()
    resetForm()
  } catch (err) {
    error.value = 'Error al crear el servicio'
    console.error(err)
  }
}

async function updateService() {
  if (!selectedService.value || !form.value.name || !form.value.duration) {
    return
  }
  
  try {
    const response = await api.put(`/api/services/${selectedService.value.id}`, form.value)
    const index = services.value.findIndex(s => s.id === selectedService.value.id)
    if (index !== -1) {
      services.value[index] = response.data
    }
    closeModals()
    resetForm()
  } catch (err) {
    error.value = 'Error al actualizar el servicio'
    console.error(err)
  }
}

async function deleteService(service) {
  selectedService.value = service
  showDeleteModal.value = true
}

async function confirmDeleteService() {
  if (!selectedService.value) return
  
  try {
    await api.delete(`/api/services/${selectedService.value.id}`)
    services.value = services.value.filter(s => s.id !== selectedService.value.id)
    showDeleteModal.value = false
    resetForm()
  } catch (err) {
    error.value = 'Error al eliminar el servicio'
    console.error(err)
  }
}

function editService(service) {
  selectedService.value = service
  form.value = { ...service }
  showEditModal.value = true
}

function selectService(service) {
  // Future: navigate to client detail or appointment creation with this service pre-selected
  console.log('Selected service:', service)
}

function closeModals() {
  showCreateModal.value = false
  showEditModal.value = false
}

function resetForm() {
  form.value = {
    name: '',
    category: '',
    duration: 30,
    price: 25.00,
    color: '#E5E7EB'
  }
}

onMounted(() => {
  loadServices()
})
</script>