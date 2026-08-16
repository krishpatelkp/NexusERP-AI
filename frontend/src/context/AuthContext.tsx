import React, { createContext, useContext, useEffect, useState } from 'react'
import { api, type UserProfile } from '../services/api'

interface AuthContextType {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  isAdmin: boolean
  isEmployee: boolean
  login: (email: string, pass: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [token, setToken] = useState<string | null>(api.getToken())
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    async function initAuth() {
      const storedToken = api.getToken()
      if (storedToken) {
        try {
          const me = await api.getMe()
          setUser(me)
          setToken(storedToken)
        } catch {
          // Token invalid or session expired
          api.clearToken()
          setUser(null)
          setToken(null)
        }
      } else {
        // Auto attempt demo login to make dev session smooth
        try {
          await api.autoLogin()
          const me = await api.getMe()
          setUser(me)
          setToken(api.getToken())
        } catch {
          setUser(null)
        }
      }
      setIsLoading(false)
    }
    initAuth()
  }, [])

  const refreshUser = async () => {
    try {
      const me = await api.getMe()
      setUser(me)
    } catch {
      setUser(null)
    }
  }

  const login = async (email: string, pass: string) => {
    setIsLoading(true)
    try {
      const res = await api.login(email, pass)
      setToken(api.getToken())
      const me = res.user || (await api.getMe())
      setUser(me)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await api.logout()
    } finally {
      setUser(null)
      setToken(null)
      setIsLoading(false)
    }
  }

  // Role checks
  const roleName = (user?.role_name || user?.role?.role_name || '').toLowerCase()
  const isSuperuser = !!user?.is_superuser
  const isAdmin = isSuperuser || roleName === 'admin' || roleName === 'hr' || roleName === 'owner' || !user?.role_name
  const isEmployee = !isAdmin && roleName === 'employee'

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        isAdmin,
        isEmployee,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
