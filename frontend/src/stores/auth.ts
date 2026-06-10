// src/stores/auth.ts
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { apiClient } from '@/api/client'
import { fetchCurrentUser, updateCurrentUser } from '@/api/auth'
import type { User, UserProfileUpdate } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const fullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
  })

  async function login(username: string, password: string) {
    const response = await apiClient.post<{ access: string; refresh: string }>(
      '/auth/token/',
      { username, password }
    )
    persistTokens(response.data.access, response.data.refresh)
    await fetchUser()
  }

  async function fetchUser() {
    const response = await fetchCurrentUser()
    user.value = response.data.data
  }

  async function updateProfile(payload: UserProfileUpdate) {
    const response = await updateCurrentUser(payload)
    user.value = response.data.data
  }

  function persistTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isAuthenticated, fullName, login, logout, fetchUser, updateProfile }
})
