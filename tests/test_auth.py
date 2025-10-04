"""
Tests for authentication API endpoints.
"""
import pytest


def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'NewPass123',
        'first_name': 'New',
        'last_name': 'User',
        'role': 'student'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert 'user' in data
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'newuser'


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # First registration
    client.post('/api/auth/register', json={
        'email': 'duplicate@example.com',
        'username': 'user1',
        'password': 'Pass123'
    })
    
    # Second registration with same email
    response = client.post('/api/auth/register', json={
        'email': 'duplicate@example.com',
        'username': 'user2',
        'password': 'Pass123'
    })
    
    assert response.status_code == 409
    data = response.get_json()
    assert 'error' in data


def test_register_invalid_email(client):
    """Test registration with invalid email."""
    response = client.post('/api/auth/register', json={
        'email': 'notanemail',
        'username': 'testuser',
        'password': 'Pass123'
    })
    
    assert response.status_code == 400


def test_register_weak_password(client):
    """Test registration with weak password."""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'weak'
    })
    
    assert response.status_code == 400


def test_login_success(client, sample_user):
    """Test successful login."""
    response = client.post('/api/auth/login', json={
        'email': 'sample@example.com',
        'password': 'SamplePass123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data


def test_login_wrong_password(client, sample_user):
    """Test login with wrong password."""
    response = client.post('/api/auth/login', json={
        'email': 'sample@example.com',
        'password': 'WrongPass123'
    })
    
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post('/api/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'Pass123'
    })
    
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test getting current user profile."""
    response = client.get('/api/auth/me', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'username' in data
    assert 'email' in data


def test_update_profile(client, auth_headers):
    """Test updating user profile."""
    response = client.put(
        '/api/auth/me',
        headers=auth_headers,
        json={
            'first_name': 'Updated',
            'last_name': 'Name',
            'learning_languages': ['es', 'fr']
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['user']['first_name'] == 'Updated'
    assert 'es' in data['user']['learning_languages']


def test_change_password_success(client, auth_headers):
    """Test successful password change."""
    response = client.post(
        '/api/auth/change-password',
        headers=auth_headers,
        json={
            'current_password': 'TestPass123',
            'new_password': 'NewPass456'
        }
    )
    
    assert response.status_code == 200


def test_change_password_wrong_current(client, auth_headers):
    """Test password change with wrong current password."""
    response = client.post(
        '/api/auth/change-password',
        headers=auth_headers,
        json={
            'current_password': 'WrongPass123',
            'new_password': 'NewPass456'
        }
    )
    
    assert response.status_code == 401


def test_logout(client, auth_headers):
    """Test user logout."""
    response = client.post('/api/auth/logout', headers=auth_headers)
    
    assert response.status_code == 200
    
    # Verify token is blacklisted by trying to use it again
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 401
