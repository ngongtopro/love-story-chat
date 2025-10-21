import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Profile from './pages/Profile'
import CaroGame from './pages/CaroGame'
import Farm from './pages/Farm'
import Wallet from './pages/Wallet'
import { AuthProvider, useAuth } from './context/AuthContext'

const { Content } = Layout

function AppContent() {
  const { user, loading } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Đang tải...</div>
      </div>
    )
  }

  if (!user) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    )
  }

  return (
    <Router>
      <Layout className="full-height">
        <Navbar collapsed={collapsed} setCollapsed={setCollapsed} />
        <Layout>
          <Sidebar collapsed={collapsed} />
          <Layout style={{ marginLeft: collapsed ? 80 : 200 }}>
            <Content style={{ margin: '16px', overflow: 'auto' }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/chat/:userId?" element={<Chat />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/caro" element={<CaroGame />} />
                <Route path="/farm" element={<Farm />} />
                <Route path="/wallet" element={<Wallet />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
