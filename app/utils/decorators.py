"""
Custom decorators for Flask routes.
"""
from functools import wraps
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def rate_limit(limit_string):
    """
    Rate limiting decorator for API endpoints.
    
    Usage:
        @rate_limit('30 per hour')
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This will be handled by flask-limiter
            return f(*args, **kwargs)
        
        # Apply rate limit
        return limiter.limit(limit_string)(decorated_function)
    
    return decorator


def validate_json(f):
    """
    Validate that request contains JSON data.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Require admin role for route access.
    Must be used after @jwt_required()
    """
    from flask_jwt_extended import get_jwt_identity
    from app.models.models import User
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """
    Require teacher or admin role for route access.
    Must be used after @jwt_required()
    """
    from flask_jwt_extended import get_jwt_identity
    from app.models.models import User
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Teacher access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
