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
  detail?: string | Array<{ msg?: string }>
}

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export type Workspace = {
  id: string
  name: string
  slug: string
  plan: string
  role: 'owner' | 'admin' | 'editor' | 'viewer'
  owner_user_id: string
  created_at: string
  updated_at: string
}

export type WorkspaceCreateInput = {
  name: string
  slug: string
}

export type Project = {
  id: string
  workspace_id: string
  name: string
  description: string | null
  status: 'active' | 'archived'
  created_by: string
  created_at: string
  updated_at: string
}

export type ProjectCreateInput = {
  name: string
  description?: string
}

function errorMessage(body: ApiErrorBody, fallback: string): string {
  if (typeof body.detail === 'string') {
    return body.detail
  }

  const validationMessage = body.detail?.[0]?.msg
  return validationMessage ?? fallback
}

async function requestJson<T>(
  path: string,
  accessToken: string,
  fallbackError: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...(options.body === undefined ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  })

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody
    throw new ApiError(errorMessage(body, fallbackError), response.status)
  }

  return (await response.json()) as T
}

export async function fetchCurrentUser(
  accessToken: string,
  signal?: AbortSignal,
): Promise<CurrentUserProfile> {
  return requestJson<CurrentUserProfile>(
    '/api/v1/auth/me',
    accessToken,
    'Unable to load your DatApp profile.',
    {
      signal,
    },
  )
}

export function fetchWorkspaces(
  accessToken: string,
  signal?: AbortSignal,
): Promise<Workspace[]> {
  return requestJson<Workspace[]>(
    '/api/v1/workspaces',
    accessToken,
    'Unable to load your workspaces.',
    { signal },
  )
}

export function createWorkspace(
  accessToken: string,
  input: WorkspaceCreateInput,
  signal?: AbortSignal,
): Promise<Workspace> {
  return requestJson<Workspace>(
    '/api/v1/workspaces',
    accessToken,
    'Unable to create the workspace.',
    {
      method: 'POST',
      body: JSON.stringify(input),
      signal,
    },
  )
}

export function fetchProjects(
  accessToken: string,
  workspaceId: string,
  signal?: AbortSignal,
): Promise<Project[]> {
  return requestJson<Project[]>(
    `/api/v1/workspaces/${workspaceId}/projects`,
    accessToken,
    'Unable to load this workspace\'s projects.',
    { signal },
  )
}

export function createProject(
  accessToken: string,
  workspaceId: string,
  input: ProjectCreateInput,
  signal?: AbortSignal,
): Promise<Project> {
  return requestJson<Project>(
    `/api/v1/workspaces/${workspaceId}/projects`,
    accessToken,
    'Unable to create the project.',
    {
      method: 'POST',
      body: JSON.stringify(input),
      signal,
    },
  )
}
