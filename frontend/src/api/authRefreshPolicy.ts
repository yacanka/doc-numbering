// src/api/authRefreshPolicy.ts

const AUTHENTICATION_ENDPOINTS = ['/auth/token/', '/auth/token/refresh/']

export type RetriableRequest = {
  url?: string
  _retry?: boolean
}

/** Returns true when the request is an authentication request that must not refresh itself. */
export function isAuthenticationEndpoint(url?: string) {
  if (!url) return false

  const pathname = extractPathname(url)
  return AUTHENTICATION_ENDPOINTS.some((endpoint) => pathname.endsWith(endpoint))
}

/** Returns true when a response should trigger exactly one access-token refresh attempt. */
export function shouldRefreshAccessToken(status?: number, request?: RetriableRequest) {
  return status === 401 && !!request && !request._retry && !isAuthenticationEndpoint(request.url)
}

function extractPathname(url: string) {
  try {
    return new URL(url, 'http://localhost').pathname
  } catch {
    return url.split('?')[0]
  }
}
