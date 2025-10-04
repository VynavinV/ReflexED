"""
Validation utilities for API requests.
"""
from typing import Dict, Optional
from config import Config


def validate_translation_request(data: Dict) -> Optional[str]:
    """
    Validate translation request data.
    
    Returns:
        Error message if validation fails, None otherwise
    """
    required_fields = ['source_text', 'source_language', 'target_language']
    
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
    
    # Validate source text
    source_text = data.get('source_text', '').strip()
    if not source_text:
        return "source_text cannot be empty"
    
    if len(source_text) > Config.MAX_TRANSLATION_LENGTH:
        return f"source_text exceeds maximum length of {Config.MAX_TRANSLATION_LENGTH} characters"
    
    # Validate language codes
    source_lang = data.get('source_language')
    target_lang = data.get('target_language')
    
    if not validate_language_code(source_lang):
        return f"Invalid source_language code: {source_lang}"
    
    if not validate_language_code(target_lang):
        return f"Invalid target_language code: {target_lang}"
    
    if source_lang == target_lang:
        return "source_language and target_language cannot be the same"
    
    # Validate difficulty if provided
    difficulty = data.get('difficulty')
    if difficulty and difficulty not in ['beginner', 'intermediate', 'advanced']:
        return "difficulty must be 'beginner', 'intermediate', or 'advanced'"
    
    return None


def validate_language_code(code: str) -> bool:
    """
    Validate language code.
    
    Args:
        code: Language code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False
    
    valid_codes = Config.SUPPORTED_LANGUAGES + ['en']
    return code.lower() in valid_codes


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Optional[str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Error message if validation fails, None otherwise
    """
    if not password:
        return "Password is required"
    
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return "Password must be less than 128 characters"
    
    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit"
    
    # Check for at least one letter
    if not any(char.isalpha() for char in password):
        return "Password must contain at least one letter"
    
    return None


def validate_username(username: str) -> Optional[str]:
    """
    Validate username.
    
    Args:
        username: Username to validate
        
    Returns:
        Error message if validation fails, None otherwise
    """
    if not username:
        return "Username is required"
    
    if len(username) < 3:
        return "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return "Username must be less than 30 characters"
    
    # Only alphanumeric and underscores
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return "Username can only contain letters, numbers, and underscores"
    
    return None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    # Enforce max length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text
