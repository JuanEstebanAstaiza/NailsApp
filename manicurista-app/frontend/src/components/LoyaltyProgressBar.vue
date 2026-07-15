<template>
  <div class="loyalty-progress-bar">
    <!-- Header -->
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2">
        <!-- Type icon -->
        <span
          class="w-6 h-6 rounded-full flex items-center justify-center"
          :class="{
            'bg-pink-100': rule.type === 'punch-card',
            'bg-blue-100': rule.type === 'rebooking',
            'bg-green-100': rule.type === 'points'
          }"
        >
          <svg v-if="rule.type === 'punch-card'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-pink-600" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          <svg v-if="rule.type === 'rebooking'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
            <path d="M8 16.028a1 1 0 100 1.944 1 1 0 000-1.944zM7 15a3 3 0 100-6 3 3 0 000 6zM12 15a3 3 0 100-6 3 3 0 000 6zM11.944 8A1 1 0 1013.888 8a1 1 0 00-1.944 0z" />
          </svg>
        </span>

        <!-- Rule name -->
        <span class="text-sm font-medium text-gray-700">{{ getRuleName() }}</span>
      </div>

      <!-- Status badge -->
      <span
        class="px-2 py-1 rounded-full text-xs font-semibold"
        :class="{
          'bg-green-100 text-green-700': isQualified,
          'bg-yellow-100 text-yellow-700': !isQualified && progress > 0,
          'bg-gray-100 text-gray-500': progress === 0
        }"
      >
        {{ getStatusLabel() }}
      </span>
    </div>

    <!-- Punch Card Grid (for punch-card type) -->
    <div v-if="rule.type === 'punch-card'" class="mb-2">
      <div class="grid grid-cols-4 gap-1.5">
        <div
          v-for="i in rule.trigger_count"
          :key="i"
          class="w-full aspect-square rounded-lg flex items-center justify-center text-sm font-bold transition-all"
          :class="{
            'bg-gradient-to-br from-pink-400 to-pink-600 text-white shadow-md': i <= progress,
            'bg-gray-100 text-gray-400 border border-dashed border-gray-300': i > progress && !isQualified,
            'bg-gradient-to-br from-green-400 to-green-600 text-white shadow-lg ring-2 ring-green-300': isQualified
          }"
        >
          <svg v-if="i <= progress || isQualified" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span v-else>{{ i }}</span>
        </div>
      </div>
    </div>

    <!-- Progress Bar (for other types) -->
    <div v-if="rule.type !== 'punch-card'" class="mb-2">
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div
          class="h-3 rounded-full transition-all"
          :class="{
            'bg-gradient-to-r from-pink-400 to-pink-600': !isQualified,
            'bg-gradient-to-r from-green-400 to-green-600 ring-2 ring-green-300': isQualified
          }"
          :style="{ width: `${Math.min((progress / rule.trigger_count) * 100, 100)}%` }"
        ></div>
      </div>
    </div>

    <!-- Progress text -->
    <div class="flex items-center justify-between">
      <span class="text-xs text-gray-500">{{ progress }} / {{ rule.trigger_count }}</span>
      
      <!-- Remaining info -->
      <span v-if="!isQualified && progress > 0" class="text-xs font-medium text-pink-600">
        Faltan {{ rule.trigger_count - progress }} citas
      </span>

      <!-- Reward info when qualified -->
      <span v-if="isQualified" class="text-xs font-bold text-green-700 flex items-center gap-1">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        ¡Calificada! {{ getRewardLabel() }}
      </span>

      <!-- Rebooking eligibility -->
      <span v-if="rule.type === 'rebooking' && isQualified" class="text-xs font-bold text-green-700">
        ¡Eligible para rebooking!
      </span>
    </div>

    <!-- Service filter info -->
    <div v-if="rule.service_filter_name" class="mt-1">
      <span class="text-xs text-gray-400">Aplica para: {{ rule.service_filter_name }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  client: { type: Object, required: true },
  rules: { type: Array, required: true }
})

// Get the applicable rule for this client
const applicableRule = computed(() => {
  if (!props.client.appointments_count) return null
  
  // Find punch-card rules that apply to this client
  const punchCardRules = props.rules.filter(r => 
    r.type === 'punch-card' && 
    (r.client_id === null || r.client_id === props.client.id) &&
    props.client.appointments_count >= 1
  )
  
  if (punchCardRules.length > 0) {
    return punchCardRules[0]
  }
  
  // Find rebooking rules that apply
  const rebookingRules = props.rules.filter(r => 
    r.type === 'rebooking' && 
    (r.client_id === null || r.client_id === props.client.id) &&
    props.client.last_appointment_date
  )
  
  if (rebookingRules.length > 0) {
    return rebookingRules[0]
  }
  
  return null
})

const progress = computed(() => {
  if (!applicableRule.value || !props.client.appointments_count) return 0
  
  // For punch-card, use appointments count
  if (applicableRule.value.type === 'punch-card') {
    return props.client.appointments_count
  }
  
  // For rebooking, check eligibility window
  if (applicableRule.value.type === 'rebooking' && props.client.last_appointment_date) {
    const lastDate = new Date(props.client.last_appointment_date)
    const today = new Date()
    const daysSince = Math.floor((today - lastDate) / (1000 * 60 * 60 * 24))
    
    if (daysSince <= (applicableRule.value.rebooking_days || 7)) {
      return applicableRule.value.trigger_count // Fully eligible
    }
  }
  
  return 0
})

const isQualified = computed(() => {
  if (!applicableRule.value) return false
  
  if (applicableRule.value.type === 'punch-card') {
    return progress.value >= applicableRule.value.trigger_count
  }
  
  if (applicableRule.value.type === 'rebooking') {
    const lastDate = new Date(props.client.last_appointment_date)
    const today = new Date()
    const daysSince = Math.floor((today - lastDate) / (1000 * 60 * 60 * 24))
    
    return daysSince <= (applicableRule.value.rebooking_days || 7) && 
           props.client.appointments_count >= applicableRule.value.trigger_count
  }
  
  return false
})

function getRuleName() {
  if (!applicableRule.value) return 'Sin regla activa'
  
  const name = applicableRule.value.name || ''
  if (name) return name
  
  switch (applicableRule.value.type) {
    case 'punch-card':
      return `Punch Card - ${applicableRule.value.trigger_count} citas`
    case 'rebooking':
      return `Rebooking - ${applicableRule.value.rebooking_days || 7} días`
    default:
      return 'Regla de fidelización'
  }
}

function getStatusLabel() {
  if (!applicableRule.value) return 'Sin regla'
  
  if (isQualified.value) return '¡Calificada!'
  
  switch (applicableRule.value.type) {
    case 'punch-card':
      return progress.value > 0 ? `${progress.value}/${applicableRule.value.trigger_count}` : 'Sin citas'
    case 'rebooking':
      return isQualified.value ? 'Eligible' : 'No elegible'
    default:
      return progress.value > 0 ? `${progress.value}/${applicableRule.value.trigger_count}` : 'Sin progreso'
  }
}

function getRewardLabel() {
  if (!applicableRule.value) return ''
  
  switch (applicableRule.value.reward_type) {
    case 'discount':
      return `${applicableRule.value.reward_value}% descuento`
    case 'free-service':
      return 'Servicio gratis'
    case 'upgrade':
      return `$${applicableRule.value.reward_value} upgrade`
    default:
      return ''
  }
}
</script>

<style scoped>
.loyalty-progress-bar {
  padding: 12px;
  background: linear-gradient(to bottom, #fafafa, #ffffff);
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
</style>