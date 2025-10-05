#!/usr/bin/env python3
"""
Quick test script to verify assignment creation and retrieval works.
Run after server is started.
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def test_create_assignment():
    """Test creating an assignment with text content."""
    print("🧪 Testing assignment creation...")
    
    # Create assignment with plain text
    data = {
        "title": "Test Science Lesson: Photosynthesis",
        "subject": "science",
        "text": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar. This process is essential for life on Earth."
    }
    
    response = requests.post(
        f"{BASE_URL}/api/assignments/create",
        headers={"Authorization": "Bearer demo-token"},
        json=data,
        timeout=120  # Generation can take time
    )
    
    if response.status_code == 201:
        assignment = response.json()
        print(f"✅ Assignment created: {assignment['id']}")
        print(f"   Status: {assignment['status']}")
        print(f"   Versions: {len(assignment.get('versions', []))}")
        
        for version in assignment.get('versions', []):
            print(f"   - {version['variant_type']}: {'✓' if version['ready'] else '✗'}")
        
        return assignment['id']
    else:
        print(f"❌ Failed to create assignment: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_list_assignments():
    """Test listing all assignments."""
    print("\n🧪 Testing assignment listing...")
    
    response = requests.get(
        f"{BASE_URL}/api/assignments",
        headers={"Authorization": "Bearer demo-token"}
    )
    
    if response.status_code == 200:
        assignments = response.json()
        print(f"✅ Found {len(assignments)} assignments")
        for a in assignments[:3]:
            print(f"   - {a['title']} ({a['status']})")
    else:
        print(f"❌ Failed to list assignments: {response.status_code}")


def test_get_assignment(assignment_id):
    """Test getting a specific assignment."""
    if not assignment_id:
        print("\n⏭️  Skipping get assignment test (no ID)")
        return
    
    print(f"\n🧪 Testing assignment retrieval ({assignment_id})...")
    
    response = requests.get(
        f"{BASE_URL}/api/assignments/{assignment_id}",
        headers={"Authorization": "Bearer demo-token"}
    )
    
    if response.status_code == 200:
        assignment = response.json()
        print(f"✅ Retrieved: {assignment['title']}")
        print(f"   Versions: {len(assignment.get('versions', []))}")
    else:
        print(f"❌ Failed to get assignment: {response.status_code}")


def test_student_view():
    """Test student view endpoint."""
    print("\n🧪 Testing student view...")
    
    response = requests.get(
        f"{BASE_URL}/api/assignments/student",
        headers={"Authorization": "Bearer demo-token"}
    )
    
    if response.status_code == 200:
        assignments = response.json()
        print(f"✅ Student view: {len(assignments)} ready assignments")
        for a in assignments[:3]:
            print(f"   - {a['title']}: {a.get('variant_types', [])} variants")
    else:
        print(f"❌ Failed to get student view: {response.status_code}")


if __name__ == "__main__":
    print("=" * 60)
    print("ReflexED Assignment API Test Suite")
    print("=" * 60)
    
    # Run tests
    assignment_id = test_create_assignment()
    time.sleep(1)
    test_list_assignments()
    time.sleep(0.5)
    test_get_assignment(assignment_id)
    time.sleep(0.5)
    test_student_view()
    
    print("\n" + "=" * 60)
    print("✨ Test suite complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Open http://127.0.0.1:5001/teacher.html")
    print("   2. Upload a file or enter text")
    print("   3. Click 'Generate Lesson Materials'")
    print("   4. View results in Student Portal: http://127.0.0.1:5001/student.html")
    print()
