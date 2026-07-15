<template>
  <div class="p-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-sm text-gray-500 mt-1">{{ todayFormatted }}</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-4 gap-6 mb-8">
      <!-- Today's Appointments -->
      <div class="card card-hover p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{{ stats.todayAppointments }}</p>
        <p class="text-sm text-gray-500 mt-1">Citas hoy</p>
      </div>

      <!-- Pending Appointments -->
      <div class="card card-hover p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-yellow-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{{ stats.pendingAppointments }}</p>
        <p class="text-sm text-gray-500 mt-1">Pendientes</p>
      </div>

      <!-- Total Clients -->
      <div class="card card-hover p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{{ stats.totalClients }}</p>
        <p class="text-sm text-gray-500 mt-1">Clientas</p>
      </div>

      <!-- Completed This Month -->
      <div class="card card-hover p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{{ stats.completedThisMonth }}</p>
        <p class="text-sm text-gray-500 mt-1">Completadas este mes</p>
      </div>
    </div>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-3 gap-6">
      <!-- Upcoming Appointments (2 columns) -->
      <div class="col-span-2 card p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Próximas Citas</h2>
          <router-link to="/calendar" class="btn-secondary text-xs px-3 py-1.5">
            Ver calendario
          </router-link>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="flex items-center justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- Empty state -->
        <div v-else-if="upcomingAppointments.length === 0" class="flex flex-col items-center justify-center py-8">
          <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="text-sm text-gray-500">No hay citas próximas</p>
        </div>

        <!-- Appointments list -->
        <div v-else class="space-y-3">
          <div 
            v-for="appointment in upcomingAppointments" 
            :key="appointment.id"
            class="flex items-center gap-4 p-4 rounded-lg border border-gray-100 hover:border-primary-200 transition-colors duration-150"
          >
            <!-- Time -->
            <div class="w-16 text-center">
              <p class="text-sm font-semibold text-gray-900">{{ appointment.time }}</p>
            </div>

            <!-- Divider -->
            <div class="w-px h-10 bg-gray-200"></div>

            <!-- Client info -->
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ appointment.client_name }}</p>
              <p class="text-xs text-gray-500 mt-0.5">{{ appointment.service_name }}</p>
            </div>

            <!-- Loyalty badge -->
            <div v-if="appointment.has_loyalty_discount" class="badge-success">
              {{ appointment.discount_percentage }}% descuento
            </div>

            <!-- Status badge -->
            <span :class="[
              'badge',
              appointment.status === 'pending' ? 'badge-warning' : 
              appointment.status === 'completed' ? 'badge-success' : 
              appointment.status === 'cancelled' ? 'badge-danger' : 'badge-info'
            ]">
              {{ formatStatus(appointment.status) }}
            </span>

            <!-- Actions -->
            <div class="flex items-center gap-2">
              <button 
                v-if="appointment.status === 'pending'"
                @click="completeAppointment(appointment.id)"
                class="p-1.5 rounded-md hover:bg-green-50 transition-colors duration-150"
                title="Completar cita"
              >
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
              <button 
                v-if="appointment.status === 'pending'"
                @click="cancelAppointment(appointment.id)"
                class="p-1.5 rounded-md hover:bg-red-50 transition-colors duration-150"
                title="Cancelar cita"
              >
                <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loyalty Alerts (1 column) -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-gray-900">Alertas de Fidelización</h2>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="flex items-center justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- Empty state -->
        <div v-else-if="loyaltyAlerts.length === 0" class="flex flex-col items-center justify-center py-8">
          <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
          <p class="text-sm text-gray-500">No hay alertas de fidelización</p>
        </div>

        <!-- Loyalty alerts list -->
        <div v-else class="space-y-3">
          <div 
            v-for="alert in loyaltyAlerts" 
            :key="alert.client_id"
            class="flex items-center gap-3 p-4 rounded-lg border border-yellow-200 bg-yellow-50"
          >
            <!-- Star icon -->
            <svg class="w-5 h-5 text-yellow-600 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>

            <!-- Alert text -->
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ alert.client_name }}</p>
              <p class="text-xs text-yellow-800 mt-0.5">{{ alert.message }}</p>
            </div>

            <!-- Progress bar -->
            <div class="w-16">
              <div class="progress-bar-bg">
                <div 
                  :class="[
                    'progress-bar-fill',
                    alert.is_qualified ? 'bg-green-500' : 'bg-yellow-500'
                  ]"
                  :style="{ width: `${(alert.appointments_count / alert.trigger_count) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick link -->
        <router-link to="/loyalty" class="block mt-4 text-center text-xs text-primary-600 hover:text-primary-700 font-medium">
          Ver fidelización →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '../api'

// Stats data
const stats = ref({
  todayAppointments: 0,
  pendingAppointments: 0,
  totalClients: 0,
  completedThisMonth: 0,
})

// Upcoming appointments
const upcomingAppointments = ref<any[]>([])
const loyaltyAlerts = ref<any[]>([])
const loading = ref(true)

// Today's date formatted
const todayFormatted = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('es-CO', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
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

// Load dashboard data
async function loadDashboard() {
  loading.value = true
  try {
    // Get today's date range
    const today = new Date().toISOString().split('T')[0]
    
    // Fetch stats from API (or calculate locally)
    const [appointmentsResponse, clientsResponse] = await Promise.all([
      api.appointments.list({ 
        date_from: today, 
        date_to: today 
      }),
      api.clients.list({ limit: 1 })
    ])

    // Calculate stats from appointments data
    const allAppointments = await api.appointments.list()
    const todayAppts = allAppointments.data.filter((a: any) => a.date === today)
    const pendingAppts = allAppointments.data.filter((a: any) => a.status === 'pending')
    
    // Get completed this month
    const currentYear = new Date().getFullYear()
    const currentMonth = new Date().getMonth()
    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).toISOString().split('T')[0] || ''
    const completedThisMonth = allAppointments.data.filter(
      (a: any) => a.status === 'completed' && a.date >= firstDayOfMonth
    ).length

    stats.value = {
      todayAppointments: todayAppts.length,
      pendingAppointments: pendingAppts.length,
      totalClients: clientsResponse.data?.total || 0,
      completedThisMonth,
    }

    // Get upcoming appointments (next 7 days)
    const nextWeek = new Date()
    nextWeek.setDate(nextWeek.getDate() + 7)
    const nextWeekStr = nextWeek.toISOString().split('T')[0]
    
    const upcomingResponse = await api.appointments.list({
      date_from: today,
      date_to: nextWeekStr,
      status: 'pending',
    })
    upcomingAppointments.value = upcomingResponse.data || []

    // Get loyalty alerts (clients close to reward)
    const clientsResponseAll = await api.clients.list()
    const clientsList = clientsResponseAll.data?.items || []
    
    for (const client of clientsList) {
      if (client.appointments_count > 0 && client.appointments_count < 10) {
        loyaltyAlerts.value.push({
          client_id: client.id,
          client_name: client.name,
          appointments_count: client.appointments_count,
          trigger_count: 8, // Default punch card threshold
          is_qualified: client.appointments_count >= 8,
          message: client.appointments_count >= 8 
            ? '¡Califica para manicure gratis!' 
            : `Faltan ${8 - client.appointments_count} citas para manicure gratis`,
        })
      }
    }

    // Sort loyalty alerts by proximity to reward (closest first)
    loyaltyAlerts.value.sort((a, b) => a.trigger_count - a.appointments_count - (b.trigger_count - b.appointments_count))

  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loading.value = false
  }
}

// Complete appointment
async function completeAppointment(id: string) {
  try {
    await api.appointments.complete(id)
    // Reload data
    await loadDashboard()
  } catch (error) {
    console.error('Error completing appointment:', error)
  }
}

// Cancel appointment
async function cancelAppointment(id: string) {
  try {
    await api.appointments.cancel(id)
    // Reload data
    await loadDashboard()
  } catch (error) {
    console.error('Error cancelling appointment:', error)
  }
}

onMounted(() => {
  loadDashboard()
})
</script>