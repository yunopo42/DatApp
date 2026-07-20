const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

export type CurrentUserProfile = {
  id: string
  email: string
  display_name: string
  status: 'active' | 'suspended' | 'deleted'
  locale: string
  created_at: string
  updated_at: string
}

type ApiErrorBody = {
  detail?: string
}

export async function fetchCurrentUser(
  accessToken: string,
  signal?: AbortSignal,
): Promise<CurrentUserProfile> {
  const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    signal,
  })

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody
    throw new Error(body.detail ?? 'Unable to load your DatApp profile.')
  }

  return (await response.json()) as CurrentUserProfile
}
