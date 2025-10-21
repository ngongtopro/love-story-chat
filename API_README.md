# Love Chat REST API

A comprehensive Django REST Framework API for a chat application with games, farming, and wallet features.

## Features

### 🚀 **Core API Features**
- **JWT Authentication** - Secure token-based authentication
- **Swagger Documentation** - Complete API documentation with interactive interface
- **Pagination** - Built-in pagination for large datasets
- **Filtering & Ordering** - Advanced filtering and sorting capabilities
- **Permissions** - Role-based access control

### 💬 **Chat API**
- **User Management** - User profiles and authentication
- **Private Chats** - One-on-one messaging
- **Room Chats** - Group chat functionality
- **Message History** - Complete message tracking
- **Real-time Features** - WebSocket support for live chat

### 🎮 **Caro Game API**
- **Game Management** - Create, join, and manage Caro games
- **Game Logic** - Complete game mechanics with move validation
- **Game Statistics** - Player stats and game history
- **Real-time Gameplay** - Live game updates

### 🌱 **Happy Farm API**
- **Farm Management** - Virtual farming simulation
- **Crop System** - Plant, grow, and harvest crops
- **Energy System** - Time-based energy regeneration
- **Experience & Levels** - Character progression system
- **Transaction History** - Complete farming activity log

### 💰 **Wallet API**
- **Balance Management** - User wallet system
- **Transaction History** - Complete transaction tracking
- **Admin Functions** - Balance adjustment capabilities

## API Documentation

### **Swagger UI**: http://localhost:8000/swagger/
- Interactive API documentation
- Test endpoints directly from browser
- Complete parameter descriptions

### **ReDoc**: http://localhost:8000/redoc/
- Alternative documentation interface
- Clean, readable format
- Detailed endpoint descriptions

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Get Access Token
```
POST /api/auth/token/
{
    "username": "your_username",
    "password": "your_password"
}
```

### Refresh Token
```
POST /api/auth/token/refresh/
{
    "refresh": "your_refresh_token"
}
```

### Use Token
Include in headers for authenticated requests:
```
Authorization: Bearer your_access_token
```

## Main API Endpoints

### 🔐 **Authentication**
- `POST /api/auth/token/` - Get access token
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/token/verify/` - Verify token

### 👥 **Chat API**
- `GET /api/chat/users/` - List users
- `GET /api/chat/profiles/` - User profiles
- `GET /api/chat/private-chats/` - Private conversations
- `GET /api/chat/messages/` - Chat messages
- `GET /api/chat/rooms/` - Chat rooms

### 🎯 **Caro Game API**
- `GET /api/caro/games/` - List games
- `POST /api/caro/games/` - Create new game
- `POST /api/caro/games/{id}/make_move/` - Make a move
- `POST /api/caro/games/{id}/join_game/` - Join game
- `GET /api/caro/games/waiting_games/` - Games waiting for players

### 🚜 **Farm API**
- `GET /api/farm/farms/my_farm/` - Get user's farm
- `GET /api/farm/crops/` - Available crops
- `POST /api/farm/farms/plant_crop/` - Plant a crop
- `POST /api/farm/farms/harvest_plot/` - Harvest crop
- `GET /api/farm/farms/stats/` - Farm statistics

### 💳 **Wallet API**
- `GET /api/wallet/wallets/my_wallet/` - Get user's wallet
- `GET /api/wallet/transactions/` - Transaction history
- `POST /api/wallet/wallets/add_balance/` - Add balance
- `GET /api/wallet/wallets/stats/` - Wallet statistics

## Installation & Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Migrations**
```bash
python manage.py migrate
```

3. **Create Superuser**
```bash
python manage.py createsuperuser
```

4. **Start Development Server**
```bash
python manage.py runserver
```

5. **Visit API Documentation**
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Key Dependencies

- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - REST API framework
- **drf-yasg 1.21.7** - Swagger/OpenAPI documentation
- **django-filter 23.3** - Advanced filtering
- **djangorestframework-simplejwt 5.3.0** - JWT authentication

## Project Structure

```
love_chat/
├── chat/                   # Chat application
│   ├── api_views.py       # Chat API views
│   ├── api_urls.py        # Chat API URLs
│   └── serializers.py     # Chat serializers
├── caro_game/             # Caro game application
│   ├── api_views.py       # Game API views
│   ├── api_urls.py        # Game API URLs
│   └── serializers.py     # Game serializers
├── happy_farm/            # Farm application
│   ├── api_views.py       # Farm API views
│   ├── api_urls.py        # Farm API URLs
│   └── serializers.py     # Farm serializers
├── user_wallet/           # Wallet application
│   ├── api_views.py       # Wallet API views
│   ├── api_urls.py        # Wallet API URLs
│   └── serializers.py     # Wallet serializers
└── love_chat/
    ├── settings.py        # Django settings with DRF config
    └── urls.py            # Main URL configuration
```

## Configuration Highlights

### REST Framework Settings
- **JWT Authentication** - Secure token-based auth
- **Pagination** - 20 items per page
- **Filtering** - DjangoFilterBackend support
- **Permissions** - IsAuthenticated by default

### Swagger Configuration
- **Complete Documentation** - All endpoints documented
- **Interactive Testing** - Test APIs directly
- **Authentication Support** - JWT token integration

This API provides a complete backend solution for a modern chat application with gaming and virtual economy features!
