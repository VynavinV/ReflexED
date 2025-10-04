"""
Tests for translation API endpoints.
"""
import pytest
import json


def test_analyze_translation_success(client, auth_headers):
    """Test successful translation analysis."""
    response = client.post(
        '/api/translation/analyze',
        headers=auth_headers,
        json={
            'source_text': 'I went to the store yesterday',
            'source_language': 'en',
            'target_language': 'es',
            'difficulty': 'intermediate'
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'session_id' in data
    assert 'questions' in data
    assert 'grammar_concepts' in data
    assert 'vocabulary_focus' in data
    assert len(data['questions']) > 0


def test_analyze_translation_missing_fields(client, auth_headers):
    """Test translation analysis with missing required fields."""
    response = client.post(
        '/api/translation/analyze',
        headers=auth_headers,
        json={
            'source_text': 'Hello'
        }
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_analyze_translation_invalid_language(client, auth_headers):
    """Test translation analysis with invalid language code."""
    response = client.post(
        '/api/translation/analyze',
        headers=auth_headers,
        json={
            'source_text': 'Hello',
            'source_language': 'en',
            'target_language': 'invalid',
            'difficulty': 'beginner'
        }
    )
    
    assert response.status_code == 400


def test_analyze_translation_unauthorized(client):
    """Test translation analysis without authentication."""
    response = client.post(
        '/api/translation/analyze',
        json={
            'source_text': 'Hello',
            'source_language': 'en',
            'target_language': 'es'
        }
    )
    
    assert response.status_code == 401


def test_get_practice_sentence(client, auth_headers):
    """Test getting practice sentence."""
    response = client.get(
        '/api/translation/practice?target_language=es&difficulty=beginner',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'english_sentence' in data
    assert 'difficulty' in data
    assert 'grammar_points' in data


def test_get_progress_empty(client, auth_headers):
    """Test getting progress with no sessions."""
    response = client.get(
        '/api/translation/progress',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'languages' in data


def test_get_translation_history_empty(client, auth_headers):
    """Test getting history with no sessions."""
    response = client.get(
        '/api/translation/history',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'sessions' in data
    assert 'total' in data
    assert data['total'] == 0
