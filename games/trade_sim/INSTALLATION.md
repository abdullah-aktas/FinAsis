# 🎮 TradeSim 3D - Complete Installation Guide

## 📋 Overview

TradeSim 3D is a world-class multiplayer 3D trading game built with:
- **Frontend**: React + Three.js + Vite
- **Backend**: Django + Channels (WebSocket)
- **Database**: PostgreSQL
- **Cache**: Redis

---

## 🔧 Prerequisites

### Required Software
- **Python**: 3.10+ ([Download](https://www.python.org/downloads/))
- **Node.js**: 18+ ([Download](https://nodejs.org/))
- **PostgreSQL**: 14+ ([Download](https://www.postgresql.org/download/))
- **Redis**: 7+ ([Download](https://redis.io/download/))

### Optional Tools
- **Git**: Version control
- **VS Code**: Recommended IDE
- **Postman**: API testing

---

## 🚀 Backend Setup (Django)

### 1. Navigate to Project Root

```bash
cd FinAsis
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# Install Channels for WebSocket support
pip install channels channels-redis daphne
```

### 4. Configure Database

Create a PostgreSQL database:

```sql
CREATE DATABASE tradesim;
CREATE USER tradesim_user WITH PASSWORD 'your_password';
ALTER ROLE tradesim_user SET client_encoding TO 'utf8';
ALTER ROLE tradesim_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tradesim_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tradesim TO tradesim_user;
```

Update `FinAsis/config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradesim',
        'USER': 'tradesim_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Configure Redis

Start Redis server:

**Windows:**
```powershell
redis-server
```

**Linux/Mac:**
```bash
redis-server
```

Update `FinAsis/config/settings.py`:

```python
# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 6. Configure Django for Channels

Update `FinAsis/config/asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import WebSocket routing
from apps.games.trade_sim import routing as tradesim_routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            tradesim_routing.websocket_urlpatterns
        )
    ),
})
```

### 7. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

### 9. Initialize Game Data

```bash
python manage.py init_trade_sim
```

### 10. Start Django Development Server

**Option A: Using Daphne (Recommended for WebSocket)**
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

**Option B: Using Django runserver (for testing only)**
```bash
python manage.py runserver
```

✅ Backend should now be running at: `http://localhost:8000`

---

## 🎨 Frontend Setup (React + Three.js)

### 1. Navigate to Frontend Directory

```bash
cd FinAsis/src/apps/games/trade_sim/frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Create Environment File

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

### 4. Start Development Server

```bash
npm run dev
```

✅ Frontend should now be running at: `http://localhost:3000`

---

## 🧪 Testing the Installation

### 1. Test Backend API

```bash
# Test health endpoint
curl http://localhost:8000/api/health/

# Test guest onboarding
curl -X POST http://localhost:8000/api/games/trade-sim/guest-onboarding/

# Test cities endpoint
curl http://localhost:8000/api/games/trade-sim/cities/
```

### 2. Test WebSocket Connection

Open browser console and run:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/game/');
ws.onopen = () => console.log('✅ WebSocket connected');
ws.onmessage = (e) => console.log('📨 Message:', e.data);
```

### 3. Test Frontend

1. Open `http://localhost:3000` in browser
2. Click "Misafir Olarak Oyna"
3. Check browser console for logs
4. Verify 3D world loads

---

## 📦 Production Build

### Backend

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn + Daphne
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# In separate terminal, run Daphne for WebSocket
daphne -b 0.0.0.0 -p 8001 config.asgi:application
```

### Frontend

```bash
cd frontend
npm run build

# Serve with nginx or similar
# Build output will be in: frontend/dist/
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'channels'`
```bash
pip install channels channels-redis daphne
```

**Problem**: Redis connection error
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

**Problem**: Database connection error
```bash
# Verify PostgreSQL is running
psql -U tradesim_user -d tradesim -h localhost
```

### Frontend Issues

**Problem**: `Cannot find module '@react-three/fiber'`
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem**: WebSocket connection refused
- Check backend is running on port 8000
- Verify `VITE_WS_URL` in `.env` file
- Check firewall settings

**Problem**: Blank screen
- Open browser console for errors
- Check if backend API is accessible
- Verify API endpoints in Network tab

---

## 🔒 Security Considerations

### Production Settings

1. **Change SECRET_KEY** in `settings.py`
2. **Set DEBUG = False**
3. **Configure ALLOWED_HOSTS**
4. **Use HTTPS for WebSocket (wss://)**
5. **Set up CORS properly**
6. **Use environment variables for sensitive data**

---

## 📊 Performance Optimization

### Backend
- Use Gunicorn with multiple workers
- Enable database connection pooling
- Configure Redis caching
- Use CDN for static files

### Frontend
- Enable production build
- Use code splitting
- Optimize 3D models (GLTF/GLB)
- Implement lazy loading
- Use service worker for caching

---

## 📝 Next Steps

1. ✅ Install and run backend
2. ✅ Install and run frontend
3. 📝 Create test user account
4. 🎮 Play the game!
5. 🛠️ Customize and extend

---

## 🆘 Need Help?

- **Documentation**: See `README.md` and `DEVELOPMENT.md`
- **Issues**: [GitHub Issues](https://github.com/abdullah-aktas/FinAsis/issues)
- **Discord**: Join our community server

---

## 🎉 Success!

If you see the TradeSim 3D main menu and can move around in the 3D world, congratulations! 🎊

You've successfully installed the world's most advanced 3D trading game.

**Happy Trading! 💰🌍**
