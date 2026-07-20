import { useState, type FormEvent } from 'react'

import { createProject, type Project } from '../lib/api'

function validateProject(name: string, description: string): string | null {
  if (name.length === 0) {
    return 'Project name is required.'
  }
  if (name.length > 160) {
    return 'Project name must be 160 characters or fewer.'
  }
  if (description.length > 2000) {
    return 'Project description must be 2,000 characters or fewer.'
  }
  return null
}

export function ProjectForm({
  accessToken,
  workspaceId,
  onCancel,
  onCreated,
}: {
  accessToken: string
  workspaceId: string
  onCancel: () => void
  onCreated: (project: Project) => void
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const normalizedName = name.trim().replace(/\s+/g, ' ')
    const normalizedDescription = description.trim()
    const validationError = validateProject(
      normalizedName,
      normalizedDescription,
    )
    if (validationError !== null) {
      setError(validationError)
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      const project = await createProject(accessToken, workspaceId, {
        name: normalizedName,
        ...(normalizedDescription === ''
          ? {}
          : { description: normalizedDescription }),
      })
      onCreated(project)
    } catch (createError: unknown) {
      setError(
        createError instanceof Error
          ? createError.message
          : 'Unable to create the project.',
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
      aria-labelledby="create-project-title"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 id="create-project-title" className="text-sm font-semibold">
            Create a project
          </h3>
          <p className="mt-1 text-xs leading-5 text-[#81738e]">
            Projects keep related datasets, analyses, and reports together.
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
          Project name
          <input
            value={name}
            onChange={(event) => {
              setName(event.target.value)
              setError(null)
            }}
            required
            maxLength={160}
            autoFocus
            autoComplete="off"
            placeholder="Customer retention analysis"
            className="mt-2 w-full cursor-text rounded-xl border border-[#dfd2ea] bg-white px-4 py-3 text-sm text-[#251536] caret-[#7c3aed] outline-none transition focus:border-[#a855f7] focus:ring-4 focus:ring-[#a855f7]/10"
          />
        </label>
        <label className="block text-xs font-semibold text-[#4a365c]">
          Description <span className="font-normal text-[#93849f]">(optional)</span>
          <textarea
            value={description}
            onChange={(event) => {
              setDescription(event.target.value)
              setError(null)
            }}
            maxLength={2000}
            rows={3}
            placeholder="Describe the question this project will answer."
            className="mt-2 w-full resize-y rounded-xl border border-[#dfd2ea] bg-white px-4 py-3 text-sm text-[#251536] caret-[#7c3aed] outline-none transition focus:border-[#a855f7] focus:ring-4 focus:ring-[#a855f7]/10"
          />
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
          {submitting ? 'Creating…' : 'Create project'}
        </button>
      </div>
    </form>
  )
}
