import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data
          localStorage.setItem('access_token', access)

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/api/auth/token/', { username, password }),
  
  register: (userData) =>
    api.post('/api/auth/register/', userData),
  
  refreshToken: (refresh) =>
    api.post('/api/auth/token/refresh/', { refresh }),
  
  verifyToken: (token) =>
    api.post('/api/auth/token/verify/', { token }),
}

// Chat API
export const chatAPI = {
  getUsers: () => api.get('/users/'),
  getProfile: (userId: number | string) => api.get(`/profiles/${userId}/`),
  getPrivateChats: () => api.get('/chats/'),
  getMessages: (chatId: number | string) => api.get(`/chats/${chatId}/messages/`),
  sendMessage: (chatId: number | string, content: string) => 
    api.post(`/chats/${chatId}/send_message/`, { content }),
  createPrivateChat: (otherUserId: number) =>
    api.post('/chats/', { other_user_id: otherUserId }),
  getRooms: () => api.get('/rooms/'),
  getRoomMessages: (roomId: number | string) => api.get(`/rooms/${roomId}/messages/`),
}

// Caro Game API
export const caroAPI = {
  getGames: () => api.get('/api/caro/games/'),
  createGame: (gameData) => api.post('/api/caro/games/', gameData),
  joinGame: (gameId) => api.post(`/api/caro/games/${gameId}/join_game/`),
  makeMove: (gameId, row, col) => 
    api.post(`/api/caro/games/${gameId}/make_move/`, { row, col }),
  getWaitingGames: () => api.get('/api/caro/games/waiting_games/'),
  getActiveGames: () => api.get('/api/caro/games/active_games/'),
  getStats: () => api.get('/api/caro/games/stats/'),
}

// Farm API
export const farmAPI = {
  getFarm: () => api.get('/api/farm/farms/my_farm/'),
  getCrops: () => api.get('/api/farm/crops/'),
  plantCrop: (plotNumber, cropTypeId) =>
    api.post('/api/farm/farms/plant_crop/', { plot_number: plotNumber, crop_type_id: cropTypeId }),
  harvestPlot: (plotNumber) =>
    api.post('/api/farm/farms/harvest_plot/', { plot_number: plotNumber }),
  clearPlot: (plotNumber) =>
    api.post('/api/farm/farms/clear_plot/', { plot_number: plotNumber }),
  harvestAll: () => api.post('/api/farm/farms/harvest_all/'),
  getStats: () => api.get('/api/farm/farms/stats/'),
  getTransactions: () => api.get('/api/farm/transactions/'),
}

// Wallet API
export const walletAPI = {
  getWallet: () => api.get('/api/wallet/wallets/my_wallet/'),
  getTransactions: () => api.get('/api/wallet/transactions/'),
  addBalance: (amount, description) =>
    api.post('/api/wallet/wallets/add_balance/', { amount, description }),
  deductBalance: (amount, description) =>
    api.post('/api/wallet/wallets/deduct_balance/', { amount, description }),
  getStats: () => api.get('/api/wallet/wallets/stats/'),
}

export default api
