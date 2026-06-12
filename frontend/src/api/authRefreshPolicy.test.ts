import assert from 'node:assert/strict'
import { test } from 'node:test'
import { isAuthenticationEndpoint, shouldRefreshAccessToken } from './authRefreshPolicy.ts'

test('authentication endpoints are excluded from refresh attempts', () => {
  assert.equal(isAuthenticationEndpoint('/auth/token/'), true)
  assert.equal(isAuthenticationEndpoint('/api/v1/auth/token/refresh/'), true)
  assert.equal(isAuthenticationEndpoint('http://localhost/api/v1/auth/token/?next=1'), true)
})

test('only first non-authentication 401 response can refresh the access token', () => {
  assert.equal(shouldRefreshAccessToken(401, { url: '/documents/' }), true)
  assert.equal(shouldRefreshAccessToken(401, { url: '/documents/', _retry: true }), false)
  assert.equal(shouldRefreshAccessToken(401, { url: '/auth/token/refresh/' }), false)
  assert.equal(shouldRefreshAccessToken(429, { url: '/documents/' }), false)
})
