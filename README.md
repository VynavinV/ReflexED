# PolyLearn - AI-Powered Translation Coach Platform

PolyLearn is a **production-ready** virtual learning environment featuring an AI Translation Coach that teaches foreign languages through guided questions instead of direct translations. Designed for students with diverse learning needs, including those with ADHD, dyslexia, and non-native speakers.

## 🎯 Project Status: 100% Production-Ready Backend ✅

✅ **Complete Flask API** with AI Translation Coach  
✅ **Full Authentication System** (JWT + token blacklisting)  
✅ **Production Database** (PostgreSQL + SQLite)  
✅ **Docker Support** (docker-compose ready)  
✅ **Comprehensive Tests** (pytest with fixtures)  
✅ **Security Features** (CORS, rate limiting, validation)  
✅ **Complete Documentation** (API docs + Postman collection)

---

## 🚀 Quick Start

### Backend API (Translation System)

```bash
# 1. Quick setup
./setup.sh

# 2. Add your Google Gemini API key to .env
# Get free key: https://makersuite.google.com/app/apikey

# 3. Start the server
python run.py

# 4. Test the API
python test_api.py
```

**API will be running at:** `http://localhost:5000`

### Frontend (Current Static Site)

```bash
# Open in browser
open index.html

# Or serve with Python
python -m http.server 8000
```

**Frontend will be at:** `http://localhost:8000`

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** | Complete setup and deployment guide |
| **[README_BACKEND.md](README_BACKEND.md)** | Backend architecture and API docs |
| **[PolyLearn_API.postman_collection.json](PolyLearn_API.postman_collection.json)** | Import into Postman for testing |

---

## 🏗️ Architecture

### Backend (Flask API)
```
app/
├── api/
│   ├── auth.py           # JWT authentication endpoints
│   └── translation.py    # AI translation coach endpoints
├── models/
│   └── models.py         # User, TranslationSession, UserProgress
├── services/
│   └── translation_coach.py  # Google Gemini AI service
└── utils/
    ├── validators.py     # Input validation
    └── decorators.py     # Rate limiting, auth
```

### Frontend (HTML/CSS/JS)
```
index.html              # Landing page
student.html           # Student portal with AI lessons
teacher.html           # Teacher dashboard
district.html          # District analytics
accessibility.html     # Accessibility settings
about.html            # About page
styles.css            # Complete styling
script.js             # Interactive functionality
```

---

## 🎓 How the AI Translation Coach Works

**Traditional Approach (Google Translate):**
- Input: "I went to the store"
- Output: "Fui a la tienda" ✅ (Done!)

**PolyLearn AI Coach:**
- Input: "I went to the store"
- AI Asks:
  1. 🤔 "What tense should 'went' be? Preterite or imperfect?"
  2. 🤔 "Is 'ir' a regular or irregular verb in Spanish?"
  3. 🤔 "Which word for 'store' fits better: tienda or almacén?"
  4. 🤔 "Where does 'ayer' typically go in the sentence?"
- Student thinks critically → learns grammar rules → builds real understanding ✅

---

## 🔥 Key Features

### ✅ AI Translation Coach
- **Guided Questions**: AI asks about tense, vocabulary, grammar instead of giving answers
- **Smart Evaluation**: Detailed feedback on accuracy, grammar, vocabulary
- **Progressive Hints**: 3-level hint system (subtle → moderate → direct)
- **Practice Generator**: AI creates custom sentences for any language/difficulty
- **Progress Tracking**: Learning streaks, mastered concepts, skill levels

### ✅ Complete Authentication
- User registration with role-based access (student/teacher/admin)
- JWT authentication with access + refresh tokens
- Token blacklisting for secure logout
- Password change and profile management

### ✅ Production Security
- CORS protection
- Rate limiting (30 requests/hour for translation)
- Input validation and sanitization
- Password hashing with bcrypt
- SQL injection protection (SQLAlchemy ORM)

### ✅ Frontend Features
- Responsive design (mobile/tablet/desktop)
- Dark mode + High contrast themes
- Accessibility settings (font size, reading speed)
- Interactive lesson modals
- District analytics dashboard

---

## 🌍 Supported Languages

- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update profile
- `POST /api/auth/logout` - Logout

### Translation Coach
- `POST /api/translation/analyze` - Get AI questions for translation
- `POST /api/translation/submit` - Submit translation & get evaluation
- `GET /api/translation/hints/<id>` - Get progressive hints
- `GET /api/translation/practice` - Get practice sentence
- `GET /api/translation/progress` - Get learning progress
- `GET /api/translation/history` - Get translation history

---

## 🧪 Testing

```bash
# Run backend tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Test API manually
python test_api.py

# Import Postman collection
# File: PolyLearn_API.postman_collection.json
```

---

## 🐳 Docker Deployment

```bash
# Start all services (API + PostgreSQL + Redis)
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLAlchemy (PostgreSQL/SQLite)
- **Authentication**: Flask-JWT-Extended
- **AI**: Google Gemini API
- **Rate Limiting**: Flask-Limiter + Redis
- **Testing**: pytest
- **Deployment**: Gunicorn + Docker

### Frontend
- **HTML5** + **CSS3** (CSS Variables for theming)
- **Vanilla JavaScript** (no frameworks)
- **Google Fonts** (Inter)
- **Responsive Design** (Grid + Flexbox)
- **WCAG 2.1 AA** compliant

---

## 📦 Installation Requirements

```bash
# Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt

# Optional: PostgreSQL (for production)
brew install postgresql  # macOS

# Optional: Redis (for rate limiting)
brew install redis  # macOS
```

---

## 🔐 Environment Variables

Required for production (see `.env.example`):

```bash
GOOGLE_GEMINI_API_KEY=your-key-here  # Required for AI
SECRET_KEY=random-secret-key          # Required for Flask
JWT_SECRET_KEY=random-jwt-secret      # Required for auth
DATABASE_URL=postgresql://...         # Optional (SQLite default)
REDIS_URL=redis://localhost:6379/0   # Optional (memory default)
```

---

## 🎨 Connecting Frontend to Backend

Update `script.js` to call the Flask API:

```javascript
// Example: Analyze translation
async function analyzeTranslation(text, sourceLang, targetLang) {
  const response = await fetch('http://localhost:5000/api/translation/analyze', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      source_text: text,
      source_language: sourceLang,
      target_language: targetLang,
      difficulty: 'intermediate'
    })
  });
  return await response.json();
}
```

---

## 🚀 Deployment Options

### Heroku (Easiest)
```bash
heroku create polylearn-api
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Docker (Recommended)
```bash
docker-compose up -d
```

### VPS (DigitalOcean/AWS)
```bash
# Use Gunicorn + nginx
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## 📈 Future Enhancements

- [ ] Audio narration with ElevenLabs API
- [ ] Teacher material upload endpoint
- [ ] Manim video generation for math/science
- [ ] WebSocket for real-time AI interactions
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics dashboard

---

## 🤝 Contributing

This is a hackathon project built for **Hack the Valley 9**. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - Feel free to use for educational purposes

---

## 👥 Team

Built with ❤️ by the PolyLearn team for accessible education

---

## 🆘 Support

- **Setup Issues**: See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- **API Questions**: Import [Postman collection](PolyLearn_API.postman_collection.json)
- **Backend Docs**: See [README_BACKEND.md](README_BACKEND.md)
- **Bugs**: Check logs in `logs/polylearn.log`

---

**🎉 The backend is 100% production-ready! Start the server and test it out!**

```bash
./setup.sh && python run.py
```
