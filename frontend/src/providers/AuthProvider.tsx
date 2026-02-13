import { createContext, useContext, ReactNode, useState } from 'react'
import { useMe, useLogin, useRegister, useLogout } from '../api/hooks'
import type { User } from '../types'

interface AuthContextType {
  user: User | null
  loading: boolean
  error: string | null
  signInEmail: (email: string, password: string) => Promise<void>
  signUp: (email: string, name: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  refreshMe: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [error, setError] = useState<string | null>(null)
  const { data: user, isLoading: loading, refetch } = useMe()
  const loginMutation = useLogin()
  const registerMutation = useRegister()
  const logoutMutation = useLogout()

  const signInEmail = async (email: string, password: string) => {
    try {
      setError(null)
      await loginMutation.mutateAsync({ email, password })
      await refetch()
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Login failed'
      setError(message)
      throw err
    }
  }

  const signUp = async (email: string, name: string, password: string) => {
    try {
      setError(null)
      await registerMutation.mutateAsync({ email, name, password })
      await refetch()
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Registration failed'
      setError(message)
      throw err
    }
  }

  const signOut = async () => {
    try {
      await logoutMutation.mutateAsync()
      await refetch()
    } catch (err: any) {
      console.error('Logout error:', err)
    }
  }

  const refreshMe = () => {
    refetch()
  }

  const value: AuthContextType = {
    user: user || null,
    loading,
    error,
    signInEmail,
    signUp,
    signOut,
    refreshMe,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
