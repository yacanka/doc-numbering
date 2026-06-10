// src/api/auth.ts
import { apiClient } from '@/api/client'
import type { ApiResponse, User, UserProfileUpdate } from '@/types'

/** Fetches the authenticated user's editable profile data. */
export function fetchCurrentUser() {
  return apiClient.get<ApiResponse<User>>('/auth/me/')
}

/** Updates profile fields that are safe for user self-service editing. */
export function updateCurrentUser(payload: UserProfileUpdate) {
  return apiClient.patch<ApiResponse<User>>('/auth/me/', payload)
}
