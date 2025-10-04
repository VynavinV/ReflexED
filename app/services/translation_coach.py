"""
AI Translation Coach Service using Google Gemini.
Provides guided translation learning with questions instead of direct answers.
"""
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import json
import re
from config import Config


class TranslationCoachService:
    """
    AI-powered translation coach that asks guided questions
    instead of providing direct translations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the translation coach with Gemini API."""
        self.api_key = api_key or Config.GOOGLE_GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Google Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.TRANSLATION_MODEL)
        
        # Language mappings
        self.language_names = {
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'en': 'English'
        }
    
    def analyze_translation_request(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str,
        difficulty: str = 'intermediate'
    ) -> Dict:
        """
        Analyze a translation request and generate guided questions.
        
        Args:
            source_text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')
            difficulty: User's proficiency level
            
        Returns:
            Dictionary with questions, grammar points, vocabulary insights
        """
        source_language = self.language_names.get(source_lang, source_lang)
        target_language = self.language_names.get(target_lang, target_lang)
        
        prompt = f"""You are an AI Translation Coach for language learning. Your job is to help students learn {target_language} through guided discovery, NOT by giving direct translations.

**Student's Task:**
Translate this {source_language} text to {target_language}: "{source_text}"

**Your Job:**
Instead of providing the translation, ask 5-7 SPECIFIC guided questions that help the student think through:
1. Verb tense and conjugation
2. Vocabulary choices and nuances
3. Grammar rules and sentence structure
4. Cultural/contextual appropriateness
5. Word order and syntax

**Difficulty Level:** {difficulty}

**Output Format (JSON):**
{{
    "questions": [
        {{
            "category": "tense|vocabulary|grammar|cultural|syntax",
            "question": "Specific question about this translation",
            "hint": "A subtle hint without giving the answer",
            "learning_point": "What grammar/vocab concept this teaches"
        }}
    ],
    "grammar_concepts": ["concept1", "concept2"],
    "vocabulary_focus": [
        {{
            "word": "source word",
            "considerations": "What to think about when translating this"
        }}
    ],
    "correct_translation": "The correct translation",
    "common_mistakes": ["mistake1", "mistake2"]
}}

Be specific to the actual sentence, not generic. Ask questions that make students THINK, not just recall.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            
            result = json.loads(result_text)
            
            # Validate and structure the response
            return {
                'source_text': source_text,
                'source_language': source_language,
                'target_language': target_language,
                'questions': result.get('questions', []),
                'grammar_concepts': result.get('grammar_concepts', []),
                'vocabulary_focus': result.get('vocabulary_focus', []),
                'correct_translation': result.get('correct_translation', ''),
                'common_mistakes': result.get('common_mistakes', []),
                'difficulty': difficulty
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Translation analysis failed: {str(e)}")
    
    def evaluate_user_translation(
        self,
        source_text: str,
        user_translation: str,
        source_lang: str,
        target_lang: str,
        correct_translation: str
    ) -> Dict:
        """
        Evaluate a user's translation attempt and provide detailed feedback.
        
        Args:
            source_text: Original text
            user_translation: User's translation attempt
            source_lang: Source language code
            target_lang: Target language code
            correct_translation: The correct translation
            
        Returns:
            Dictionary with scores, feedback, and improvements
        """
        source_language = self.language_names.get(source_lang, source_lang)
        target_language = self.language_names.get(target_lang, target_lang)
        
        prompt = f"""You are evaluating a language student's translation attempt.

**Original ({source_language}):** {source_text}
**Student's Translation ({target_language}):** {user_translation}
**Correct Translation:** {correct_translation}

**Provide detailed evaluation in JSON format:**
{{
    "accuracy_score": 0-100,
    "grammar_score": 0-100,
    "vocabulary_score": 0-100,
    "overall_feedback": "Encouraging feedback highlighting what they did well",
    "specific_errors": [
        {{
            "error_type": "grammar|vocabulary|tense|word_order|spelling",
            "user_version": "what they wrote",
            "correct_version": "what it should be",
            "explanation": "why this is the correction"
        }}
    ],
    "strengths": ["what they got right"],
    "improvements": ["specific things to work on"],
    "learning_resources": ["suggested topics to study"]
}}

Be encouraging but honest. Celebrate correct parts even if overall translation has issues.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            
            result = json.loads(result_text)
            
            return {
                'accuracy_score': result.get('accuracy_score', 0),
                'grammar_score': result.get('grammar_score', 0),
                'vocabulary_score': result.get('vocabulary_score', 0),
                'overall_feedback': result.get('overall_feedback', ''),
                'specific_errors': result.get('specific_errors', []),
                'strengths': result.get('strengths', []),
                'improvements': result.get('improvements', []),
                'learning_resources': result.get('learning_resources', [])
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse evaluation response: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Translation evaluation failed: {str(e)}")
    
    def generate_hints(
        self,
        questions: List[Dict],
        hint_level: int = 1
    ) -> List[Dict]:
        """
        Generate progressive hints for translation questions.
        
        Args:
            questions: List of questions from analyze_translation_request
            hint_level: 1 (subtle) to 3 (more direct)
            
        Returns:
            List of hints with varying levels of directness
        """
        hints = []
        for q in questions:
            hint = {
                'question': q['question'],
                'category': q['category'],
                'hint': q.get('hint', '')
            }
            
            # Add progressive hints based on level
            if hint_level == 1:
                hint['help'] = "Think about the basic rules you've learned."
            elif hint_level == 2:
                hint['help'] = f"Focus on: {q.get('learning_point', 'this concept')}"
            else:  # level 3
                hint['help'] = f"Hint: {q.get('hint', 'Consider the context carefully')}"
            
            hints.append(hint)
        
        return hints
    
    def get_practice_sentence(
        self,
        target_lang: str,
        difficulty: str,
        grammar_focus: Optional[str] = None
    ) -> Dict:
        """
        Generate a practice sentence for translation.
        
        Args:
            target_lang: Language to practice
            difficulty: beginner, intermediate, advanced
            grammar_focus: Optional specific grammar point to practice
            
        Returns:
            Dictionary with practice sentence and metadata
        """
        target_language = self.language_names.get(target_lang, target_lang)
        focus_text = f" focusing on {grammar_focus}" if grammar_focus else ""
        
        prompt = f"""Generate a practice sentence for {difficulty} level {target_language} translation{focus_text}.

**Output JSON:**
{{
    "english_sentence": "The sentence to translate",
    "difficulty": "{difficulty}",
    "grammar_points": ["grammar concepts in this sentence"],
    "vocabulary_level": "description of vocabulary complexity",
    "cultural_notes": "any cultural context to consider"
}}

Make it realistic, practical, and appropriate for the difficulty level.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            
            return json.loads(result_text)
            
        except Exception as e:
            # Fallback to predefined sentences if AI fails
            return self._get_fallback_sentence(difficulty, grammar_focus)
    
    def _get_fallback_sentence(self, difficulty: str, grammar_focus: Optional[str]) -> Dict:
        """Fallback practice sentences if AI generation fails."""
        fallback_sentences = {
            'beginner': {
                'sentence': 'I go to school every day.',
                'grammar': ['present tense', 'daily routines']
            },
            'intermediate': {
                'sentence': 'Yesterday I went to the store and bought some groceries.',
                'grammar': ['past tense', 'sequencing']
            },
            'advanced': {
                'sentence': 'If I had known about the meeting, I would have prepared better.',
                'grammar': ['conditional', 'past perfect']
            }
        }
        
        data = fallback_sentences.get(difficulty, fallback_sentences['intermediate'])
        return {
            'english_sentence': data['sentence'],
            'difficulty': difficulty,
            'grammar_points': data['grammar'],
            'vocabulary_level': difficulty,
            'cultural_notes': 'Standard usage'
        }
