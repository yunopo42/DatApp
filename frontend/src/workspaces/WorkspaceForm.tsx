import { useState, type FormEvent } from 'react'

import { createWorkspace, type Workspace } from '../lib/api'

const workspaceSlugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/

function createSlug(value: string): string {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 63)
}

function validateWorkspace(name: string, slug: string): string | null {
  if (name.length === 0) {
    return 'Workspace name is required.'
  }
  if (name.length > 120) {
    return 'Workspace name must be 120 characters or fewer.'
  }
  if (slug.length < 3 || slug.length > 63) {
    return 'Workspace slug must contain between 3 and 63 characters.'
  }
  if (!workspaceSlugPattern.test(slug)) {
    return 'Use lowercase letters, numbers, and single hyphens in the slug.'
  }
  return null
}

export function WorkspaceForm({
  accessToken,
  onCancel,
  onCreated,
}: {
  accessToken: string
  onCancel: () => void
  onCreated: (workspace: Workspace) => void
}) {
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [slugEdited, setSlugEdited] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateName(nextName: string) {
    setName(nextName)
    if (!slugEdited) {
      setSlug(createSlug(nextName))
    }
    setError(null)
  }

  function updateSlug(nextSlug: string) {
    setSlug(nextSlug.toLowerCase())
    setSlugEdited(true)
    setError(null)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const normalizedName = name.trim().replace(/\s+/g, ' ')
    const normalizedSlug = slug.trim()
    const validationError = validateWorkspace(normalizedName, normalizedSlug)
    if (validationError !== null) {
      setError(validationError)
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      const workspace = await createWorkspace(accessToken, {
        name: normalizedName,
        slug: normalizedSlug,
      })
      onCreated(workspace)
    } catch (createError: unknown) {
      setError(
        createError instanceof Error
          ? createError.message
          : 'Unable to create the workspace.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={(event) => void handleSubmit(event)}
      noValidate
      className="mt-6 rounded-2xl border border-[#ddcfeb] bg-[#faf6ff] p-5"
      aria-labelledby="create-workspace-title"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 id="create-workspace-title" className="text-sm font-semibold">
            Create a workspace
          </h3>
          <p className="mt-1 text-xs leading-5 text-[#81738e]">
            A workspace keeps projects, datasets, and members securely scoped.
          </p>
        </div>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="text-xs font-semibold text-[#765d8a] disabled:opacity-50"
        >
          Cancel
        </button>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <label className="block text-xs font-semibold text-[#4a365c]">
          Workspace name
          <input
            value={name}
            onChange={(event) => updateName(event.target.value)}
            required
            maxLength={120}
            autoFocus
            autoComplete="organization"
            placeholder="Acme Analytics"
            className="mt-2 w-full cursor-text rounded-xl border border-[#dfd2ea] bg-white px-4 py-3 text-sm text-[#251536] caret-[#7c3aed] outline-none transition focus:border-[#a855f7] focus:ring-4 focus:ring-[#a855f7]/10"
          />
        </label>
        <label className="block text-xs font-semibold text-[#4a365c]">
          Workspace slug
          <div className="mt-2 flex overflow-hidden rounded-xl border border-[#dfd2ea] bg-white transition focus-within:border-[#a855f7] focus-within:ring-4 focus-within:ring-[#a855f7]/10">
            <span className="grid place-items-center border-r border-[#eee5f5] bg-[#f8f4fb] px-3 text-sm text-[#9b8aa8]">
              /
            </span>
            <input
              value={slug}
              onChange={(event) => updateSlug(event.target.value)}
              required
              minLength={3}
              maxLength={63}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              autoComplete="off"
              placeholder="acme-analytics"
              className="min-w-0 flex-1 cursor-text px-3 py-3 text-sm text-[#251536] caret-[#7c3aed] outline-none"
            />
          </div>
          <span className="mt-2 block font-normal leading-5 text-[#93849f]">
            Lowercase letters, numbers, and single hyphens only.
          </span>
        </label>
      </div>

      {error !== null && (
        <p
          role="alert"
          className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-700"
        >
          {error}
        </p>
      )}

      <div className="mt-5 flex justify-end">
        <button
          type="submit"
          disabled={submitting}
          className="ai-button rounded-xl px-4 py-2.5 text-xs font-semibold text-white shadow-[0_10px_24px_rgba(126,34,206,0.2)] disabled:cursor-wait disabled:opacity-60"
        >
          {submitting ? 'Creating…' : 'Create workspace'}
        </button>
      </div>
    </form>
  )
}
