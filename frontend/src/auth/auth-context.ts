import { createContext } from 'react'
import type { Session, User } from '@supabase/supabase-js'

import type { CurrentUserProfile } from '../lib/api'

export type AuthResult = {
  error: string | null
  needsEmailConfirmation?: boolean
}

export type AuthContextValue = {
  configured: boolean
  loading: boolean
  session: Session | null
  user: User | null
  profile: CurrentUserProfile | null
  profileLoading: boolean
  profileError: string | null
  signIn: (email: string, password: string) => Promise<AuthResult>
  signUp: (
    email: string,
    password: string,
    displayName: string,
  ) => Promise<AuthResult>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
