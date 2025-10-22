import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './layout'

// App Pages (with layout)
import HomePage from './page'
import ChatPage from './chat/page'
import ChatWithUserPage from './chat/[userId]/page'
import ProfilePage from './profile/page'
import CaroPage from './caro/page'
import FarmPage from './farm/page'
import WalletPage from './wallet/page'

// Auth Pages (without layout)
import LoginPage from './auth/login/page'
import RegisterPage from './auth/register/page'
import LandingPage from './LandingPage'

interface AppRoutesProps {
  isAuthenticated: boolean
}

export default function AppRoutes({ isAuthenticated }: AppRoutesProps) {
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/login" element={<Navigate to="/login" replace />} />
        <Route path="/auth/register" element={<Navigate to="/register" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    )
  }

  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:userId" element={<ChatWithUserPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/caro" element={<CaroPage />} />
        <Route path="/farm" element={<FarmPage />} />
        <Route path="/wallet" element={<WalletPage />} />
        
        {/* Redirect legacy auth routes */}
        <Route path="/auth/login" element={<Navigate to="/login" replace />} />
        <Route path="/auth/register" element={<Navigate to="/register" replace />} />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  )
}
