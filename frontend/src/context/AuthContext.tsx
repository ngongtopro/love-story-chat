import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react'
import { message } from 'antd'
import { authAPI } from '../services/api'

interface User {
  id?: number
  username?: string
  email?: string
  authenticated: boolean
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>
  register: (userData: any) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        // Verify token is still valid
        await authAPI.verifyToken(token)
        // If valid, you might want to fetch user info here
        // For now, we'll just set a basic user object
        setUser({ authenticated: true })
      }
    } catch (error) {
      // Token is invalid, clear it
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login(username, password)
      const { access, refresh } = response.data

      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      setUser({ authenticated: true, username })
      message.success('Đăng nhập thành công!')
      
      return { success: true }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Đăng nhập thất bại'
      message.error(errorMessage)
      return { success: false, error: errorMessage }
    }
  }

  const register = async (userData: any) => {
    try {
      await authAPI.register(userData)
      message.success('Đăng ký thành công! Vui lòng đăng nhập.')
      return { success: true }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Đăng ký thất bại'
      message.error(errorMessage)
      return { success: false, error: errorMessage }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    message.success('Đã đăng xuất!')
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
