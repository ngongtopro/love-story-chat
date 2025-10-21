# Love Chat - Django Real-time Chat Application

A beautiful, real-time chat application built with Django, WebSockets (using Django Channels), and Tailwind CSS.

## Features

- 🚀 **Real-time messaging** with WebSocket support
- 💬 **Multiple chat rooms** - Create and join different conversations
- 🎨 **Beautiful UI** - Modern design with Tailwind CSS
- 🔐 **User authentication** - Secure login and registration
- 🐳 **Docker support** - Easy deployment with Docker Compose
- 📱 **Responsive design** - Works on all device sizes
- 🔄 **Message history** - Persistent message storage

## Tech Stack

- **Backend**: Django 4.2, Django Channels
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **WebSocket**: Django Channels with Redis
- **Database**: SQLite (can be easily changed to PostgreSQL)
- **Deployment**: Docker & Docker Compose

## Prerequisites

- Python 3.8+
- Redis server
- Docker & Docker Compose (for containerized deployment)

## Local Development Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd love_chat
```

### 2. Create virtual environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Redis server
Make sure Redis is running on your system:
```bash
# Using Redis server directly
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:alpine
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Collect static files
```bash
python manage.py collectstatic
```

### 8. Run the development server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Docker Deployment

### 🐳 Quick Start with Docker

**1. Start all services (MongoDB + Redis + Django):**
```bash
# Windows
docker_start.bat

# macOS/Linux
bash docker_start.sh
```

This will:
- Start MongoDB with persistent data storage
- Start Redis for WebSocket channels
- Build and run Django application
- Run database migrations
- Create admin user
- Show service status and logs

**2. Stop services:**
```bash
# Windows
docker_stop.bat

# macOS/Linux
bash docker_stop.sh
```

### Manual Docker Commands

**1. Build and run with Docker Compose:**
```bash
docker-compose up --build -d
```

**2. Run migrations:**
```bash
docker-compose exec web python manage.py migrate
```

**3. Create superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

**4. View logs:**
```bash
docker-compose logs -f web
```

**5. Access MongoDB shell:**
```bash
docker-compose exec mongodb mongosh -u admin -p admin123
```

**6. Access Redis CLI:**
```bash
docker-compose exec redis redis-cli
```

## Usage

1. **Register/Login**: Create a new account or login with existing credentials
2. **Browse Rooms**: View available chat rooms on the home page
3. **Create Room**: Click "Create Room" to start a new conversation
4. **Join Room**: Click "Join Room" to enter an existing chat room
5. **Chat**: Send real-time messages to other users in the room

## Project Structure

```
love_chat/
├── love_chat/              # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── asgi.py            # ASGI configuration for WebSockets
│   └── wsgi.py            # WSGI configuration
├── chat/                  # Chat application
│   ├── models.py          # Database models (Room, Message)
│   ├── views.py           # Django views
│   ├── consumers.py       # WebSocket consumers
│   ├── routing.py         # WebSocket routing
│   ├── urls.py            # URL patterns
│   └── admin.py           # Django admin configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── chat/              # Chat-specific templates
│   └── registration/      # Authentication templates
├── static/                # Static files
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── manage.py             # Django management script
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### Settings

Key settings in `settings.py`:

- `CHANNEL_LAYERS`: Redis configuration for WebSocket support
- `DATABASES`: Database configuration (SQLite by default)
- `STATIC_URL` & `STATIC_ROOT`: Static files configuration
- `CORS_ALLOWED_ORIGINS`: CORS settings for API access

## API Endpoints

- `/` - Home page with room list
- `/room/<room_name>/` - Chat room interface
- `/create-room/` - Create new room
- `/api/messages/<room_name>/` - Get room messages (JSON)
- `/login/` - User login
- `/register/` - User registration
- `/logout/` - User logout

## WebSocket Endpoints

- `ws/chat/<room_name>/` - WebSocket connection for real-time chat

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you have any questions or issues, please open an issue on GitHub or contact the maintainers.

## Screenshots

### Home Page
Beautiful landing page with room listings and authentication options.

### Chat Room
Real-time messaging interface with modern design and user-friendly features.

### Room Creation
Simple and intuitive room creation with validation and helpful tips.

---

Made with ❤️ using Django, Channels, and Tailwind CSS

daphne -b 0.0.0.0 -p 8001 love_chat.asgi:application