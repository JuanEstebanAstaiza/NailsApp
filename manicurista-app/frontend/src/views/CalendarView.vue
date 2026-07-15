<template>
  <div class="p-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Calendario</h1>
        <p class="text-sm text-gray-500 mt-1">{{ currentMonthFormatted }}</p>
      </div>

      <!-- Navigation Controls -->
      <div class="flex items-center gap-3">
        <button @click="prevMonth" class="btn-secondary p-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <button @click="goToToday" class="btn-secondary text-xs px-3 py-1.5">
          Hoy
        </button>

        <button @click="nextMonth" class="btn-secondary p-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- New Appointment Button -->
        <button @click="showNewAppointment = true" class="btn-primary text-xs px-3 py-1.5">
          + Nueva cita
        </button>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="card p-6">
      <!-- Day Headers -->
      <div class="grid grid-cols-7 gap-px mb-2">
        <div 
          v-for="day in ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']" 
          :key="day"
          class="text-center text-xs font-medium text-gray-500 py-2"
        >
          {{ day }}
        </div>
      </div>

      <!-- Calendar Days -->
      <div class="grid grid-cols-7 gap-px">
        <div 
          v-for="day in calendarDays" 
          :key="day.dateStr"
          :class="[
            'min-h-[100px] p-2 border border-gray-100 transition-colors duration-150',
            day.isCurrentMonth ? '' : 'bg-gray-50',
            day.isToday ? 'border-primary-300 bg-primary-50' : '',
          ]"
        >
          <!-- Day number -->
          <div class="flex items-center justify-between mb-1">
            <span 
              :class="[
                'text-sm font-medium',
                day.isToday ? 'bg-primary-600 text-white w-7 h-7 rounded-full flex items-center justify-center' : 
                day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
              ]"
            >
              {{ day.dayNumber }}
            </span>

            <!-- Appointment count badge -->
            <span 
              v-if="day.appointments.length > 0"
              class="badge-info text-xs px-1.5 py-0.5"
            >
              {{ day.appointments.length }}
            </span>
          </div>

          <!-- Appointments for this day -->
          <div class="space-y-1">
            <div 
              v-for="appointment in day.appointments.slice(0, 3)" 
              :key="appointment.id"
              @click="showAppointmentDetail(appointment)"
              class="p-1.5 rounded text-xs cursor-pointer transition-colors duration-150 hover:opacity-80"
              :class="[
                appointment.status === 'pending' ? 'bg-yellow-100 text-yellow-800 border-l-2 border-yellow-400' : 
                appointment.status === 'completed' ? 'bg-green-100 text-green-800 border-l-2 border-green-400' : 
                appointment.status === 'cancelled' ? 'bg-red-100 text-red-800 border-l-2 border-red-400' : 
                'bg-gray-100 text-gray-800 border-l-2 border-gray-400'
              ]"
            >
              <p class="font-medium">{{ appointment.time }}</p>
              <p class="truncate">{{ appointment.client_name }}</p>
            </div>

            <!-- More appointments indicator -->
            <div 
              v-if="day.appointments.length > 3"
              class="text-xs text-gray-500 pl-1.5"
            >
              +{{ day.appointments.length - 3 }} más
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Appointment Modal using AppointmentForm component -->
    <AppointmentForm
      v-if="showNewAppointment"
      :clients="clients"
      :services="services"
      :rules="loyaltyRules"
      @close="showNewAppointment = false"
      @created="handleAppointmentCreated"
    />

    <!-- Appointment Detail Modal -->
    <div 
      v-if="showAppointmentDetailModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showAppointmentDetailModal = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Detalle de Cita</h2>
          <button @click="showAppointmentDetailModal = false" class="p-1.5 rounded-md hover:bg-gray-100 transition-colors duration-150">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Appointment Info -->
        <div v-if="selectedAppointment" class="space-y-4">
          <!-- Status Badge -->
          <span :class="[
            'badge',
            selectedAppointment.status === 'pending' ? 'badge-warning' : 
            selectedAppointment.status === 'completed' ? 'badge-success' : 
            selectedAppointment.status === 'cancelled' ? 'badge-danger' : 'badge-info'
          ]">
            {{ formatStatus(selectedAppointment.status) }}
          </span>

          <!-- Client -->
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ selectedAppointment.client_name }}</p>
              <p class="text-xs text-gray-500">ID: {{ selectedAppointment.client_id }}</p>
            </div>
          </div>

          <!-- Service -->
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ selectedAppointment.service_name }}</p>
              <p class="text-xs text-gray-500">${{ selectedAppointment.service_price }} · {{ selectedAppointment.service_duration }} min</p>
            </div>
          </div>

          <!-- Date & Time -->
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ selectedAppointment.date }}</p>
              <p class="text-xs text-gray-500">{{ selectedAppointment.time }}</p>
            </div>
          </div>

          <!-- Loyalty Discount -->
          <div 
            v-if="selectedAppointment.has_loyalty_discount"
            class="flex items-center gap-3 p-3 rounded-lg bg-green-50 border border-green-200"
          >
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            <div>
              <p class="text-sm font-medium text-green-800">Descuento de fidelización</p>
              <p class="text-xs text-green-700">{{ selectedAppointment.discount_percentage }}% - ${{ selectedAppointment.original_price }} → ${{ selectedAppointment.final_price }}</p>
            </div>
          </div>

          <!-- Notes -->
          <div 
            v-if="selectedAppointment.notes"
            class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 border border-gray-100"
          >
            <svg class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            <p class="text-sm text-gray-700">{{ selectedAppointment.notes }}</p>
          </div>

          <!-- Actions -->
          <div v-if="selectedAppointment.status === 'pending'" class="flex items-center gap-3 pt-2">
            <button 
              @click="completeAppointment(selectedAppointment.id)"
              class="btn-success flex-1 py-2.5"
            >
              Completar cita
            </button>
            <button 
              @click="cancelAppointment(selectedAppointment.id)"
              class="btn-danger flex-1 py-2.5"
            >
              Cancelar cita
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '../api'
import AppointmentForm from '../components/AppointmentForm.vue'

// Calendar state
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const appointments = ref<any[]>([])
const clients = ref<any[]>([])
const services = ref<any[]>([])
const loyaltyRules = ref<any[]>([])

// Modal states
const showNewAppointment = ref(false)
const showAppointmentDetailModal = ref(false)
const selectedAppointment = ref<any>(null)

// Today's date string
const todayStr = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Current month formatted
const currentMonthFormatted = computed(() => {
  const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
  return `${months[currentMonth.value]} ${currentYear.value}`
})

// Calendar days (for display)
const calendarDays = computed(() => {
  const firstDayOfMonth = new Date(currentYear.value, currentMonth.value, 1)
  const lastDayOfMonth = new Date(currentYear.value, currentMonth.value + 1, 0)
  
  const startDayOfWeek = firstDayOfMonth.getDay() // 0=Sunday
  
  const days: any[] = []
  
  // Previous month padding
  for (let i = 0; i < startDayOfWeek; i++) {
    const date = new Date(currentYear.value, currentMonth.value, -startDayOfWeek + i + 1)
    days.push({
      dayNumber: date.getDate(),
      dateStr: date.toISOString().split('T')[0],
      isCurrentMonth: false,
      isToday: false,
      appointments: [],
    })
  }
  
  // Current month days
  for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    const dateStr = date.toISOString().split('T')[0]
    
    const dayAppointments = appointments.value.filter((a: any) => a.date === dateStr)
    
    days.push({
      dayNumber: i,
      dateStr,
      isCurrentMonth: true,
      isToday: dateStr === todayStr.value,
      appointments: dayAppointments.sort((a: any, b: any) => a.time.localeCompare(b.time)),
    })
  }
  
  // Next month padding (to fill grid to 42 cells = 6 rows × 7 days)
  const remainingCells = 42 - days.length
  for (let i = 1; i <= remainingCells; i++) {
    const date = new Date(currentYear.value, currentMonth.value + 1, i)
    days.push({
      dayNumber: date.getDate(),
      dateStr: date.toISOString().split('T')[0],
      isCurrentMonth: false,
      isToday: false,
      appointments: [],
    })
  }
  
  return days
})

// Format status for display
function formatStatus(status: string): string {
  const statusMap: Record<string, string> = {
    pending: 'Pendiente',
    completed: 'Completada',
    cancelled: 'Cancelada',
  }
  return statusMap[status] || status
}

// Navigate to previous month
function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

// Navigate to next month
function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

// Go to today's month
function goToToday() {
  const now = new Date()
  currentMonth.value = now.getMonth()
  currentYear.value = now.getFullYear()
}

// Show appointment detail
function showAppointmentDetail(appointment: any) {
  selectedAppointment.value = appointment
  showAppointmentDetailModal.value = true
}

// Load calendar data
async function loadCalendarData() {
  try {
    // Get all appointments for the current month and surrounding months
    const firstDayOfMonth = new Date(currentYear.value, currentMonth.value, 1).toISOString().split('T')[0]
    const lastDayOfMonth = new Date(currentYear.value, currentMonth.value + 1, 0).toISOString().split('T')[0]
    
    const apptResponse = await api.appointments.list({
      date_from: firstDayOfMonth,
      date_to: lastDayOfMonth,
    })
    appointments.value = apptResponse.data || []

    // Get clients and services for the new appointment form
    const [clientsResponse, servicesResponse] = await Promise.all([
      api.clients.list(),
      api.services.list(),
    ])
    clients.value = clientsResponse.data || []
    services.value = servicesResponse.data || []
    
    // Load loyalty rules for discount preview in AppointmentForm
    try {
      const rulesResponse = await api.loyalty.listRules()
      loyaltyRules.value = rulesResponse.data?.rules || []
    } catch (err) {
      console.error('Error loading loyalty rules:', err)
    }
  } catch (error) {
    console.error('Error loading calendar data:', error)
  }
}

// Handle appointment created from AppointmentForm component
async function handleAppointmentCreated() {
  showNewAppointment.value = false
  await loadCalendarData()
}

// Complete appointment
async function completeAppointment(id: string) {
  try {
    await api.appointments.complete(id)
    showAppointmentDetailModal.value = false
    selectedAppointment.value = null
    await loadCalendarData()
  } catch (error) {
    console.error('Error completing appointment:', error)
  }
}

// Cancel appointment
async function cancelAppointment(id: string) {
  try {
    await api.appointments.cancel(id)
    showAppointmentDetailModal.value = false
    selectedAppointment.value = null
    await loadCalendarData()
  } catch (error) {
    console.error('Error cancelling appointment:', error)
  }
}

onMounted(() => {
  loadCalendarData()
})
</script>