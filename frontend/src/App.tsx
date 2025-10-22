import { BrowserRouter as Router } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import AppRoutes from './app/routes'

function AppContent() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column'
      }}>
        <div style={{ fontSize: 18, color: '#1890ff' }}>Đang tải...</div>
      </div>
    )
  }

  return (
    <Router>
      <AppRoutes isAuthenticated={!!user} />
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
