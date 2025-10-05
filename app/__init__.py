"""
ReflexED Flask Application Factory.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
from app.models import init_db, db
from app.models.models import TokenBlacklist
from app.utils.decorators import limiter
import logging
from logging.handlers import RotatingFileHandler
import os


def create_app(config_name=None):
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def init_extensions(app):
    """Initialize Flask extensions."""
    
    # Database
    init_db(app)
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # JWT
    jwt = JWTManager(app)
    
    # JWT token blacklist loader
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED'):
        limiter.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    
    # Authentication routes
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Translation routes
    from app.api.translation import translation_bp
    app.register_blueprint(translation_bp)
    
    # Assignments routes
    from app.api.assignments import assignments_bp
    app.register_blueprint(assignments_bp)
    
    # Import send_from_directory for serving HTML files
    from flask import send_from_directory
    import os
    
    # Root route - serve index.html
    @app.route('/')
    def index():
        return send_from_directory(os.path.dirname(os.path.dirname(__file__)), 'index.html')
    
    # Serve uploaded files (audio, video, etc.)
    @app.route('/uploads/<path:filepath>')
    def serve_uploads(filepath):
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        return send_from_directory(upload_dir, filepath)
    
    # Serve static files (HTML, CSS, JS)
    @app.route('/<path:filename>')
    def serve_files(filename):
        # Get the directory where the app is located (parent of app/)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Check if file exists and has allowed extension
        if filename.endswith(('.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
            file_path = os.path.join(base_dir, filename)
            if os.path.exists(file_path):
                return send_from_directory(base_dir, filename)
        
        # If not a static file or doesn't exist, return 404
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'ReflexED API'
        }), 200
    
    # API root
    @app.route('/api')
    def api_root():
        return jsonify({
            'message': 'Welcome to ReflexED API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth/*',
                'translation': '/api/translation/*',
                'health': '/health',
                'documentation': 'See README.md for full API docs'
            }
        }), 200


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Too many requests', 'message': 'Rate limit exceeded'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {str(error)}')
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({'error': 'Service unavailable', 'message': 'Please try again later'}), 503


def setup_logging(app):
    """Setup application logging."""
    
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler
        file_handler = RotatingFileHandler(
            'logs/reflexed.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('ReflexED startup')
