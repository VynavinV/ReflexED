# ReflexED Backend Documentation

## 🚀 Production-Ready Flask Backend

A comprehensive Flask API for the PolyLearn platform, featuring an AI-powered translation coach that teaches languages through guided questions instead of direct translations.

## 📋 Features

### ✅ Translation Coach System
- **AI-Guided Learning**: Uses Google Gemini to ask questions about tense, vocabulary, and grammar
- **Smart Evaluation**: Detailed scoring on accuracy, grammar, and vocabulary
- **Progressive Hints**: Multi-level hint system (subtle → direct)
- **Practice Generator**: AI-generated practice sentences for any language/difficulty
- **Progress Tracking**: Comprehensive learning analytics and streaks

### ✅ Production-Ready Architecture
- **Database**: SQLAlchemy with PostgreSQL support (SQLite for dev)
- **Authentication**: JWT-based auth with token blacklisting
- **Security**: CORS, rate limiting, input validation, password hashing
- **Logging**: Rotating file logs with configurable levels
- **Error Handling**: Comprehensive error handlers with proper HTTP codes
- **Testing Ready**: Separate test configuration and database

### ✅ API Endpoints

#### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - Login user
- `POST /refresh` - Refresh access token
- `POST /logout` - Logout (blacklist token)
- `GET /me` - Get current user profile
- `PUT /me` - Update profile
- `POST /change-password` - Change password

#### Translation (`/api/translation`)
- `POST /analyze` - Get AI questions for translation
- `POST /submit` - Submit translation and get evaluation
- `GET /hints/<session_id>` - Get progressive hints
- `GET /practice` - Get practice sentence
- `GET /progress` - Get learning progress
- `GET /history` - Get translation history

## 🛠️ Installation

### 1. Clone and Setup

```bash
cd /Users/vynavin/Documents/Projects/hackthevalley

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required environment variables:**
- `GOOGLE_GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `SECRET_KEY` - Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY` - Generate with `python -c "import secrets; print(secrets.token_hex(32))"`

### 3. Initialize Database

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 4. Run Development Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## 📚 API Usage Examples

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student1",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "native_language": "en"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123"
  }'
```

### Analyze Translation (requires auth)
```bash
curl -X POST http://localhost:5000/api/translation/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "source_text": "I went to the store yesterday",
    "source_language": "en",
    "target_language": "es",
    "difficulty": "intermediate"
  }'
```

### Submit Translation
```bash
curl -X POST http://localhost:5000/api/translation/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "session_id": "SESSION_UUID",
    "user_translation": "Fui a la tienda ayer",
    "time_spent_seconds": 120,
    "hints_requested": 1
  }'
```

## 🏗️ Project Structure

```
hackthevalley/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── api/
│   │   ├── auth.py           # Authentication endpoints
│   │   └── translation.py    # Translation endpoints
│   ├── models/
│   │   ├── __init__.py       # Database initialization
│   │   └── models.py         # User, TranslationSession, UserProgress
│   ├── services/
│   │   └── translation_coach.py  # AI translation coach service
│   └── utils/
│       ├── decorators.py     # Custom decorators (rate_limit, etc.)
│       └── validators.py     # Input validation
├── tests/                    # Unit and integration tests
├── static/                   # Static files (CSS, JS, images)
├── templates/                # HTML templates
├── config.py                 # Configuration classes
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── run.py                    # Application entry point
└── README_BACKEND.md         # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_translation.py
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Using Docker

```bash
# Build image
docker build -t polylearn-api .

# Run container
docker run -p 5000:5000 --env-file .env polylearn-api
```

### Environment Variables for Production

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/polylearn
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
GOOGLE_GEMINI_API_KEY=<your-api-key>
CORS_ORIGINS=https://yourdomain.com
```

## 📊 Database Models

### User
- Authentication and profile management
- Roles: student, teacher, admin
- Learning language preferences
- Account status tracking

### TranslationSession
- Individual translation practice attempts
- AI questions and hints
- Scoring: accuracy, grammar, vocabulary
- Time tracking and completion status

### UserProgress
- Aggregate learning metrics per language
- Skill levels (grammar, vocabulary, overall)
- Learning streaks
- Mastered concepts tracking

## 🔐 Security Features

- ✅ JWT token authentication with blacklisting
- ✅ Password hashing with bcrypt
- ✅ Rate limiting (configurable per endpoint)
- ✅ Input validation and sanitization
- ✅ CORS protection
- ✅ Secure session cookies
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection

## 📈 Rate Limits

- Default: 200 requests/day, 50 requests/hour
- Translation analysis: 30 requests/hour
- Translation submission: 60 requests/hour

## 🌍 Supported Languages

- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

## 📝 License

MIT License - Feel free to use for educational purposes

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

## 📧 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ for Hack the Valley 9**
