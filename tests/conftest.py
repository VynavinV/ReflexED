"""
Test configuration and fixtures.
"""
import pytest
from app import create_app
from app.models import db
from app.models.models import User


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create authenticated headers for testing."""
    # Register user
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'TestPass123',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'student'
    })
    
    data = response.get_json()
    token = data['access_token']
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            email='sample@example.com',
            username='sampleuser',
            first_name='Sample',
            last_name='User',
            role='student',
            native_language='en'
        )
        user.set_password('SamplePass123')
        
        db.session.add(user)
        db.session.commit()
        
        return user
