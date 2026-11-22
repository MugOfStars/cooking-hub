export type Health = {
  status: string
  database: string
}

export async function fetchHealth(): Promise<Health> {
  const response = await fetch('/api/health')
  if (!response.ok) {
    throw new Error(`Health check failed: HTTP ${response.status}`)
  }
  return response.json()
}

/** Thrown on HTTP 401, so the app can send the user back to the login screen. */
export class UnauthorizedError extends Error {}

/** fetch() for JSON API calls. The session cookie is sent automatically (same origin). */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (response.status === 401) {
    const body = await response.json().catch(() => ({}))
    throw new UnauthorizedError(body.detail ?? 'Not logged in')
  }
  if (!response.ok) {
    throw new Error(`${path} failed: HTTP ${response.status}`)
  }
  return response.status === 204 ? (undefined as T) : response.json()
}

export type AuthStatus = {
  authenticated: boolean
  auth_enabled: boolean
}

export const fetchMe = () => request<AuthStatus>('/api/auth/me')

export const login = (password: string) =>
  request<void>('/api/auth/login', { method: 'POST', body: JSON.stringify({ password }) })

export const logout = () => request<void>('/api/auth/logout', { method: 'POST' })
