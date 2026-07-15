// API Client with security features (CORS protection, XSS sanitization)
import axios from 'axios'
import DOMPurify from 'dompurify'

// Base URL - proxied through Vite dev server in development mode
const API_BASE_URL = '/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// XSS sanitization utility for user input
export function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input)
}

// Sanitize all string values in an object recursively
export function sanitizeObject(obj: Record<string, any>): Record<string, any> {
  const sanitized: Record<string, any> = {}
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = DOMPurify.sanitize(value)
    } else if (Array.isArray(value)) {
      sanitized[key] = value.map(item => 
        typeof item === 'string' ? DOMPurify.sanitize(item) : item
      )
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value as Record<string, any>)
    } else {
      sanitized[key] = value
    }
  }
  return sanitized
}

// Request interceptor - add auth token and sanitize outgoing data
apiClient.interceptors.request.use(
  (config) => {
    // Add JWT token from localStorage if available
    const token = localStorage.getItem('jwt_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Sanitize request data for POST/PUT/PATCH requests
    if (['POST', 'PUT', 'PATCH'].includes(config.method?.toUpperCase() || '')) {
      if (config.data && typeof config.data === 'object') {
        config.data = sanitizeObject(config.data)
      }
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and token expiration
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear localStorage and redirect to login
      localStorage.removeItem('jwt_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints for NailBook
export const api = {
  // Clients
  clients: {
    list: (params?: { page?: number; limit?: number }) => 
      apiClient.get('/clients', { params }),
    get: (id: string) => 
      apiClient.get(`/clients/${id}`),
    create: (data: Record<string, any>) => 
      apiClient.post('/clients', sanitizeObject(data)),
    update: (id: string, data: Record<string, any>) => 
      apiClient.put(`/clients/${id}`, sanitizeObject(data)),
    delete: (id: string) => 
      apiClient.delete(`/clients/${id}`),
  },

  // Services
  services: {
    list: (params?: { page?: number; limit?: number }) => 
      apiClient.get('/services', { params }),
    get: (id: string) => 
      apiClient.get(`/services/${id}`),
    create: (data: Record<string, any>) => 
      apiClient.post('/services', sanitizeObject(data)),
    update: (id: string, data: Record<string, any>) => 
      apiClient.put(`/services/${id}`, sanitizeObject(data)),
    delete: (id: string) => 
      apiClient.delete(`/services/${id}`),
  },

  // Appointments
  appointments: {
    list: (params?: { date_from?: string; date_to?: string; status?: string; client_id?: string }) => 
      apiClient.get('/appointments', { params }),
    get: (id: string) => 
      apiClient.get(`/appointments/${id}`),
    create: (data: Record<string, any>) => 
      apiClient.post('/appointments', sanitizeObject(data)),
    update: (id: string, data: Record<string, any>) => 
      apiClient.put(`/appointments/${id}`, sanitizeObject(data)),
    complete: (id: string) => 
      apiClient.patch(`/appointments/${id}/complete`),
    cancel: (id: string) => 
      apiClient.patch(`/appointments/${id}/cancel`),
  },

  // Loyalty
  loyalty: {
    listRules: () => 
      apiClient.get('/loyalty/rules'),
    getRule: (id: string) => 
      apiClient.get(`/loyalty/rules/${id}`),
    createRule: (data: Record<string, any>) => 
      apiClient.post('/loyalty/rules', sanitizeObject(data)),
    updateRule: (id: string, data: Record<string, any>) => 
      apiClient.put(`/loyalty/rules/${id}`, sanitizeObject(data)),
    deleteRule: (id: string) => 
      apiClient.delete(`/loyalty/rules/${id}`),
  },

  // Dashboard
  dashboard: {
    overview: () => 
      apiClient.get('/dashboard/overview'),
  },

  // Loyalty Status (additional endpoint)
  loyaltyStatus: (clientId: string) => 
    apiClient.get(`/loyalty/status/${clientId}`),
}

// Export default for convenience
export default api
