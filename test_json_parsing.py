#!/usr/bin/env python3
"""
Test script to verify JSON parsing improvements in assignment_service.py
"""
import re
import json as _json

def parse_json_improved(text: str, fallback_keys: dict):
    """Improved JSON parsing with better error handling"""
    if not text or not text.strip():
        print("⚠️ Empty response, using fallback")
        return fallback_keys
        
    cleaned = text.strip()
    
    # Try to extract JSON from markdown code blocks (both ```json and ``` variants)
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if m:
        cleaned = m.group(1).strip()
    
    # Try to find JSON object in the text
    if not cleaned.startswith('{'):
        # Look for first { to last }
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1:
            cleaned = cleaned[start:end+1]
    
    # Fix common JSON issues before parsing
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Remove comments (// and /* */)
    cleaned = re.sub(r'//[^\n]*', '', cleaned)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
    
    try:
        data = _json.loads(cleaned)
        print(f"✅ Successfully parsed JSON with {len(str(data))} chars")
        return {**fallback_keys, **data}
    except Exception as e:
        print(f"⚠️ JSON parsing failed: {str(e)[:100]}")
        print(f"⚠️ Received text (first 200 chars): {text[:200]}")
        print(f"⚠️ Cleaned text (first 300 chars): {cleaned[:300]}")
        return fallback_keys


# Test cases
def test_json_parsing():
    print("=" * 60)
    print("Testing JSON Parsing Improvements")
    print("=" * 60)
    
    # Test 1: JSON wrapped in markdown code blocks
    test1 = '''```json
{
  "summary": "Practice problems to master factoring",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "Factor x^2 + 5x + 6",
      "answer": "(x+2)(x+3)",
      "difficulty": "easy"
    }
  ]
}
```'''
    
    print("\n📝 Test 1: JSON in markdown code blocks")
    result1 = parse_json_improved(test1, {"summary": "fallback"})
    print(f"Result: {result1.get('quiz_type', 'FAILED')}")
    assert result1.get('quiz_type') == 'practice', "Test 1 failed"
    print("✅ Test 1 passed")
    
    # Test 2: JSON with trailing commas
    test2 = '''{
  "summary": "Test with trailing commas",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "What is 2+2?",
      "answer": "4",
    },
  ],
}'''
    
    print("\n📝 Test 2: JSON with trailing commas")
    result2 = parse_json_improved(test2, {"summary": "fallback"})
    print(f"Result: {result2.get('quiz_type', 'FAILED')}")
    assert result2.get('quiz_type') == 'practice', "Test 2 failed"
    print("✅ Test 2 passed")
    
    # Test 3: JSON with comments
    test3 = '''{
  // This is a comment
  "summary": "Test with comments",
  "quiz_type": "practice",
  /* Multi-line
     comment */
  "questions": []
}'''
    
    print("\n📝 Test 3: JSON with comments")
    result3 = parse_json_improved(test3, {"summary": "fallback"})
    print(f"Result: {result3.get('quiz_type', 'FAILED')}")
    assert result3.get('quiz_type') == 'practice', "Test 3 failed"
    print("✅ Test 3 passed")
    
    # Test 4: JSON in text with prefix/suffix
    test4 = '''Here is the JSON you requested:
{
  "summary": "Embedded JSON",
  "quiz_type": "socratic",
  "questions": []
}
That's all!'''
    
    print("\n📝 Test 4: JSON embedded in text")
    result4 = parse_json_improved(test4, {"summary": "fallback"})
    print(f"Result: {result4.get('quiz_type', 'FAILED')}")
    assert result4.get('quiz_type') == 'socratic', "Test 4 failed"
    print("✅ Test 4 passed")
    
    # Test 5: Empty response
    test5 = ''
    
    print("\n📝 Test 5: Empty response")
    result5 = parse_json_improved(test5, {"summary": "fallback", "quiz_type": "fallback"})
    print(f"Result: {result5.get('quiz_type', 'FAILED')}")
    assert result5.get('quiz_type') == 'fallback', "Test 5 failed"
    print("✅ Test 5 passed")
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_json_parsing()
