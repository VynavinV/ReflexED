#!/bin/bash

# Quick start script for PolyLearn Flask API

echo "🚀 PolyLearn Flask API - Quick Start"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  IMPORTANT: Edit .env and add your GOOGLE_GEMINI_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if database exists
if [ ! -f "polylearn.db" ]; then
    echo "🗄️  Setting up database..."
    python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database created')"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To start the development server:"
echo "   python run.py"
echo ""
echo "📚 API will be available at: http://localhost:5000"
echo "📖 API docs at: http://localhost:5000/api"
echo ""
echo "🧪 To run tests:"
echo "   pytest"
echo ""
echo "🐳 To run with Docker:"
echo "   docker-compose up"
echo ""
