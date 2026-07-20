import { useEffect, useState, type ReactNode } from 'react'
import type { Session } from '@supabase/supabase-js'

import { AuthContext, type AuthResult } from './auth-context'
import { fetchCurrentUser, type CurrentUserProfile } from '../lib/api'
import { isSupabaseConfigured, supabase } from '../lib/supabase'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(isSupabaseConfigured)
  const [profile, setProfile] = useState<CurrentUserProfile | null>(null)
  const [profileError, setProfileError] = useState<string | null>(null)

  useEffect(() => {
    if (supabase === null) {
      return
    }

    let active = true
    void supabase.auth.getSession().then(({ data }) => {
      if (active) {
        setSession(data.session)
        setLoading(false)
      }
    })

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, nextSession) => {
        setProfile(null)
        setProfileError(null)
        setSession(nextSession)
        setLoading(false)
      },
    )

    return () => {
      active = false
      listener.subscription.unsubscribe()
    }
  }, [])

  useEffect(() => {
    if (session === null) {
      return
    }

    const controller = new AbortController()

    void fetchCurrentUser(session.access_token, controller.signal)
      .then((currentProfile) => {
        setProfile(currentProfile)
        setProfileError(null)
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setProfile(null)
          setProfileError(
            error instanceof Error
              ? error.message
              : 'Unable to load your DatApp profile.',
          )
        }
      })

    return () => controller.abort()
  }, [session])

  const profileLoading =
    session !== null && profile === null && profileError === null

  async function signIn(email: string, password: string): Promise<AuthResult> {
    if (supabase === null) {
      return { error: 'Authentication is not configured.' }
    }

    const { error } = await supabase.auth.signInWithPassword({ email, password })
    return { error: error?.message ?? null }
  }

  async function signUp(
    email: string,
    password: string,
    displayName: string,
  ): Promise<AuthResult> {
    if (supabase === null) {
      return { error: 'Authentication is not configured.' }
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { display_name: displayName },
      },
    })
    return {
      error: error?.message ?? null,
      needsEmailConfirmation: error === null && data.session === null,
    }
  }

  async function signOut(): Promise<void> {
    if (supabase !== null) {
      await supabase.auth.signOut()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        configured: isSupabaseConfigured,
        loading,
        session,
        user: session?.user ?? null,
        profile,
        profileLoading,
        profileError,
        signIn,
        signUp,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
