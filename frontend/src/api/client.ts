// src/api/client.ts
import axios, {
  AxiosHeaders,
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { useAuthStore } from '@/stores/auth'
import { isAuthenticationEndpoint, shouldRefreshAccessToken } from '@/api/authRefreshPolicy'

type TokenRefreshResponse = { access: string }
type RetriableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean }

class ApiClient {
  private instance: AxiosInstance
  private refreshTokenRequest: Promise<string> | null = null

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.instance.interceptors.request.use(
      (config) => this.authorizeRequest(config),
      (error) => Promise.reject(error)
    )

    this.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => this.handleUnauthorizedResponse(error)
    )
  }

  private authorizeRequest(config: InternalAxiosRequestConfig) {
    if (isAuthenticationEndpoint(config.url)) return config

    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers = AxiosHeaders.from(config.headers)
      config.headers.set('Authorization', `Bearer ${token}`)
    }
    return config
  }

  private async handleUnauthorizedResponse(error: any) {
    const originalRequest = error.config as RetriableRequestConfig | undefined

    if (!originalRequest || !shouldRefreshAccessToken(error.response?.status, originalRequest)) {
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const accessToken = await this.refreshAccessToken()
      originalRequest.headers = AxiosHeaders.from(originalRequest.headers)
      originalRequest.headers.set('Authorization', `Bearer ${accessToken}`)
      return this.instance(originalRequest)
    } catch (refreshError) {
      this.redirectToLogin()
      return Promise.reject(refreshError)
    }
  }

  private refreshAccessToken() {
    this.refreshTokenRequest ??= this.requestNewAccessToken().finally(() => {
      this.refreshTokenRequest = null
    })
    return this.refreshTokenRequest
  }

  private async requestNewAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) throw new Error('No refresh token')

    const response = await this.instance.post<TokenRefreshResponse>('/auth/token/refresh/', {
      refresh: refreshToken,
    })

    localStorage.setItem('access_token', response.data.access)
    return response.data.access
  }

  private redirectToLogin() {
    const authStore = useAuthStore()
    authStore.logout()

    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }

  get<T>(url: string, config?: AxiosRequestConfig) {
    return this.instance.get<T>(url, config)
  }

  post<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.post<T>(url, data, config)
  }

  put<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.put<T>(url, data, config)
  }

  patch<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.patch<T>(url, data, config)
  }

  delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.instance.delete<T>(url, config)
  }
}

export const apiClient = new ApiClient()
