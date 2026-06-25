// src/api/auth.ts
import { apiClient } from '@/api/client'
import type { ApiResponse, User, UserProfileUpdate } from '@/types'

/** Ensures the browser has a CSRF cookie for credentialed auth requests. */
export function fetchCsrfToken() {
  return apiClient.get<{ success: boolean }>('/auth/csrf/')
}

/** Authenticates a user with secure, HttpOnly cookie-backed tokens. */
export function loginWithPassword(username: string, password: string) {
  return apiClient.post<{ success: boolean }>('/auth/token/', { username, password })
}

/** Clears secure authentication cookies on the server. */
export function logoutSession() {
  return apiClient.post<{ success: boolean }>('/auth/logout/')
}

/** Fetches the authenticated user's editable profile data. */
export function fetchCurrentUser() {
  return apiClient.get<ApiResponse<User>>('/auth/me/')
}

/** Updates profile fields that are safe for user self-service editing. */
export function updateCurrentUser(payload: UserProfileUpdate) {
  return apiClient.patch<ApiResponse<User>>('/auth/me/', payload)
}
