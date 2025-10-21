# Frontend cho Love Chat

Frontend hiện đại được xây dựng với **Vite + React + Ant Design 5.0** để kết nối với Django REST API.

## ✨ Tính năng

### 🎨 **Giao diện hiện đại**
- **Ant Design 5.0** - Components đẹp và chuyên nghiệp
- **Responsive Design** - Hoạt động tốt trên mọi thiết bị
- **Theme tùy chỉnh** - Màu sắc Love Chat (#ff69b4)
- **Vietnamese locale** - Giao diện tiếng Việt

### 🔐 **Xác thực**
- **JWT Authentication** - Bảo mật với token
- **Auto refresh token** - Tự động làm mới token
- **Login/Register** - Đăng nhập và đăng ký đẹp mắt

### 💬 **Chat**
- **Real-time messaging** - Tin nhắn thời gian thực
- **Private chats** - Trò chuyện riêng tư
- **Online status** - Hiển thị trạng thái online
- **Message history** - Lịch sử tin nhắn

### 🎮 **Game Caro**
- **Game board** - Bàn cờ Caro tương tác
- **Real-time gameplay** - Chơi game thời gian thực
- **Game stats** - Thống kê game
- **Game history** - Lịch sử các trận đấu

### 🌱 **Farm**
- **Virtual farming** - Trang trại ảo
- **Crop management** - Quản lý cây trồng
- **Harvest system** - Hệ thống thu hoạch
- **Farm stats** - Thống kê trang trại

### 💰 **Wallet**
- **Balance management** - Quản lý số dư
- **Transaction history** - Lịch sử giao dịch
- **Add/Withdraw** - Nạp/Rút tiền

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
cd frontend
npm install
```

### 2. Cấu hình environment

File `.env` đã được tạo với cấu hình mặc định:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Chạy development server

```bash
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

### 4. Build production

```bash
npm run build
```

## 📁 Cấu trúc project

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/        # Shared components
│   │   ├── Navbar.jsx    # Top navigation
│   │   └── Sidebar.jsx   # Side navigation
│   ├── context/          # React contexts
│   │   └── AuthContext.jsx # Authentication context
│   ├── pages/            # Main pages
│   │   ├── Login.jsx     # Login page
│   │   ├── Register.jsx  # Register page
│   │   ├── Home.jsx      # Dashboard
│   │   ├── Chat.jsx      # Chat page
│   │   ├── Profile.jsx   # User profile
│   │   ├── CaroGame.jsx  # Caro game page
│   │   ├── Farm.jsx      # Farm page
│   │   └── Wallet.jsx    # Wallet page
│   ├── services/         # API services
│   │   └── api.js        # API client
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── package.json
├── vite.config.js
└── .env
```

## 🛠 Công nghệ sử dụng

### **Core**
- **Vite** - Build tool nhanh và hiện đại
- **React 18** - Library UI phổ biến
- **React Router 6** - Routing cho SPA

### **UI Framework**
- **Ant Design 5.0** - Component library chuyên nghiệp
- **@ant-design/icons** - Icon set đầy đủ
- **CSS Grid/Flexbox** - Layout hiện đại

### **API & State**
- **Axios** - HTTP client
- **React Context** - State management
- **Local Storage** - Token persistence

### **Utilities**
- **Day.js** - Date manipulation
- **Vietnamese locale** - Hỗ trợ tiếng Việt

## 🎨 Thiết kế

### **Color Scheme**
- **Primary**: #ff69b4 (Hot Pink)
- **Secondary**: #ff1493 (Deep Pink)
- **Success**: #52c41a
- **Warning**: #faad14
- **Error**: #ff4d4f

### **Components**
- **Cards** - Hiển thị thông tin
- **Lists** - Danh sách dữ liệu
- **Forms** - Input và validation
- **Modals** - Dialog boxes
- **Tables** - Bảng dữ liệu
- **Statistics** - Thống kê

### **Responsive**
- **Mobile First** - Thiết kế ưu tiên mobile
- **Breakpoints** - xs, sm, md, lg, xl
- **Grid System** - 24 columns

## 🔗 API Integration

### **Authentication**
```javascript
// Login
POST /api/auth/token/
{
  "username": "user",
  "password": "pass"
}

// Auto refresh token
POST /api/auth/token/refresh/
{
  "refresh": "refresh_token"
}
```

### **Chat**
```javascript
// Get users
GET /api/chat/users/

// Send message
POST /api/chat/private-chats/{id}/send_message/
{
  "content": "Hello!"
}
```

### **Game**
```javascript
// Create game
POST /api/caro/games/
{
  "board_size": 15
}

// Make move
POST /api/caro/games/{id}/make_move/
{
  "row": 7,
  "col": 7
}
```

## 📱 Features

### **Dashboard**
- **Quick stats** - Thống kê nhanh
- **Recent activity** - Hoạt động gần đây
- **Online users** - Người dùng online
- **Quick actions** - Hành động nhanh

### **Chat Interface**
- **User list** - Danh sách người dùng
- **Chat window** - Cửa sổ chat
- **Message bubbles** - Bong bóng tin nhắn
- **Typing indicators** - Đang gõ...

### **Game Interface**
- **Game board** - Bàn cờ tương tác
- **Game controls** - Điều khiển game
- **Game status** - Trạng thái game
- **Player info** - Thông tin người chơi

### **Farm Interface**
- **Farm grid** - Lưới trang trại
- **Crop selection** - Chọn cây trồng
- **Harvest actions** - Hành động thu hoạch
- **Farm stats** - Thống kê trang trại

## 🎯 Scripts

```bash
# Development
npm run dev          # Start dev server

# Build
npm run build        # Build for production
npm run preview      # Preview production build

# Lint
npm run lint         # Check code quality
```

## 🌟 Highlights

### **Performance**
- **Vite HMR** - Hot Module Replacement
- **Code splitting** - Tách code tự động
- **Tree shaking** - Loại bỏ code không dùng
- **Optimized builds** - Build tối ưu

### **Developer Experience**
- **TypeScript support** - Hỗ trợ TypeScript
- **ESLint** - Code quality
- **Hot reload** - Reload nhanh
- **Error overlay** - Hiển thị lỗi

### **User Experience**
- **Loading states** - Trạng thái loading
- **Error handling** - Xử lý lỗi
- **Success feedback** - Phản hồi thành công
- **Responsive design** - Thiết kế responsive

Frontend Love Chat đã sẵn sàng để kết nối với Django REST API và cung cấp trải nghiệm người dùng tuyệt vời! 🎉
