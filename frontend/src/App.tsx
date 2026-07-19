import { useEffect, useState } from 'react'

type ServiceStatus = 'checking' | 'ready' | 'unavailable'
type IconName =
  | 'activity'
  | 'chart'
  | 'database'
  | 'folder'
  | 'grid'
  | 'help'
  | 'home'
  | 'refresh'
  | 'settings'
  | 'sparkles'
  | 'upload'

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

async function fetchServiceStatus(): Promise<ServiceStatus> {
  try {
    const response = await fetch(`${apiBaseUrl}/health/ready`)
    const body = (await response.json()) as { status?: string }
    return response.ok && body.status === 'ready' ? 'ready' : 'unavailable'
  } catch {
    return 'unavailable'
  }
}

function currentTime(): string {
  return new Intl.DateTimeFormat('en', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date())
}

const iconPaths: Record<IconName, React.ReactNode> = {
  activity: <path d="M4 12h3l2-6 4 12 2-6h5" />,
  chart: <path d="M5 19V9m7 10V5m7 14v-7" />,
  database: (
    <>
      <ellipse cx="12" cy="5" rx="7" ry="3" />
      <path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" />
    </>
  ),
  folder: <path d="M3 7h7l2 2h9v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" />,
  grid: <path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" />,
  help: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.8 9a2.3 2.3 0 1 1 3.1 2.2c-.9.4-.9 1-.9 1.8M12 17h.01" />
    </>
  ),
  home: <path d="m3 11 9-8 9 8v9h-6v-6H9v6H3z" />,
  refresh: <path d="M20 7v5h-5M4 17v-5h5m10.2-3A8 8 0 0 0 6 6l-2 2m.8 7A8 8 0 0 0 18 18l2-2" />,
  settings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z" />
    </>
  ),
  sparkles: <path d="m12 3 1.2 3.8L17 8l-3.8 1.2L12 13l-1.2-3.8L7 8l3.8-1.2L12 3Zm6 10 .8 2.2L21 16l-2.2.8L18 19l-.8-2.2L15 16l2.2-.8L18 13ZM6 14l.8 2.2L9 17l-2.2.8L6 20l-.8-2.2L3 17l2.2-.8L6 14Z" />,
  upload: <path d="M12 16V4m0 0L7 9m5-5 5 5M5 14v5h14v-5" />,
}

function Icon({ name, className = 'size-5' }: { name: IconName; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {iconPaths[name]}
    </svg>
  )
}

const navigation = [
  { label: 'Overview', icon: 'home' as const, active: true },
  { label: 'Projects', icon: 'folder' as const },
  { label: 'Datasets', icon: 'database' as const },
  { label: 'Reports', icon: 'chart' as const },
]

function App() {
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>('checking')
  const [lastChecked, setLastChecked] = useState<string>('Checking now')

  useEffect(() => {
    let active = true
    void fetchServiceStatus().then((status) => {
      if (active) {
        setServiceStatus(status)
        setLastChecked(currentTime())
      }
    })
    return () => {
      active = false
    }
  }, [])

  const isReady = serviceStatus === 'ready'

  return (
    <div className="min-h-screen bg-[#f3f6f4] text-[#17211b] lg:grid lg:grid-cols-[248px_1fr]">
      <aside className="hidden min-h-screen border-r border-[#dfe6e1] bg-[#10281d] px-4 py-5 text-white lg:flex lg:flex-col">
        <div className="flex items-center gap-3 px-2">
          <div className="grid size-10 place-items-center rounded-xl bg-[#d9f99d] text-[#153d27] shadow-[0_8px_24px_rgba(0,0,0,0.18)]">
            <Icon name="sparkles" className="size-5" />
          </div>
          <div>
            <p className="text-lg font-semibold tracking-[-0.03em]">DatApp</p>
            <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-[#91aa9c]">Data workspace</p>
          </div>
        </div>

        <nav className="mt-10 space-y-1" aria-label="Primary navigation">
          {navigation.map((item) => (
            <button
              key={item.label}
              type="button"
              disabled={!item.active}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition ${
                item.active
                  ? 'bg-white/12 text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]'
                  : 'cursor-not-allowed text-[#87a093]'
              }`}
            >
              <Icon name={item.icon} className="size-[18px]" />
              {item.label}
              {!item.active && <span className="ml-auto text-[9px] uppercase tracking-wider text-[#6f887b]">Soon</span>}
            </button>
          ))}
        </nav>

        <div className="mt-auto space-y-2">
          <button type="button" className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-[#a8bbb1]">
            <Icon name="help" className="size-[18px]" /> Help center
          </button>
          <button type="button" className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-[#a8bbb1]">
            <Icon name="settings" className="size-[18px]" /> Settings
          </button>
          <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-3">
            <p className="text-xs font-medium text-white">Local development</p>
            <p className="mt-1 text-[11px] leading-4 text-[#91aa9c]">Authentication provider setup is next.</p>
          </div>
        </div>
      </aside>

      <main className="min-w-0">
        <header className="flex h-16 items-center justify-between border-b border-[#dfe6e1] bg-white/80 px-5 backdrop-blur md:px-8 lg:h-[76px]">
          <div className="flex items-center gap-3 lg:hidden">
            <div className="grid size-9 place-items-center rounded-xl bg-[#173e2a] text-[#d9f99d]">
              <Icon name="sparkles" className="size-4" />
            </div>
            <span className="font-semibold">DatApp</span>
          </div>
          <div className="hidden lg:block">
            <p className="text-sm font-semibold">Overview</p>
            <p className="text-xs text-[#718078]">Your data workspace at a glance</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-[#dce5df] bg-white px-3 py-1.5 text-xs font-medium text-[#526159] sm:flex">
              <span className={`size-2 rounded-full ${isReady ? 'bg-[#3eb875]' : serviceStatus === 'checking' ? 'animate-pulse bg-amber-400' : 'bg-rose-500'}`} />
              {isReady ? 'Systems online' : serviceStatus === 'checking' ? 'Checking systems' : 'Service unavailable'}
            </div>
            <button type="button" disabled className="rounded-xl bg-[#173e2a] px-4 py-2 text-xs font-semibold text-white opacity-60">
              Sign in soon
            </button>
          </div>
        </header>

        <div className="mx-auto max-w-[1440px] space-y-6 p-5 md:p-8 lg:p-10">
          <section className="relative overflow-hidden rounded-[28px] bg-[#173e2a] p-6 text-white shadow-[0_18px_60px_rgba(23,62,42,0.16)] md:p-9">
            <div className="absolute -right-12 -top-20 size-72 rounded-full border-[52px] border-[#d9f99d]/10" />
            <div className="absolute bottom-[-90px] right-36 size-52 rounded-full bg-[#5cce91]/10 blur-2xl" />
            <div className="relative max-w-2xl">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#d9f99d]">
                <Icon name="sparkles" className="size-3.5" /> Foundation ready
              </div>
              <h1 className="text-3xl font-semibold leading-tight tracking-[-0.04em] md:text-[44px]">
                Turn messy data into clear decisions.
              </h1>
              <p className="mt-4 max-w-xl text-sm leading-6 text-[#c1d1c8] md:text-base">
                DatApp will bring upload, quality checks, statistics, and visual reports into one focused workspace.
              </p>
              <div className="mt-7 flex flex-wrap items-center gap-3">
                <a href="#getting-started" className="inline-flex items-center gap-2 rounded-xl bg-[#d9f99d] px-4 py-2.5 text-sm font-semibold text-[#173e2a] transition hover:bg-[#e6ffb7]">
                  Explore the foundation <span aria-hidden="true">→</span>
                </a>
                <div className="flex max-w-full items-start gap-2 text-xs leading-5 text-[#9fb5aa]">
                  <Icon name="upload" className="mt-0.5 size-4 shrink-0" /> Dataset upload is the next product phase
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[
              { label: 'Projects', value: '0', helper: 'Workspace API next', icon: 'folder' as const },
              { label: 'Datasets', value: '0', helper: 'Upload phase pending', icon: 'database' as const },
              { label: 'Analyses', value: '0', helper: 'No runs yet', icon: 'activity' as const },
              { label: 'Data quality', value: '—', helper: 'Waiting for data', icon: 'chart' as const },
            ].map((item) => (
              <article key={item.label} className="rounded-2xl border border-[#e0e7e2] bg-white p-5 shadow-[0_8px_30px_rgba(31,52,40,0.04)]">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-[#748078]">{item.label}</p>
                    <p className="mt-2 text-3xl font-semibold tracking-[-0.04em]">{item.value}</p>
                  </div>
                  <div className="grid size-10 place-items-center rounded-xl bg-[#eef5f0] text-[#2e6a49]">
                    <Icon name={item.icon} className="size-[18px]" />
                  </div>
                </div>
                <p className="mt-5 text-[11px] text-[#96a099]">{item.helper}</p>
              </article>
            ))}
          </section>

          <section id="getting-started" className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
            <article className="rounded-2xl border border-[#e0e7e2] bg-white p-6 shadow-[0_8px_30px_rgba(31,52,40,0.04)]">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold tracking-[-0.02em]">Getting started</h2>
                  <p className="mt-1 text-sm text-[#78847d]">The path from foundation to your first analysis.</p>
                </div>
                <span className="rounded-full bg-[#eef5f0] px-3 py-1 text-[11px] font-semibold text-[#36704f]">2 of 5 ready</span>
              </div>
              <div className="mt-6 space-y-1">
                {[
                  { title: 'Development environment', detail: 'Frontend, backend, and PostgreSQL are running.', done: true },
                  { title: 'Secure API foundation', detail: 'OIDC verification and current-user endpoint are tested.', done: true },
                  { title: 'Connect an identity provider', detail: 'Required before testing protected workspace actions.', done: false },
                  { title: 'Create your first workspace', detail: 'Workspace and project screens will follow authentication.', done: false },
                  { title: 'Upload a dataset', detail: 'CSV and XLSX support comes after project APIs.', done: false },
                ].map((step, index) => (
                  <div key={step.title} className="flex gap-4 rounded-xl p-3 hover:bg-[#f7f9f7]">
                    <div className={`grid size-8 shrink-0 place-items-center rounded-full text-xs font-bold ${step.done ? 'bg-[#dff5e7] text-[#238451]' : 'border border-[#dfe5e1] text-[#87928b]'}`}>
                      {step.done ? '✓' : index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{step.title}</p>
                      <p className="mt-1 text-xs leading-5 text-[#7e8982]">{step.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-2xl border border-[#e0e7e2] bg-white p-6 shadow-[0_8px_30px_rgba(31,52,40,0.04)]">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold tracking-[-0.02em]">System status</h2>
                  <p className="mt-1 text-xs text-[#8b958f]">Last checked {lastChecked}</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setServiceStatus('checking')
                    void fetchServiceStatus().then((status) => {
                      setServiceStatus(status)
                      setLastChecked(currentTime())
                    })
                  }}
                  aria-label="Refresh system status"
                  className="grid size-9 place-items-center rounded-xl border border-[#dfe6e1] text-[#617069] transition hover:bg-[#f3f7f4]"
                >
                  <Icon name="refresh" className={`size-4 ${serviceStatus === 'checking' ? 'animate-spin' : ''}`} />
                </button>
              </div>
              <div className="mt-7 space-y-5">
                {[
                  { label: 'Frontend application', status: 'Online', ready: true },
                  { label: 'FastAPI backend', status: isReady ? 'Online' : serviceStatus === 'checking' ? 'Checking' : 'Unavailable', ready: isReady },
                  { label: 'PostgreSQL database', status: isReady ? 'Healthy' : serviceStatus === 'checking' ? 'Checking' : 'Unavailable', ready: isReady },
                ].map((service) => (
                  <div key={service.label} className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <span className={`size-2.5 rounded-full ${service.ready ? 'bg-[#3eb875] shadow-[0_0_0_4px_rgba(62,184,117,0.12)]' : serviceStatus === 'checking' ? 'animate-pulse bg-amber-400' : 'bg-rose-500'}`} />
                      <span className="text-sm font-medium">{service.label}</span>
                    </div>
                    <span className="text-xs text-[#7c8981]">{service.status}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8 rounded-xl bg-[#f1f7f3] p-4">
                <div className="flex items-center gap-2 text-xs font-semibold text-[#306d4b]">
                  <Icon name="grid" className="size-4" /> Local environment
                </div>
                <p className="mt-2 text-[11px] leading-5 text-[#718078]">This dashboard reads the live FastAPI readiness endpoint. It is not using mock health data.</p>
              </div>
            </article>
          </section>
        </div>
      </main>
    </div>
  )
}

export default App
