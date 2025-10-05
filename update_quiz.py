#!/usr/bin/env python3
"""
Script to update quiz generation with subject-specific types
"""

# Read the file
with open('app/services/assignment_service.py', 'r') as f:
    content = f.read()

# Find and replace the quiz generation function
old_quiz = '''    def _gen_quiz(self, subject: str, text: str) -> Dict:
        print(f"🧠 Creating quiz for {subject}...")
        prompt = (
            f"Create a 5-question quiz for {subject}. "
            f"Output JSON with keys: summary, questions (array with question, options, answer, hint).\\n\\nLESSON:\\n{text[:2000]}"
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={'summary': 'Quick check', 'questions': []})
        print(f"🧠 Quiz generated: {len(result.get('questions', []))} questions")
        return result'''

new_quiz = '''    def _gen_quiz(self, subject: str, text: str) -> Dict:
        print(f"🧠 Creating quiz for {subject}...")
        
        # Subject-specific quiz formats
        quiz_formats = {
            'language': {
                'type': 'socratic',
                'instruction': (
                    "Create a Socratic questioning exercise for language learning. "
                    "Don't test knowledge - instead guide the student to discover answers themselves. "
                    "Create 5-7 progressive questions where each builds on the previous answer. "
                    "Output JSON with: {{'summary': 'brief description', 'quiz_type': 'socratic', 'questions': ["
                    "{{'question': 'the question', 'guidance': 'hints to guide thinking', 'follow_up': 'what to consider next'}}]}}"
                )
            },
            'math': {
                'type': 'practice',
                'instruction': (
                    "Create 8-10 practice math problems with varying difficulty levels. "
                    "Include step-by-step solutions and common mistakes to avoid. "
                    "Output JSON with: {{'summary': 'brief description', 'quiz_type': 'practice', 'questions': ["
                    "{{'question': 'the problem', 'difficulty': 'easy|medium|hard', 'solution': 'step-by-step solution', 'common_mistakes': ['mistake 1', 'mistake 2']}}]}}"
                )
            },
            'science': {
                'type': 'practice_repeatable',
                'instruction': (
                    "Create 8-10 science practice questions that can be repeated for mastery. "
                    "Include detailed explanations and real-world applications. "
                    "Output JSON with: {{'summary': 'brief description', 'quiz_type': 'practice_repeatable', 'questions': ["
                    "{{'question': 'the question', 'answer': 'correct answer', 'explanation': 'detailed explanation', 'real_world_example': 'practical application'}}]}}"
                )
            },
            'history': {
                'type': 'timeline_fill',
                'instruction': (
                    "Create a timeline and famous names fill-in-the-blank exercise for history. "
                    "Include dates, events, and key historical figures. "
                    "Output JSON with: {{'summary': 'brief description', 'quiz_type': 'timeline_fill', 'timeline_events': ["
                    "{{'year': 'year', 'event_description': 'description with ___ blanks', 'answer': 'the missing word/phrase'}}], "
                    "'famous_people': [{{'description': 'description with ___ blanks', 'answer': 'the person\\\\'s name', 'significance': 'why they matter'}}]}}"
                )
            },
            'geography': {
                'type': 'practice_repeatable',
                'instruction': (
                    "Create 8-10 geography practice questions that can be repeated for mastery. "
                    "Include maps, locations, features, and facts. "
                    "Output JSON with: {{'summary': 'brief description', 'quiz_type': 'practice_repeatable', 'questions': ["
                    "{{'question': 'the question', 'answer': 'correct answer', 'hint': 'helpful hint', 'interesting_fact': 'related fun fact'}}]}}"
                )
            }
        }
        
        # Get subject-specific format or use default
        quiz_format = quiz_formats.get(subject.lower(), {
            'type': 'standard',
            'instruction': (
                "Create a 5-question quiz with multiple choice options. "
                "Output JSON with: {{'summary': 'brief description', 'quiz_type': 'standard', 'questions': ["
                "{{'question': 'the question', 'options': ['A', 'B', 'C', 'D'], 'correct_answer': 0, 'explanation': 'why this is correct'}}]}}"
            )
        })
        
        prompt = f"{quiz_format['instruction']}\\n\\nLESSON CONTENT:\\n{text[:3000]}"
        
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={
            'summary': f'{subject} practice exercise',
            'quiz_type': quiz_format['type'],
            'questions': []
        })
        print(f"🧠 Quiz generated: {quiz_format['type']} format with {len(result.get('questions', result.get('timeline_events', [])))} items")
        return result'''

content = content.replace(old_quiz, new_quiz)

# Write the updated file
with open('app/services/assignment_service.py', 'w') as f:
    f.write(content)

print("✅ Updated quiz generation with subject-specific types!")
print("   - Language: Socratic questioning")
print("   - Math: Practice problems")
print("   - Science: Practice questions (repeatable)")
print("   - History: Timeline & names fill-in")
print("   - Geography: Practice questions (repeatable)")
