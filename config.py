"""
Configuration management for ReflexED Flask application.
Supports multiple environments: development, testing, production.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration with common settings."""
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    APP_NAME = 'ReflexED'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///reflexed.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # AI Services
    GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    
    # Translation Service Settings
    TRANSLATION_MODEL = 'gemini-1.5-pro'
    TRANSLATION_TIMEOUT = 30  # seconds
    MAX_TRANSLATION_LENGTH = 500  # characters
    SUPPORTED_LANGUAGES = ['es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko']
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_TRANSLATION = "30 per hour"
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'pptx'}
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    
    # More verbose logging
    LOG_LEVEL = 'DEBUG'
    
    # Disable rate limiting in dev
    RATELIMIT_ENABLED = False


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    # Disable CSRF for API testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    
    # Enforce strong secret keys in production
    def __init__(self):
        super().__init__()
        if self.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("Must set SECRET_KEY environment variable in production")
        if self.JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
            raise ValueError("Must set JWT_SECRET_KEY environment variable in production")
        if not self.GOOGLE_GEMINI_API_KEY:
            raise ValueError("Must set GOOGLE_GEMINI_API_KEY environment variable")
    
    # Stricter security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production database should be PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Production rate limiting with Redis
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
