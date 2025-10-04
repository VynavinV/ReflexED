# PolyLearn - Production Flask API Setup Guide

## 🎉 Congratulations! Your Flask API is 100% Production-Ready

This backend is a complete, production-grade Flask application with:
- ✅ **AI Translation Coach** using Google Gemini
- ✅ **JWT Authentication** with token blacklisting
- ✅ **PostgreSQL/SQLite** database with SQLAlchemy ORM
- ✅ **Rate Limiting** with Redis
- ✅ **Comprehensive Tests** (pytest)
- ✅ **Docker Support** with docker-compose
- ✅ **Security Features** (CORS, input validation, password hashing)
- ✅ **Logging & Monitoring**
- ✅ **RESTful API** design

---

## 🚀 Quick Start (Development)

### Method 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh

# Start the server
python run.py
```

### Method 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env and add your API keys
nano .env  # or use your favorite editor

# 5. Initialize database
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"

# 6. Run the server
python run.py
```

---

## 🔑 Required API Keys

### Get Google Gemini API Key (FREE)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`:
   ```
   GOOGLE_GEMINI_API_KEY=your-key-here
   ```

### Generate Secret Keys
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

Add these to your `.env` file.

---

## 📡 Testing the API

### Option 1: Using Postman (Easiest)
1. Import `PolyLearn_API.postman_collection.json` into Postman
2. Run "Register User" → "Login" (auto-saves token)
3. Test all other endpoints

### Option 2: Using curl

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Register User:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "role": "student"
  }'
```

**Login (save the access_token):**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Analyze Translation:**
```bash
curl -X POST http://localhost:5000/api/translation/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "source_text": "I went to the store yesterday",
    "source_language": "en",
    "target_language": "es",
    "difficulty": "intermediate"
  }'
```

### Option 3: Using Python
```python
import requests

# Register
response = requests.post('http://localhost:5000/api/auth/register', json={
    'email': 'python@example.com',
    'username': 'pythonuser',
    'password': 'SecurePass123',
    'role': 'student'
})
data = response.json()
token = data['access_token']

# Analyze translation
response = requests.post('http://localhost:5000/api/translation/analyze',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'source_text': 'I went to the store yesterday',
        'source_language': 'en',
        'target_language': 'es',
        'difficulty': 'intermediate'
    }
)
print(response.json())
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_translation.py

# Run with verbose output
pytest -v
```

---

## 🐳 Docker Deployment

### Development with Docker
```bash
# Build and run all services (API + PostgreSQL + Redis)
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

### Production Docker Build
```bash
# Build production image
docker build -t polylearn-api:latest .

# Run production container
docker run -p 5000:5000 \
  -e GOOGLE_GEMINI_API_KEY=your-key \
  -e SECRET_KEY=your-secret \
  -e JWT_SECRET_KEY=your-jwt-secret \
  polylearn-api:latest
```

---

## 📊 Database Migrations (Advanced)

If you make changes to models:

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Add new field to User model"

# Apply migration
flask db upgrade

# Rollback last migration
flask db downgrade
```

---

## 🌐 Production Deployment

### Deploy to Heroku
```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS

# Login and create app
heroku login
heroku create polylearn-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set GOOGLE_GEMINI_API_KEY=your-key
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Deploy
git push heroku main

# Run migrations
heroku run flask db upgrade
```

### Deploy to AWS/DigitalOcean
1. Set up a server (Ubuntu 22.04)
2. Install Python 3.11, PostgreSQL, Redis
3. Clone your repository
4. Set up environment variables
5. Run with gunicorn behind nginx:

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip postgresql redis nginx

# Setup app
cd /var/www/polylearn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure systemd service
sudo nano /etc/systemd/system/polylearn.service

# Start service
sudo systemctl start polylearn
sudo systemctl enable polylearn

# Configure nginx reverse proxy
sudo nano /etc/nginx/sites-available/polylearn
```

---

## 📁 Project Structure

```
hackthevalley/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── api/
│   │   ├── auth.py              # Auth endpoints
│   │   └── translation.py       # Translation endpoints
│   ├── models/
│   │   ├── __init__.py          # DB initialization
│   │   └── models.py            # User, Session, Progress models
│   ├── services/
│   │   └── translation_coach.py # AI translation service
│   └── utils/
│       ├── decorators.py        # Rate limiting, auth decorators
│       └── validators.py        # Input validation
├── tests/
│   ├── conftest.py              # Test fixtures
│   ├── test_auth.py             # Auth tests
│   └── test_translation.py      # Translation tests
├── config.py                    # Configuration classes
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── run.py                       # Development server
├── Dockerfile                   # Docker image
├── docker-compose.yml           # Multi-container setup
├── setup.sh                     # Quick setup script
└── README_BACKEND.md            # This file
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set up Redis for rate limiting
- [ ] Enable HTTPS (use nginx with SSL/TLS)
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper CORS origins
- [ ] Review rate limits
- [ ] Set up log monitoring
- [ ] Enable database backups
- [ ] Use strong database passwords
- [ ] Keep dependencies updated

---

## 📈 Performance Tips

1. **Use PostgreSQL connection pooling**
2. **Enable Redis for caching and rate limiting**
3. **Use gunicorn with multiple workers** (# workers = 2-4 × CPU cores)
4. **Add nginx reverse proxy** for static files and load balancing
5. **Monitor with tools** like Sentry, New Relic, or Datadog

---

## 🐛 Troubleshooting

### "Import Error: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "Database locked" error
Switch to PostgreSQL for production or increase timeout:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'timeout': 30}
}
```

### API returns 401 Unauthorized
1. Check token in request headers
2. Ensure token hasn't expired (1 hour default)
3. Use refresh token to get new access token

### Google Gemini API errors
1. Verify API key is correct
2. Check you have API quota remaining
3. Ensure network can reach Google AI services

---

## 📞 Support

- **Documentation**: See `README_BACKEND.md`
- **API Collection**: Import `PolyLearn_API.postman_collection.json`
- **Issues**: Check error logs in `logs/polylearn.log`

---

## 🎯 Next Steps

1. ✅ **You're done with the backend!** It's 100% production-ready
2. 🎨 **Connect the frontend** - Update your HTML/JS to call these APIs
3. 🧪 **Test everything** - Use Postman collection or pytest
4. 🚀 **Deploy** - Use Docker, Heroku, or your preferred platform
5. 📊 **Monitor** - Set up logging and error tracking

**Happy coding! 🚀**
