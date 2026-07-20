import { useEffect, useRef, useState } from 'react'

import { fetchWorkspaces, type Workspace } from '../lib/api'
import { WorkspaceForm } from './WorkspaceForm'

export function WorkspacePanel({
  accessToken,
  onWorkspaceSelected,
}: {
  accessToken: string
  onWorkspaceSelected: (workspace: Workspace | null) => void
}) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [formOpen, setFormOpen] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string | null>(
    null,
  )
  const selectedWorkspaceIdRef = useRef<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    void fetchWorkspaces(accessToken, controller.signal)
      .then((loadedWorkspaces) => {
        setWorkspaces(loadedWorkspaces)
        setError(null)
        const selectedWorkspace =
          loadedWorkspaces.find(
            (workspace) => workspace.id === selectedWorkspaceIdRef.current,
          ) ??
          loadedWorkspaces[0] ??
          null
        selectedWorkspaceIdRef.current = selectedWorkspace?.id ?? null
        setSelectedWorkspaceId(selectedWorkspace?.id ?? null)
        onWorkspaceSelected(selectedWorkspace)
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
  }, [accessToken, onWorkspaceSelected, reloadKey])

  useEffect(
    () => () => {
      onWorkspaceSelected(null)
    },
    [onWorkspaceSelected],
  )

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
    selectedWorkspaceIdRef.current = workspace.id
    setSelectedWorkspaceId(workspace.id)
    onWorkspaceSelected(workspace)
  }

  function selectWorkspace(workspace: Workspace) {
    selectedWorkspaceIdRef.current = workspace.id
    setSelectedWorkspaceId(workspace.id)
    setSuccessMessage(null)
    onWorkspaceSelected(workspace)
  }

  const selectedWorkspace =
    workspaces.find((workspace) => workspace.id === selectedWorkspaceId) ?? null

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

      {selectedWorkspace !== null && (
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#cdb5e4] bg-[linear-gradient(120deg,#f8f1ff,#fdf9ff)] px-4 py-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#8b5bb5]">
              Active workspace
            </p>
            <p className="mt-1 text-sm font-semibold">{selectedWorkspace.name}</p>
          </div>
          <span className="rounded-full bg-white px-3 py-1 text-xs text-[#765d8a] shadow-sm">
            /{selectedWorkspace.slug}
          </span>
        </div>
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
            {workspaces.map((workspace) => {
              const selected = workspace.id === selectedWorkspaceId
              return (
              <button
                key={workspace.id}
                type="button"
                onClick={() => selectWorkspace(workspace)}
                aria-pressed={selected}
                className={`rounded-2xl border p-4 text-left transition ${
                  selected
                    ? 'border-[#a855f7] bg-[#f7edff] shadow-[0_10px_28px_rgba(126,34,206,0.12)]'
                    : 'border-[#e5d9ef] bg-[#fcfaff] hover:border-[#cdb5e4] hover:bg-[#faf6ff]'
                }`}
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
                  <div className="flex flex-col items-end gap-2">
                    <span className="rounded-full bg-[#eee3f8] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-[#72409d]">
                      {workspace.plan}
                    </span>
                    {selected && (
                      <span className="text-[10px] font-semibold uppercase tracking-wide text-[#7c3aed]">
                        Active
                      </span>
                    )}
                  </div>
                </div>
              </button>
            )})}
          </div>
        )}
      </div>
    </section>
  )
}
