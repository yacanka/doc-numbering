// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const fullName = computed(() =>
    user.value
      ? `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
      : ''
  )

  async function login(username: string, password: string) {
    const response = await apiClient.post<{ access: string; refresh: string }>(
      '/auth/token/',
      { username, password }
    )
    accessToken.value = response.data.access
    refreshToken.value = response.data.refresh
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    await fetchUser()
  }

  async function fetchUser() {
    const response = await apiClient.get<{ data: User }>('/auth/me/')
    user.value = response.data.data
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isAuthenticated, fullName, login, logout, fetchUser }
})