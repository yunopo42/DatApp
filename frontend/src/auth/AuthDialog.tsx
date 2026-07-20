import { useState, type FormEvent } from 'react'

import { useAuth } from './useAuth'

type AuthMode = 'sign-in' | 'sign-up'

export function AuthDialog({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const { signIn, signUp } = useAuth()
  const [mode, setMode] = useState<AuthMode>('sign-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (!open) {
    return null
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage(null)
    setSubmitting(true)

    const result =
      mode === 'sign-in'
        ? await signIn(email.trim(), password)
        : await signUp(email.trim(), password, displayName.trim())

    setSubmitting(false)
    if (result.error !== null) {
      setMessage(result.error)
      return
    }
    if (result.needsEmailConfirmation) {
      setMessage('Check your email to confirm your DatApp account.')
      return
    }
    onClose()
  }

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode)
    setMessage(null)
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-[#12051f]/70 p-4 backdrop-blur-sm">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
        className="w-full max-w-md overflow-hidden rounded-[28px] border border-white/20 bg-white shadow-[0_32px_100px_rgba(46,16,101,0.4)]"
      >
        <div className="ai-hero px-7 py-6 text-white">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#ead7ff]">
                Supabase Auth
              </p>
              <h2 id="auth-title" className="mt-2 text-2xl font-semibold">
                {mode === 'sign-in' ? 'Welcome back' : 'Create your account'}
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close authentication dialog"
              className="grid size-9 place-items-center rounded-full bg-white/10 text-xl text-white transition hover:bg-white/20"
            >
              ×
            </button>
          </div>
        </div>

        <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4 p-7">
          {mode === 'sign-up' && (
            <label className="block text-sm font-medium text-[#4a365c]">
              Display name
              <input
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                required
                maxLength={120}
                autoComplete="name"
                className="mt-2 w-full rounded-xl border border-[#dfd2ea] bg-[#fcfaff] px-4 py-3 text-[#251536] outline-none transition focus:border-[#a855f7] focus:ring-4 focus:ring-[#a855f7]/10"
              />
            </label>
          )}
          <label className="block text-sm font-medium text-[#4a365c]">
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
              className="mt-2 w-full rounded-xl border border-[#dfd2ea] bg-[#fcfaff] px-4 py-3 text-[#251536] outline-none transition focus:border-[#a855f7] focus:ring-4 focus:ring-[#a855f7]/10"
            />
          </label>
          <label className="block text-sm font-medium text-[#4a365c]">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={8}
              autoComplete={mode === 'sign-in' ? 'current-password' : 'new-password'}
              className="mt-2 w-full rounded-xl border border-[#dfd2ea] bg-[#fcfaff] px-4 py-3 text-[#251536] outline-none transition focus:border-[#a855f7] focus:ring-4 focus:ring-[#a855f7]/10"
            />
          </label>

          {message !== null && (
            <p className="rounded-xl bg-[#f4eaff] px-4 py-3 text-sm text-[#6b2ca0]">
              {message}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="ai-button w-full rounded-xl px-4 py-3 text-sm font-semibold text-white shadow-[0_12px_30px_rgba(126,34,206,0.24)] disabled:cursor-wait disabled:opacity-60"
          >
            {submitting
              ? 'Please wait…'
              : mode === 'sign-in'
                ? 'Sign in'
                : 'Create account'}
          </button>

          <button
            type="button"
            onClick={() =>
              switchMode(mode === 'sign-in' ? 'sign-up' : 'sign-in')
            }
            className="w-full text-sm font-medium text-[#7c3aed]"
          >
            {mode === 'sign-in'
              ? 'New to DatApp? Create an account'
              : 'Already have an account? Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
