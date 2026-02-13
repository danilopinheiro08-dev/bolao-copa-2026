import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

// Em produção, usa /api (nginx faz proxy para backend)
// Em desenvolvimento, usa localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important: send cookies with requests
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor for adding auth headers if needed
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Cookies are sent automatically via withCredentials
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
