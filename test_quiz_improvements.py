#!/usr/bin/env python3
"""
Test quiz generation improvements with problematic content
"""
import re
import json as _json

def parse_json_improved(text: str, fallback_keys: dict):
    """Enhanced JSON parsing with Unicode character handling"""
    if not text or not text.strip():
        print("⚠️ Empty response, using fallback")
        return fallback_keys
        
    cleaned = text.strip()
    
    # Try to extract JSON from markdown code blocks
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if m:
        cleaned = m.group(1).strip()
    
    # Try to find JSON object in the text
    if not cleaned.startswith('{'):
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1:
            cleaned = cleaned[start:end+1]
    
    # Remove trailing commas
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Remove comments
    cleaned = re.sub(r'//[^\n]*', '', cleaned)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
    
    # Fix Unicode characters
    replacements = {
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '--',
        '\u2026': '...',
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    try:
        data = _json.loads(cleaned)
        print(f"✅ Successfully parsed JSON with {len(str(data))} chars")
        return {**fallback_keys, **data}
    except _json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing failed: {str(e)[:100]}")
        print(f"⚠️ Error at line {e.lineno}, column {e.colno}")
        if e.pos and e.pos < len(cleaned):
            start = max(0, e.pos - 50)
            end = min(len(cleaned), e.pos + 50)
            print(f"⚠️ Problem area: ...{cleaned[start:end]}...")
        return fallback_keys
    except Exception as e:
        print(f"⚠️ Unexpected error: {str(e)[:100]}")
        return fallback_keys


def test_problematic_cases():
    print("=" * 70)
    print("Testing Quiz Generation JSON Parser Improvements")
    print("=" * 70)
    
    # Test 1: Unicode superscripts and symbols
    test1 = '''{
  "summary": "Practice problems",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "Find the area of a circle with radius 7cm",
      "answer": "153.94 cm²",
      "solution": "Use A = πr². A = π(7)² = 49π ≈ 153.94"
    }
  ]
}'''
    
    print("\n📝 Test 1: Unicode mathematical symbols (², π, ≈)")
    result1 = parse_json_improved(test1, {"summary": "fallback"})
    has_questions = len(result1.get('questions', [])) > 0
    print(f"Result: {'✅ PASS' if has_questions else '❌ FAIL'} - {len(result1.get('questions', []))} questions")
    
    # Test 2: Smart quotes and dashes (as they would come from Gemini)
    test2 = '''{
  "summary": "Test with smart quotes",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "What\u2019s the answer to \u201clife, the universe, and everything\u201d?",
      "answer": "42\u2014the ultimate answer",
      "solution": "As Douglas Adams wrote\u2026 it\u2019s 42."
    }
  ]
}'''
    
    print("\n📝 Test 2: Smart quotes and Unicode punctuation")
    result2 = parse_json_improved(test2, {"summary": "fallback"})
    has_questions = len(result2.get('questions', [])) > 0
    print(f"Result: {'✅ PASS' if has_questions else '❌ FAIL'} - {len(result2.get('questions', []))} questions")
    
    # Test 3: Unterminated string (should fail gracefully)
    test3 = '''{
  "summary": "Broken JSON",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "This string is not terminated properly
      "answer": "This will fail"
    }
  ]
}'''
    
    print("\n📝 Test 3: Unterminated string (should fail gracefully)")
    result3 = parse_json_improved(test3, {"summary": "fallback", "questions": []})
    is_fallback = result3.get('summary') == 'fallback'
    print(f"Result: {'✅ PASS' if is_fallback else '❌ FAIL'} - Used fallback correctly")
    
    # Test 4: Trailing commas
    test4 = '''{
  "summary": "Quiz with trailing commas",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "What is 2+2?",
      "answer": "4",
    },
  ],
}'''
    
    print("\n📝 Test 4: Trailing commas (should auto-fix)")
    result4 = parse_json_improved(test4, {"summary": "fallback"})
    has_questions = len(result4.get('questions', [])) > 0
    print(f"Result: {'✅ PASS' if has_questions else '❌ FAIL'} - {len(result4.get('questions', []))} questions")
    
    # Test 5: Real-world example from error logs
    test5 = '''{
  "summary": "Practice problems to master the concepts",
  "quiz_type": "practice",
  "questions": [
    {
      "question": "Find the y-intercept of the polynomial P(x) = 3x³ - 2x + 7",
      "answer": "(0, 7)",
      "difficulty": "easy",
      "solution": "The y-intercept occurs when x = 0. Substitute to get P(0) = 7, so the point is (0, 7).",
      "common_mistakes": ["Confusing x-intercept with y-intercept", "Forgetting to evaluate at x=0"]
    }
  ]
}'''
    
    print("\n📝 Test 5: Real-world polynomial problem")
    result5 = parse_json_improved(test5, {"summary": "fallback"})
    has_questions = len(result5.get('questions', [])) > 0
    print(f"Result: {'✅ PASS' if has_questions else '❌ FAIL'} - {len(result5.get('questions', []))} questions")
    if has_questions:
        print(f"   Question: {result5['questions'][0]['question'][:50]}...")
    
    print("\n" + "=" * 70)
    print("✨ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    test_problematic_cases()
