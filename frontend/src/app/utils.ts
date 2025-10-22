/**
 * Route utilities for the app
 */

export const APP_ROUTES = {
  // Public routes
  LANDING: '/',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  
  // App routes (authenticated)
  HOME: '/',
  CHAT: '/chat',
  CHAT_WITH_USER: (userId: string | number) => `/chat/${userId}`,
  PROFILE: '/profile',
  CARO: '/caro',
  FARM: '/farm',
  WALLET: '/wallet',
} as const

export type AppRoute = typeof APP_ROUTES[keyof typeof APP_ROUTES]

/**
 * Check if route requires authentication
 */
export function requiresAuth(pathname: string): boolean {
  const publicRoutes = ['/', '/auth/login', '/auth/register', '/landing']
  
  // If user is on a public route and not authenticated, don't require auth
  if (publicRoutes.includes(pathname)) {
    return false
  }
  
  // All other routes require authentication
  return true
}

/**
 * Check if route should show layout
 */
export function shouldShowLayout(pathname: string, isAuthenticated: boolean): boolean {
  const authRoutes = ['/auth/login', '/auth/register']
  const landingRoutes = ['/', '/landing']
  
  // Don't show layout for auth routes
  if (authRoutes.includes(pathname)) {
    return false
  }
  
  // Don't show layout for landing if not authenticated
  if (landingRoutes.includes(pathname) && !isAuthenticated) {
    return false
  }
  
  // Show layout for all other authenticated routes
  return isAuthenticated
}

/**
 * Get page title based on route
 */
export function getPageTitle(pathname: string): string {
  const titles: Record<string, string> = {
    '/': 'Trang chủ',
    '/chat': 'Trò chuyện',
    '/profile': 'Hồ sơ',
    '/caro': 'Game Caro',
    '/farm': 'Trang trại',
    '/wallet': 'Ví tiền',
    '/auth/login': 'Đăng nhập',
    '/auth/register': 'Đăng ký',
  }
  
  // Handle dynamic routes
  if (pathname.startsWith('/chat/')) {
    return 'Trò chuyện'
  }
  
  return titles[pathname] || 'Love Chat'
}
