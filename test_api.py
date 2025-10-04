#!/usr/bin/env python3
"""
Quick API test script to verify everything is working.
Run this after starting the server with: python run.py
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5001"

def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_health():
    """Test health endpoint."""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_register():
    """Test user registration."""
    print_section("Testing User Registration")
    try:
        data = {
            "email": "testbot@polylearn.com",
            "username": "testbot",
            "password": "TestBot123",
            "first_name": "Test",
            "last_name": "Bot",
            "role": "student"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            print(f"User: {result['user']['username']}")
            return result['access_token']
        elif response.status_code == 409:
            print("ℹ️  User already exists, trying login...")
            return test_login(data['email'], data['password'])
        else:
            print(f"❌ Error: {result}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login(email, password):
    """Test user login."""
    print_section("Testing User Login")
    try:
        data = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Login successful!")
            print(f"User: {result['user']['username']}")
            return result['access_token']
        else:
            print(f"❌ Error: {result}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_translation_analyze(token):
    """Test translation analysis."""
    print_section("Testing Translation Analysis (AI Coach)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "source_text": "I went to the store yesterday",
            "source_language": "en",
            "target_language": "es",
            "difficulty": "intermediate"
        }
        response = requests.post(f"{BASE_URL}/api/translation/analyze", 
                                headers=headers, json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ AI Analysis successful!")
            print(f"\nSession ID: {result['session_id']}")
            print(f"\nAI Questions ({len(result['questions'])}):")
            for i, q in enumerate(result['questions'][:3], 1):  # Show first 3
                print(f"  {i}. [{q['category']}] {q['question']}")
            if len(result['questions']) > 3:
                print(f"  ... and {len(result['questions']) - 3} more questions")
            return result['session_id']
        else:
            print(f"❌ Error: {result}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_translation_submit(token, session_id):
    """Test translation submission."""
    print_section("Testing Translation Submission")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "session_id": session_id,
            "user_translation": "Fui a la tienda ayer",
            "time_spent_seconds": 120,
            "hints_requested": 0
        }
        response = requests.post(f"{BASE_URL}/api/translation/submit",
                                headers=headers, json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Translation submitted successfully!")
            eval_data = result['evaluation']
            print(f"\n📊 Scores:")
            print(f"  Accuracy:   {eval_data['accuracy_score']}%")
            print(f"  Grammar:    {eval_data['grammar_score']}%")
            print(f"  Vocabulary: {eval_data['vocabulary_score']}%")
            print(f"\n💬 Feedback: {eval_data['overall_feedback']}")
            return True
        else:
            print(f"❌ Error: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_progress(token):
    """Test getting user progress."""
    print_section("Testing Get Progress")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/translation/progress", 
                               headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Progress retrieved!")
            if result['languages']:
                for lang_progress in result['languages']:
                    print(f"\n📈 {lang_progress['language'].upper()}:")
                    print(f"  Sessions: {lang_progress['completed_sessions']}")
                    print(f"  Avg Accuracy: {lang_progress['average_accuracy']:.1f}%")
                    print(f"  Streak: {lang_progress['current_streak_days']} days")
            else:
                print("  No progress data yet")
            return True
        else:
            print(f"❌ Error: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🚀 PolyLearn API Test Suite")
    print("="*60)
    print("Make sure the server is running: python run.py")
    print("="*60)
    
    # Test health
    if not test_health():
        print("\n❌ Server is not responding. Is it running?")
        sys.exit(1)
    
    # Test authentication
    token = test_register()
    if not token:
        print("\n❌ Authentication failed")
        sys.exit(1)
    
    # Test translation workflow
    session_id = test_translation_analyze(token)
    if session_id:
        test_translation_submit(token, session_id)
    
    # Test progress
    test_get_progress(token)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\n📚 Next steps:")
    print("  1. Import PolyLearn_API.postman_collection.json into Postman")
    print("  2. Update your frontend to call these APIs")
    print("  3. Run pytest for comprehensive testing")
    print()

if __name__ == "__main__":
    main()
