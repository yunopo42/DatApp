import { useEffect, useState } from 'react'

import { fetchWorkspaces, type Workspace } from '../lib/api'
import { WorkspaceForm } from './WorkspaceForm'

export function WorkspacePanel({ accessToken }: { accessToken: string }) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [formOpen, setFormOpen] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    void fetchWorkspaces(accessToken, controller.signal)
      .then((loadedWorkspaces) => {
        setWorkspaces(loadedWorkspaces)
        setError(null)
      })
      .catch((loadError: unknown) => {
        if (!controller.signal.aborted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Unable to load your workspaces.',
          )
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      })

    return () => controller.abort()
  }, [accessToken, reloadKey])

  function retry() {
    setLoading(true)
    setError(null)
    setReloadKey((currentKey) => currentKey + 1)
  }

  function handleCreated(workspace: Workspace) {
    setWorkspaces((currentWorkspaces) => [
      workspace,
      ...currentWorkspaces.filter((current) => current.id !== workspace.id),
    ])
    setFormOpen(false)
    setSuccessMessage(`${workspace.name} was created successfully.`)
  }

  return (
    <section
      aria-labelledby="workspaces-title"
      className="ai-card rounded-2xl border border-[#e8dff2] bg-white/90 p-6 shadow-[0_10px_35px_rgba(76,29,149,0.06)] backdrop-blur"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b5bb5]">
            Your account
          </p>
          <h2
            id="workspaces-title"
            className="mt-2 text-lg font-semibold tracking-[-0.02em]"
          >
            Workspaces
          </h2>
          <p className="mt-1 text-sm text-[#81738e]">
            Secure spaces available through your current membership.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {!loading && error === null && (
            <span className="rounded-full bg-[#f1e9fb] px-3 py-1 text-[11px] font-semibold text-[#7136b5]">
              {workspaces.length}{' '}
              {workspaces.length === 1 ? 'workspace' : 'workspaces'}
            </span>
          )}
          {!loading && error === null && (
            <button
              type="button"
              onClick={() => {
                setFormOpen((current) => !current)
                setSuccessMessage(null)
              }}
              aria-expanded={formOpen}
              className="ai-button rounded-xl px-3.5 py-2 text-xs font-semibold text-white shadow-[0_8px_20px_rgba(126,34,206,0.18)]"
            >
              {formOpen ? 'Close form' : 'New workspace'}
            </button>
          )}
        </div>
      </div>

      {formOpen && (
        <WorkspaceForm
          accessToken={accessToken}
          onCancel={() => setFormOpen(false)}
          onCreated={handleCreated}
        />
      )}

      {successMessage !== null && (
        <p
          role="status"
          className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-xs text-emerald-700"
        >
          {successMessage}
        </p>
      )}

      <div className="mt-6" aria-live="polite">
        {loading ? (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {[0, 1, 2].map((item) => (
              <div
                key={item}
                className="h-28 animate-pulse rounded-2xl border border-[#ece3f4] bg-[#f7f2fc]"
              />
            ))}
          </div>
        ) : error !== null ? (
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-rose-200 bg-rose-50 p-4">
            <div>
              <p className="text-sm font-semibold text-rose-800">
                Workspaces could not be loaded
              </p>
              <p className="mt-1 text-xs text-rose-700">{error}</p>
            </div>
            <button
              type="button"
              onClick={retry}
              className="rounded-xl border border-rose-200 bg-white px-3 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-100"
            >
              Try again
            </button>
          </div>
        ) : workspaces.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[#d9c8e8] bg-[#fbf8fe] px-5 py-8 text-center">
            <div className="mx-auto grid size-11 place-items-center rounded-2xl bg-[#eee2fa] text-[#7c3aed]">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="size-5"
                aria-hidden="true"
              >
                <path d="M3 7h7l2 2h9v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" />
              </svg>
            </div>
            <p className="mt-4 text-sm font-semibold">No workspaces yet</p>
            <p className="mx-auto mt-1 max-w-md text-xs leading-5 text-[#867990]">
              Your account is ready. Use New workspace to create the first one.
            </p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {workspaces.map((workspace) => (
              <article
                key={workspace.id}
                className="rounded-2xl border border-[#e5d9ef] bg-[#fcfaff] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">
                      {workspace.name}
                    </p>
                    <p className="mt-1 truncate text-xs text-[#8a7997]">
                      /{workspace.slug}
                    </p>
                  </div>
                  <span className="rounded-full bg-[#eee3f8] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-[#72409d]">
                    {workspace.plan}
                  </span>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
