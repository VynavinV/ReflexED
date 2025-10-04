# PolyLearn Flask API - Quick Reference Card

## 🚀 Start Server
```bash
python run.py
# API: http://localhost:5000
```

## 🧪 Test API
```bash
python test_api.py
# Or import: PolyLearn_API.postman_collection.json
```

## 📡 Key Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login (get token) |
| GET | `/api/auth/me` | Get profile |
| POST | `/api/auth/logout` | Logout |

### Translation Coach
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/translation/analyze` | Get AI questions |
| POST | `/api/translation/submit` | Submit & evaluate |
| GET | `/api/translation/hints/<id>?level=1` | Get hints |
| GET | `/api/translation/progress` | Get progress |

## 🔑 Required Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 📝 Example Request
```bash
# 1. Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"Test123","role":"student"}'

# 2. Login (save token)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123"}'

# 3. Analyze Translation
curl -X POST http://localhost:5000/api/translation/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_text":"I went to the store","source_language":"en","target_language":"es","difficulty":"intermediate"}'
```

## 🐳 Docker Commands
```bash
docker-compose up -d     # Start
docker-compose logs -f   # View logs
docker-compose down      # Stop
```

## 🔧 Environment Setup
```bash
cp .env.example .env
# Edit .env:
# - Add GOOGLE_GEMINI_API_KEY
# - Generate SECRET_KEY and JWT_SECRET_KEY
```

## 📊 Database
```bash
# Create tables
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"

# Migrations (advanced)
flask db init
flask db migrate -m "message"
flask db upgrade
```

## 🧪 Testing
```bash
pytest                              # Run all tests
pytest --cov=app                    # With coverage
pytest tests/test_translation.py    # Specific file
pytest -v                           # Verbose
```

## 📁 Project Structure
```
app/
├── api/          # API endpoints
├── models/       # Database models
├── services/     # AI translation service
└── utils/        # Validators, decorators
```

## 🌍 Supported Languages
`es`, `fr`, `de`, `it`, `pt`, `zh`, `ja`, `ko`

## 🔒 Rate Limits
- Default: 200/day, 50/hour
- Translation: 30/hour
- Submit: 60/hour

## 📚 Documentation
- README.md - Overview
- INSTALLATION_GUIDE.md - Setup
- README_BACKEND.md - API details
- COMPLETION_SUMMARY.md - What was built

## 🆘 Troubleshooting
```bash
# Check server
curl http://localhost:5000/health

# View logs
tail -f logs/polylearn.log

# Check env variables
cat .env

# Reinstall dependencies
pip install -r requirements.txt
```

## 💡 Quick Tips
- Token expires in 1 hour (refresh with `/api/auth/refresh`)
- All POST requests need `Content-Type: application/json`
- Protected endpoints need `Authorization` header
- Use Postman collection for easy testing
- Check logs for debugging

---

**Get Started:**
```bash
./setup.sh && python run.py && python test_api.py
```
