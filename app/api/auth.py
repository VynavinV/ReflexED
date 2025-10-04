"""
Authentication API endpoints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import datetime, timedelta
from app.models import db
from app.models.models import User, TokenBlacklist
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    sanitize_input
)
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    POST /api/auth/register
    Body: {
        "email": "user@example.com",
        "username": "johndoe",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",  # optional: student, teacher
        "native_language": "en"  # optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        email = sanitize_input(data.get('email', ''), 120)
        username = sanitize_input(data.get('username', ''), 80)
        password = data.get('password', '')
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Validate username
        username_error = validate_username(username)
        if username_error:
            return jsonify({'error': username_error}), 400
        
        # Validate password
        password_error = validate_password(password)
        if password_error:
            return jsonify({'error': password_error}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 409
        
        # Create new user
        user = User(
            email=email,
            username=username,
            first_name=sanitize_input(data.get('first_name', ''), 50),
            last_name=sanitize_input(data.get('last_name', ''), 50),
            role=data.get('role', 'student'),
            native_language=data.get('native_language', 'en')
        )
        user.set_password(password)
        
        # Validate role
        if user.role not in ['student', 'teacher']:
            user.role = 'student'
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        logger.info(f"New user registered: {username} ({email})")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user.
    
    POST /api/auth/login
    Body: {
        "email": "user@example.com",  # or "username": "johndoe"
        "password": "SecurePass123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get credentials
        email = data.get('email')
        username = data.get('username')
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not email and not username:
            return jsonify({'error': 'Email or username is required'}), 400
        
        # Find user
        if email:
            user = User.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        logger.info(f"User logged in: {user.username}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token.
    
    POST /api/auth/refresh
    Headers: Authorization: Bearer <refresh_token>
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (blacklist current token).
    
    POST /api/auth/logout
    Headers: Authorization: Bearer <access_token>
    """
    try:
        jti = get_jwt()['jti']
        user_id = get_jwt_identity()
        token_type = get_jwt()['type']
        expires_at = datetime.fromtimestamp(get_jwt()['exp'])
        
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at
        )
        
        db.session.add(blacklisted_token)
        db.session.commit()
        
        logger.info(f"User logged out: {user_id}")
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user profile.
    
    GET /api/auth/me
    Headers: Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict(include_email=True)), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile.
    
    PUT /api/auth/me
    Headers: Authorization: Bearer <access_token>
    Body: {
        "first_name": "John",
        "last_name": "Doe",
        "native_language": "en",
        "learning_languages": ["es", "fr"]
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = sanitize_input(data['first_name'], 50)
        
        if 'last_name' in data:
            user.last_name = sanitize_input(data['last_name'], 50)
        
        if 'native_language' in data:
            user.native_language = data['native_language']
        
        if 'learning_languages' in data:
            if isinstance(data['learning_languages'], list):
                user.learning_languages = data['learning_languages']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Profile updated: {user.username}")
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(include_email=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    
    POST /api/auth/change-password
    Headers: Authorization: Bearer <access_token>
    Body: {
        "current_password": "OldPass123",
        "new_password": "NewPass456"
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        password_error = validate_password(new_password)
        if password_error:
            return jsonify({'error': password_error}), 400
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Password changed: {user.username}")
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500
