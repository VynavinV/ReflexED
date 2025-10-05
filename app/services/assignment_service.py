"""
Assignment generation service.
Uses Gemini to create scripts/content, Manim to render visuals, and ElevenLabs to generate narration.
For hackathon demo, Manim/ElevenLabs calls are implemented as minimal wrappers with file outputs.
"""
from typing import Dict, Optional, Tuple
import os
import json
import uuid
from datetime import datetime

from config import Config
from app.models import db
from app.models.models import Assignment, AssignmentVersion

# Gemini client (follow main.py syntax)
import google.generativeai as genai
from app.utils.file_extract import extract_text


class AssignmentService:
    def __init__(self, upload_root: Optional[str] = None):
        api_key = Config.GOOGLE_GEMINI_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY must be set")

        genai.configure(api_key=api_key)
        
        # Create separate models for each variant type with optimized configs
        self.model_simplified = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"temperature": 0.5, "max_output_tokens": 2048}
        )
        
        self.model_audio = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"temperature": 0.8, "max_output_tokens": 8192}
        )
        
        self.model_visual = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"temperature": 0.7, "max_output_tokens": 8192}
        )
        
        # Use gemini-2.0-flash-exp for quiz generation (better at structured output)
        # Alternative: "gemini-1.5-pro" for even more reliability (but slower)
        self.model_quiz = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.3,  # Lower temperature for more consistent JSON
                "max_output_tokens": 8192
                # Note: response_mime_type not supported in current SDK version
            }
        )
        self.upload_root = upload_root or os.path.abspath(Config.UPLOAD_FOLDER)
        os.makedirs(self.upload_root, exist_ok=True)

    # ------------- Public API -------------
    def create_assignment(self, *, title: str, subject: str, teacher_id: Optional[str], original_text: Optional[str], file_path: Optional[str]) -> Assignment:
        print(f"🔄 Starting assignment creation: '{title}' ({subject}) by {teacher_id}")
        assignment = Assignment(
            title=title,
            subject=subject,
            teacher_id=teacher_id,
            original_content=original_text,
            file_path=file_path,
            status='generating',
            created_at=datetime.utcnow(),
        )
        db.session.add(assignment)
        db.session.flush()  # Generate ID before using it
        print(f"📝 Created assignment record with ID: {assignment.id}")

        try:
            self._generate_all_variants(assignment)
            assignment.status = 'ready'
            db.session.commit()
            print(f"✅ Assignment {assignment.id} generation completed successfully")
        except Exception as e:
            print(f"❌ Assignment {assignment.id} generation failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            assignment.status = 'failed'
            assignment.error_message = str(e)
            db.session.commit()
            raise

        return assignment

    def regenerate_variant(self, *, assignment: Assignment, variant_type: str, difficulty: str = 'medium') -> AssignmentVersion:
        """Regenerate a specific variant (e.g., quiz) with adjusted difficulty."""
        print(f"🔄 Regenerating {variant_type} variant for assignment {assignment.id} with difficulty={difficulty}")
        
        # Extract base text
        text_parts = []
        if assignment.original_content:
            text_parts.append(assignment.original_content.strip())
        if assignment.file_path:
            file_text = extract_text(assignment.file_path)
            if file_text:
                text_parts.append(file_text.strip())
        
        base_text = "\n\n".join(text_parts) if text_parts else None
        if not base_text:
            raise ValueError("No content found in assignment")
        
        # Truncate very long texts
        if len(base_text) > 4000:
            base_text = base_text[:4000] + "\n\n[Content truncated for processing]"
        
        # Assignment directory
        a_dir = os.path.join(self.upload_root, assignment.id)
        os.makedirs(a_dir, exist_ok=True)
        
        # Find existing variant version to update
        existing_version = AssignmentVersion.query.filter_by(
            assignment_id=assignment.id,
            variant_type=variant_type
        ).first()
        
        if variant_type == 'quiz':
            # Generate new quiz with difficulty parameter
            print(f"🧠 Generating new quiz with difficulty={difficulty}...")
            quiz = self._gen_quiz(assignment.subject, base_text, difficulty=difficulty)
            quiz_path = self._write_json(quiz, os.path.join(a_dir, f'quiz_{difficulty}.json'))
            
            if existing_version:
                # Update existing version
                existing_version.content_text = json.dumps(quiz, ensure_ascii=False)
                existing_version.assets = json.dumps({'quiz_json': quiz_path}, ensure_ascii=False)
                db.session.commit()
                print(f"✅ Quiz variant updated with difficulty={difficulty}")
                return existing_version
            else:
                # Create new version
                return self._persist_variant(
                    assignment, 'quiz', assignment.subject,
                    content_text=json.dumps(quiz, ensure_ascii=False),
                    assets={'quiz_json': quiz_path}
                )
        else:
            raise ValueError(f"Regeneration not supported for variant type: {variant_type}")

    # ------------- Variant Generation -------------
    def _generate_all_variants(self, assignment: Assignment):
        print(f"📖 Extracting content from assignment {assignment.id}")
        
        # Combine text from both sources if available
        text_parts = []
        if assignment.original_content:
            text_parts.append(assignment.original_content.strip())
        if assignment.file_path:
            file_text = extract_text(assignment.file_path)
            if file_text:
                text_parts.append(file_text.strip())
        
        base_text = "\n\n".join(text_parts) if text_parts else None
        
        print(f"📊 Content extracted: {len(base_text) if base_text else 0} characters")
        if not base_text:
            raise ValueError("No content found in assignment")
        
        # Truncate very long texts to avoid timeouts (keep first 4000 chars)
        if len(base_text) > 4000:
            print(f"✂️ Truncating text from {len(base_text)} to 4000 chars")
            base_text = base_text[:4000] + "\n\n[Content truncated for processing]"

        # Ensure directory per assignment
        a_dir = os.path.join(self.upload_root, assignment.id)
        os.makedirs(a_dir, exist_ok=True)
        print(f"📁 Created assignment directory: {a_dir}")

        # Simplified Text
        print("📝 Generating simplified text variant...")
        simplified = self._gen_simplified_text(assignment.subject, base_text)
        self._persist_variant(
            assignment, 'simplified', assignment.subject,
            content_text=json.dumps(simplified, ensure_ascii=False), assets={}
        )
        print("✅ Simplified text variant created")

        # Audio Guide (podcast discussion with 2 voices)
        print("🎵 Generating audio script variant...")
        audio = self._gen_audio_script(assignment.subject, base_text)
        
        # Process discussion format
        discussion = audio.get('discussion', [])
        if discussion and isinstance(discussion, list):
            print(f"🎙️ Creating podcast discussion with {len(discussion)} segments...")
            audio_mp3 = self._synthesize_podcast(discussion, out_dir=a_dir, name='podcast.mp3')
        else:
            # Fallback to simple narration
            script_text = audio.get('script', str(audio))
            if isinstance(script_text, dict):
                script_text = json.dumps(script_text, ensure_ascii=False)
            print("🔊 Synthesizing single-voice audio...")
            audio_mp3 = self._synthesize_audio(str(script_text), out_dir=a_dir, name='narration.mp3')
        
        # Store the complete data
        self._persist_variant(
            assignment, 'audio', assignment.subject,
            content_text=json.dumps(audio, ensure_ascii=False),
            assets={'audio_mp3': audio_mp3, 'summary': audio.get('summary', 'Educational podcast discussion')}
        )
        print("✅ Audio variant created")

        # Visualized Lesson (Manim with narration)
        print("🎬 Generating visual/Manim variant...")
        
        # Try up to 2 times to generate a valid visual plan and video
        video_mp4 = None
        manim_script = None
        narration_audio = None
        
        for attempt in range(2):
            print(f"🎬 Visual generation attempt {attempt + 1}/2...")
            
            visual = self._gen_visual_plan(assignment.subject, base_text)
            
            # Generate narration audio from the visual plan
            narration_segments = visual.get('narration', [])
            if narration_segments and isinstance(narration_segments, list):
                print(f"🎤 Generating narration audio from {len(narration_segments)} segments...")
                # Combine all narration text
                full_narration = ' '.join(seg.get('text', '') for seg in narration_segments)
                narration_audio = self._synthesize_audio(full_narration, out_dir=a_dir, name='narration.mp3')
            
            # Render Manim video
            video_mp4, manim_script, success = self._render_manim(
                visual.get('manim_code', ''), 
                out_dir=a_dir, 
                name='visual_silent.mp4'
            )
            
            # Check if we got a valid video (not a placeholder)
            if success and os.path.exists(video_mp4) and os.path.getsize(video_mp4) > 10000:
                print(f"✅ Valid video generated on attempt {attempt + 1}")
                break
            else:
                print(f"⚠️ Attempt {attempt + 1} failed, {'retrying with new script' if attempt < 1 else 'using placeholder'}...")
                if attempt == 1:  # Last attempt
                    break
        
        # Combine video with narration audio (only if we have a valid video)
        final_video = video_mp4
        if narration_audio and os.path.exists(narration_audio):
            # Check if video is valid (not tiny placeholder)
            if os.path.exists(video_mp4) and os.path.getsize(video_mp4) > 10000:
                print("🎬 Combining video with narration audio...")
                final_video = self._add_audio_to_video(video_mp4, narration_audio, out_dir=a_dir, name='visual.mp4')
            else:
                print("⚠️ Video is placeholder, skipping audio combination. Using narration.mp3 separately.")
                final_video = video_mp4  # Keep placeholder video
        
        # Store the complete visual data including narration
        self._persist_variant(
            assignment, 'visual', assignment.subject,
            content_text=json.dumps(visual, ensure_ascii=False),
            assets={'video_mp4': final_video, 'manim_script': manim_script, 'narration_audio': narration_audio or ''}
        )
        print("✅ Visual variant created")

        # Interactive Quiz
        print("🧠 Generating quiz variant...")
        quiz = self._gen_quiz(assignment.subject, base_text)
        quiz_path = self._write_json(quiz, os.path.join(a_dir, 'quiz.json'))
        # Store the complete quiz data as JSON
        self._persist_variant(
            assignment, 'quiz', assignment.subject,
            content_text=json.dumps(quiz, ensure_ascii=False), assets={'quiz_json': quiz_path}
        )
        print("✅ Quiz variant created")
        print(f"🎉 All variants generated for assignment {assignment.id}")

    # ------------- Gemini Prompts -------------
    def _call_gemini_with_retry(self, prompt: str, model=None, max_retries: int = 2) -> str:
        """Call Gemini with retry logic for timeout errors."""
        if model is None:
            model = self.model_simplified
        print(f"🤖 Calling Gemini API (attempt 1/{max_retries})...")
        for attempt in range(max_retries):
            try:
                resp = model.generate_content(prompt)
                
                # Handle both simple and complex (multi-part) responses
                try:
                    result = resp.text
                except ValueError:
                    # Multi-part response - extract text from all parts
                    result = ''
                    if hasattr(resp, 'candidates') and resp.candidates:
                        for candidate in resp.candidates:
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text'):
                                        result += part.text
                
                print(f"✅ Gemini response received ({len(result)} chars)")
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ Gemini call failed after {max_retries} attempts: {e}")
                    raise
                print(f"⚠️ Gemini retry {attempt + 2}/{max_retries} after error: {e}")
                import time
                time.sleep(2)  # Brief delay before retry
        return ''
    
    def _gen_simplified_text(self, subject: str, text: str) -> Dict:
        print(f"📝 Creating simplified text for {subject}...")
        prompt = f"Simplify the following {subject} lesson for a grade 5 reader. Output JSON with keys: text, highlights (array of key points). Text should be concise and clear.\n\nLESSON:\n{text[:2000]}"
        resp_text = self._call_gemini_with_retry(prompt, model=self.model_simplified)
        result = self._parse_json(resp_text, fallback_keys={'text': text, 'highlights': []})
        print(f"📝 Simplified text generated: {len(result.get('text', ''))} chars")
        return result

    def _gen_audio_script(self, subject: str, text: str) -> Dict:
        print(f"🎵 Creating audio script for {subject}...")
        prompt = (
            'CRITICAL: Return ONLY valid JSON, nothing else. No explanations, no markdown.\n\n'
            'Create an educational podcast discussion between a Host and an Expert about the following lesson. '
            'The discussion should have 6-10 dialogue exchanges that help students understand the material. '
            'Make it engaging and conversational.\n\n'
            'Use this EXACT format:\n'
            '{\n'
            '  "summary": "Brief description of the podcast",\n'
            '  "discussion": [\n'
            '    {"speaker": "Host", "text": "Welcome to our lesson on..."},\n'
            '    {"speaker": "Expert", "text": "Thanks! Let me explain..."},\n'
            '    {"speaker": "Host", "text": "That\'s interesting. Can you elaborate?"},\n'
            '    {"speaker": "Expert", "text": "Of course. Here\'s an example..."}\n'
            '  ]\n'
            '}\n\n'
            f'LESSON:\n{text[:2500]}\n\n'
            'Each speaker should have 2-4 sentences per turn. '
            'Host asks questions and summarizes. Expert explains with examples.\n\n'
            "Return ONLY the JSON object."
        )
        resp_text = self._call_gemini_with_retry(prompt, model=self.model_audio)
        result = self._parse_json(resp_text, fallback_keys={'discussion': [{'speaker': 'Host', 'text': text[:500]}], 'summary': 'Educational podcast discussion'})
        print(f"🎵 Audio script generated: {len(result.get('discussion', []))} dialogue segments")
        return result

    def _gen_visual_plan(self, subject: str, text: str) -> Dict:
        print(f"🎬 Creating visual plan for {subject}...")
        
        # Different examples based on subject
        if subject.lower() == 'math':
            # Example with actual graphs for math
            example_code = r"from manim import *\n\nclass PolynomialLesson(Scene):\n    def construct(self):\n        # Title\n        title = Text('Graphing Polynomials', font_size=48, color=BLUE)\n        title.to_edge(UP)\n        self.play(Write(title))\n        self.wait(1.5)\n        \n        # Create axes\n        axes = Axes(\n            x_range=[-4, 4, 1],\n            y_range=[-8, 8, 2],\n            x_length=6,\n            y_length=5,\n            axis_config={'color': WHITE, 'include_tip': True}\n        )\n        axes.scale(0.7)\n        axes_labels = axes.get_axis_labels(x_label='x', y_label='y')\n        \n        # Quadratic function\n        eq1_label = Text('f(x) = x^2', font_size=32, color=YELLOW)\n        eq1_label.next_to(title, DOWN).shift(LEFT*2)\n        \n        graph1 = axes.plot(lambda x: x**2, color=YELLOW, x_range=[-2.5, 2.5])\n        \n        self.play(Create(axes), Write(axes_labels))\n        self.play(Write(eq1_label))\n        self.play(Create(graph1), run_time=2)\n        self.wait(2)\n        \n        # Cubic function\n        eq2_label = Text('f(x) = x^3 - 2x', font_size=32, color=GREEN)\n        eq2_label.next_to(title, DOWN).shift(LEFT*2)\n        \n        graph2 = axes.plot(lambda x: x**3 - 2*x, color=GREEN, x_range=[-2, 2])\n        \n        self.play(Transform(eq1_label, eq2_label))\n        self.play(Transform(graph1, graph2), run_time=2)\n        self.wait(2)\n        \n        # Summary\n        self.play(FadeOut(graph1), FadeOut(eq1_label), FadeOut(axes), FadeOut(axes_labels))\n        summary = Text('Different degrees create\\ndifferent curve shapes!', font_size=36, color=RED)\n        self.play(Write(summary))\n        self.wait(2)\n        self.play(FadeOut(summary), FadeOut(title))"
        else:
            # Example with text and shapes for other subjects
            example_code = r"from manim import *\n\nclass Lesson(Scene):\n    def construct(self):\n        title = Text('Lesson Topic', font_size=52, color=BLUE)\n        title.to_edge(UP)\n        self.play(Write(title))\n        self.wait(2)\n        \n        concept1 = Text('First Key Concept', font_size=40, color=YELLOW)\n        self.play(FadeIn(concept1))\n        self.wait(3)\n        \n        self.play(FadeOut(concept1))\n        concept2 = Text('Second Key Concept', font_size=40, color=GREEN)\n        self.play(FadeIn(concept2))\n        self.wait(3)\n        \n        self.play(FadeOut(concept2))\n        summary = Text('Key Takeaway!', font_size=36, color=RED)\n        self.play(Write(summary))\n        self.wait(2)\n        self.play(FadeOut(summary), FadeOut(title))"
        
        # Build prompt based on subject
        if subject.lower() == 'math':
            subject_instructions = """MATH-SPECIFIC REQUIREMENTS:
- Use Axes() to create coordinate systems
- Use axes.plot(lambda x: ...) to graph actual functions
- For polynomials: plot quadratic (x**2), cubic (x**3), etc.
- Show multiple graphs with different colors
- Use Transform() to morph one graph into another
- Include axis labels with get_axis_labels()
- Position axes with .scale() and .shift()

Example for graphing:
axes = Axes(x_range=[-4, 4, 1], y_range=[-8, 8, 2], x_length=6, y_length=5)
graph = axes.plot(lambda x: x**2, color=YELLOW)
self.play(Create(axes), Create(graph))
"""
        elif subject.lower() == 'language':
            subject_instructions = """LANGUAGE-SPECIFIC REQUIREMENTS:
- Use Text() to display vocabulary, sentences, and translations.
- Show verb conjugations using tables or lists.
- Use Transform() to show how sentences change (e.g., tense, word order).
- Use different colors to highlight parts of speech (nouns, verbs, adjectives).
- Animate text appearing and disappearing to build sentences step-by-step.

Example for showing a translation:
sentence_fr = Text('Le chat est noir', font_size=40, color=YELLOW)
sentence_en = Text('The cat is black', font_size=40, color=BLUE)
sentence_fr.to_edge(UP)
sentence_en.next_to(sentence_fr, DOWN, buff=0.5)
self.play(Write(sentence_fr))
self.wait(1)
self.play(Write(sentence_en))
"""
            example_code = r"from manim import *\\n\\nclass LanguageLesson(Scene):\\n    def construct(self):\\n        title = Text('French Verb: Être', font_size=48, color=BLUE)\\n        title.to_edge(UP)\\n        self.play(Write(title))\\n        self.wait(1.5)\\n\\n        # Present Tense\\n        t_present = Text('Present Tense', font_size=36, color=YELLOW).next_to(title, DOWN, buff=0.5)\\n        self.play(Write(t_present))\\n\\n        conjugations = VGroup(\\n            Text('Je suis - I am', font_size=32),\\n            Text('Tu es - You are', font_size=32),\\n            Text('Il/Elle est - He/She is', font_size=32)\\n        ).arrange(DOWN, buff=0.3).next_to(t_present, DOWN, buff=0.5)\\n        self.play(Write(conjugations))\\n        self.wait(3)\\n\\n        # Past Tense\\n        t_past = Text('Past Tense (Passé Composé)', font_size=36, color=GREEN).next_to(title, DOWN, buff=0.5)\\n        past_conjugations = VGroup(\\n            Text('J\\'ai été - I have been', font_size=32),\\n            Text('Tu as été - You have been', font_size=32),\\n            Text('Il/Elle a été - He/She has been', font_size=32)\\n        ).arrange(DOWN, buff=0.3).next_to(t_past, DOWN, buff=0.5)\\n\\n        self.play(Transform(t_present, t_past), Transform(conjugations, past_conjugations))\\n        self.wait(3)\\n\\n        self.play(FadeOut(t_present), FadeOut(conjugations), FadeOut(title))"
        else:
            subject_instructions = """GENERAL REQUIREMENTS:
- Use Text() for all text - NO MathTex, NO Tex
- Include 3-5 text elements with animations
- Add visual elements: Circle(), Square(), Rectangle() if relevant
- Use colors: RED, BLUE, GREEN, YELLOW
- Position: .to_edge(UP), .shift(DOWN*2)
"""
        
        prompt = f"""CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON - no markdown, no code blocks, no explanations
2. Do NOT wrap the JSON in ```json or ``` markers  
3. Do NOT include trailing commas
4. Start with {{ and end with }}

Create an educational animated video about: {subject}
Content: {text[:2000]}

{subject_instructions}

ANIMATION REQUIREMENTS:
- Use: Write(), Create(), FadeIn(), FadeOut(), Transform()
- Duration: 30-45 seconds total (use self.wait() to control timing)
- Multiple visual elements (not just text)
- Smooth transitions between scenes

Required JSON (NO trailing commas):
{{
  "description": "Brief description of the video",
  "narration": [
    {{"text": "Intro explanation", "duration": 8}},
    {{"text": "Main concept with details", "duration": 10}},
    {{"text": "Summary and conclusion", "duration": 8}}
  ],
  "manim_code": "{example_code}"
}}

REMEMBER:
- For math: Include actual graphs using axes.plot()
- Include multiple visual elements
- Use self.wait(2-4) between animations for pacing
- Escape single quotes as \\' inside strings
- Return ONLY the JSON object
"""
        
        resp_text = self._call_gemini_with_retry(prompt, model=self.model_visual)
        result = self._parse_json(resp_text, fallback_keys={
            'description': f'Visual animation for {subject} lesson based on the provided content.',
            'narration': [{'text': text[:200], 'duration': 10}],
            'manim_code': self._default_manim_code(text)
        })
        print(f"🎬 Visual plan generated: {len(result.get('description', ''))} chars description, {len(result.get('manim_code', ''))} chars code")
        return result

    def _gen_quiz(self, subject: str, text: str, difficulty: str = 'medium') -> Dict:
        print(f"🧠 Creating quiz for {subject} with difficulty={difficulty}...")
        
        # Add difficulty context to prompts
        difficulty_context = {
            'easy': 'Focus on basic concepts and straightforward questions. Make problems simple and clear.',
            'medium': 'Include a mix of straightforward and moderately challenging questions.',
            'hard': 'Include complex scenarios and multi-step problems that require deeper thinking.'
        }
        diff_instruction = difficulty_context.get(difficulty, difficulty_context['medium'])
        
        # Retry up to 2 times if JSON parsing fails
        max_retries = 2
        
        # Subject-specific quiz formats
        quiz_formats = {
            'language': {
                'type': 'socratic',
                'instruction': (
                    'CRITICAL INSTRUCTIONS:\n'
                    '1. Return ONLY valid JSON - no markdown, no code blocks, no explanations\n'
                    '2. Do NOT wrap the JSON in ```json or ``` markers\n'
                    '3. Do NOT include trailing commas before closing braces or brackets\n'
                    '4. Start your response directly with { and end with }\n\n'
                    f'{diff_instruction}\n\n'
                    'Create 5-7 Socratic questions to guide student learning about the language concepts. '
                    'Include guidance hints and follow-up prompts.\n\n'
                    'Use this EXACT format (notice: NO trailing commas):\n'
                    '{\n'
                    '  "summary": "Guided questions to help you learn",\n'
                    '  "quiz_type": "socratic",\n'
                    '  "questions": [\n'
                    '    {\n'
                    '      "question": "What do you notice about...",\n'
                    '      "guidance": "Think about how...",\n'
                    '      "follow_up": "Now consider..."\n'
                    '    },\n'
                    '    {\n'
                    '      "question": "How would you explain...",\n'
                    '      "guidance": "Look at the pattern...",\n'
                    '      "follow_up": "Can you apply this..."\n'
                    '    }\n'
                    '  ]\n'
                    '}\n\n'
                    "REMEMBER: Start with { and end with }. No markdown formatting."
                )
            },
            'math': {
                'type': 'practice',
                'instruction': (
                    'Create 8-10 practice math problems as a JSON object.\n\n'
                    f'{diff_instruction}\n\n'
                    'CRITICAL JSON FORMATTING RULES:\n'
                    '1. All strings must use escaped characters: \\n for newlines, \\" for quotes\n'
                    '2. Mathematical symbols: Use Unicode or plain text (x^2 not x², ≈ as "approximately")\n'
                    '3. Degree symbols: Write "degrees" or "deg" instead of °\n'
                    '4. NO trailing commas anywhere\n'
                    '5. Each question MUST be complete and self-contained\n\n'
                    'Required JSON structure:\n'
                    '{\n'
                    '  "summary": "Brief description of quiz",\n'
                    '  "quiz_type": "practice",\n'
                    '  "questions": [\n'
                    '    {\n'
                    '      "question": "Problem statement with all necessary info",\n'
                    '      "answer": "Complete answer with units",\n'
                    '      "difficulty": "easy" | "medium" | "hard",\n'
                    '      "solution": "Step-by-step explanation",\n'
                    '      "common_mistakes": ["Mistake 1", "Mistake 2"]\n'
                    '    }\n'
                    '  ]\n'
                    '}\n\n'
                    'EXAMPLE (notice proper escaping and formatting):\n'
                    '{\n'
                    '  "summary": "Practice problems for algebra",\n'
                    '  "quiz_type": "practice",\n'
                    '  "questions": [\n'
                    '    {\n'
                    '      "question": "Solve for x: 2x + 5 = 13",\n'
                    '      "answer": "x = 4",\n'
                    '      "difficulty": "easy",\n'
                    '      "solution": "Subtract 5 from both sides to get 2x = 8. Then divide both sides by 2 to get x = 4.",\n'
                    '      "common_mistakes": ["Forgetting to apply operations to both sides", "Sign errors when subtracting"]\n'
                    '    }\n'
                    '  ]\n'
                    '}'
                )
            },
            'science': {
                'type': 'practice_repeatable',
                'instruction': (
                    'CRITICAL INSTRUCTIONS:\n'
                    '1. Return ONLY valid JSON - no markdown, no code blocks, no explanations\n'
                    '2. Do NOT wrap the JSON in ```json or ``` markers\n'
                    '3. Do NOT include trailing commas before closing braces or brackets\n'
                    '4. Start your response directly with { and end with }\n\n'
                    f'{diff_instruction}\n\n'
                    'Create 8-10 science practice questions that can be repeated for mastery. '
                    'Include detailed explanations and real-world applications.\n\n'
                    'Use this EXACT format (notice: NO trailing commas):\n'
                    '{\n'
                    '  "summary": "Practice questions to build understanding",\n'
                    '  "quiz_type": "practice_repeatable",\n'
                    '  "questions": [\n'
                    '    {\n'
                    '      "question": "What is photosynthesis?",\n'
                    '      "answer": "The process plants use to convert light energy into chemical energy",\n'
                    '      "explanation": "Plants use chlorophyll to capture sunlight and convert CO2 and water into glucose and oxygen",\n'
                    '      "real_world_example": "This is how plants produce oxygen for us to breathe"\n'
                    '    },\n'
                    '    {\n'
                    '      "question": "Why does ice float on water?",\n'
                    '      "answer": "Ice is less dense than liquid water",\n'
                    '      "explanation": "Water molecules form a crystalline structure when frozen, creating more space between molecules",\n'
                    '      "real_world_example": "This allows fish to survive winter in frozen ponds"\n'
                    '    }\n'
                    '  ]\n'
                    '}\n\n'
                    "REMEMBER: Start with { and end with }. No markdown formatting."
                )
            },
            'history': {
                'type': 'timeline_fill',
                'instruction': (
                    'CRITICAL INSTRUCTIONS:\n'
                    '1. Return ONLY valid JSON - no markdown, no code blocks, no explanations\n'
                    '2. Do NOT wrap the JSON in ```json or ``` markers\n'
                    '3. Do NOT include trailing commas before closing braces or brackets\n'
                    '4. Start your response directly with { and end with }\n\n'
                    f'{diff_instruction}\n\n'
                    'Create a timeline and famous names fill-in-the-blank exercise for history. '
                    'Include dates, events, and key historical figures. Use ___ for blanks.\n\n'
                    'Use this EXACT format (notice: NO trailing commas):\n'
                    '{\n'
                    '  "summary": "Timeline and key figures to memorize",\n'
                    '  "quiz_type": "timeline_fill",\n'
                    '  "timeline_events": [\n'
                    '    {\n'
                    '      "year": "1776",\n'
                    '      "event_description": "The ___ of Independence was signed",\n'
                    '      "answer": "Declaration"\n'
                    '    },\n'
                    '    {\n'
                    '      "year": "1945",\n'
                    '      "event_description": "___ ended with the defeat of Nazi Germany",\n'
                    '      "answer": "World War II"\n'
                    '    }\n'
                    '  ],\n'
                    '  "famous_people": [\n'
                    '    {\n'
                    '      "description": "___ led the civil rights movement",\n'
                    '      "answer": "Martin Luther King Jr.",\n'
                    '      "significance": "Fought for racial equality through nonviolent protest"\n'
                    '    },\n'
                    '    {\n'
                    '      "description": "___ discovered America in 1492",\n'
                    '      "answer": "Christopher Columbus",\n'
                    '      "significance": "Opened European exploration of the Americas"\n'
                    '    }\n'
                    '  ]\n'
                    '}\n\n'
                    "REMEMBER: Start with { and end with }. No markdown formatting."
                )
            },
            'geography': {
                'type': 'practice_repeatable',
                'instruction': (
                    'CRITICAL INSTRUCTIONS:\n'
                    '1. Return ONLY valid JSON - no markdown, no code blocks, no explanations\n'
                    '2. Do NOT wrap the JSON in ```json or ``` markers\n'
                    '3. Do NOT include trailing commas before closing braces or brackets\n'
                    '4. Start your response directly with { and end with }\n\n'
                    'Create 8-10 geography practice questions that can be repeated for mastery. '
                    'Include maps, locations, features, and facts.\n\n'
                    'Use this EXACT format (notice: NO trailing commas):\n'
                    '{\n'
                    '  "summary": "Practice questions to learn geography",\n'
                    '  "quiz_type": "practice_repeatable",\n'
                    '  "questions": [\n'
                    '    {\n'
                    '      "question": "What is the capital of France?",\n'
                    '      "answer": "Paris",\n'
                    '      "hint": "This city is known for the Eiffel Tower",\n'
                    '      "interesting_fact": "Paris is called the City of Light"\n'
                    '    },\n'
                    '    {\n'
                    '      "question": "Which river is the longest in the world?",\n'
                    '      "answer": "The Nile River",\n'
                    '      "hint": "It flows through Egypt",\n'
                    '      "interesting_fact": "The Nile is about 6,650 km long"\n'
                    '    }\n'
                    '  ]\n'
                    '}\n\n'
                    "REMEMBER: Start with { and end with }. No markdown formatting."
                )
            }
        }
        
        # Get subject-specific format or use default
        quiz_format = quiz_formats.get(subject.lower(), {
            'type': 'standard',
            'instruction': f'Create a 5-question quiz for {subject}. Output JSON with keys: summary, quiz_type: "standard", questions (array with question, options, answer, hint).'
        })
        
        prompt = f"{quiz_format['instruction']}\n\nLESSON CONTENT:\n{text[:3000]}"
        
        # Try up to max_retries times if JSON parsing fails
        for attempt in range(max_retries):
            resp_text = self._call_gemini_with_retry(prompt, model=self.model_quiz)
            result = self._parse_json(resp_text, fallback_keys={
                'summary': f'{subject} practice exercise',
                'quiz_type': quiz_format['type'],
                'questions': []
            })
            
            # Check if we got valid questions
            question_count = len(result.get('questions', result.get('timeline_events', [])))
            if question_count > 0:
                print(f"🧠 Quiz generated: {quiz_format['type']} format with {question_count} items")
                return result
            else:
                print(f"⚠️ Quiz attempt {attempt + 1}/{max_retries} failed (0 questions), {'retrying...' if attempt < max_retries - 1 else 'using fallback'}")
        
        print(f"🧠 Quiz generated: {quiz_format['type']} format with 0 items (fallback)")
        return result

    # ------------- Synthesis/Rendering -------------
    def _synthesize_audio(self, script: str, out_dir: str, name: str) -> str:
        """Use ElevenLabs SDK to synthesize audio; write placeholder MP3 if no key provided."""
        print(f"🔊 Synthesizing audio: {len(script)} chars of script")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, name)
        try:
            if Config.ELEVENLABS_API_KEY and script.strip():
                print("🎤 Calling ElevenLabs API...")
                # Use official ElevenLabs SDK
                from elevenlabs.client import ElevenLabs
                
                client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
                
                # Generate audio using the new SDK
                audio_generator = client.text_to_speech.convert(
                    text=script[:4000],  # Limit to 4000 chars
                    voice_id="JBFqnCBsd6RMkjVDRZzb",  # Default voice
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                )
                
                # Write audio bytes to file
                with open(out_path, 'wb') as f:
                    for chunk in audio_generator:
                        f.write(chunk)
                
                file_size = os.path.getsize(out_path)
                print(f"✅ Audio synthesized: {file_size} bytes")
            else:
                print("🎵 Creating minimal valid MP3 placeholder...")
                # Create a minimal valid MP3 file (1 second of silence at 44.1kHz)
                # This is a minimal MPEG audio frame
                minimal_mp3 = (
                    b'\xff\xfb\x90\x00'  # MPEG-1 Layer 3 frame header
                    b'\x00' * 100  # Padding for minimal valid frame
                )
                with open(out_path, 'wb') as f:
                    f.write(minimal_mp3)
                print(f"✅ Placeholder audio created: {out_path}")
        except Exception as e:
            print(f"⚠️ Audio synthesis failed: {e}, creating placeholder")
            minimal_mp3 = b'\xff\xfb\x90\x00' + b'\x00' * 100
            with open(out_path, 'wb') as f:
                f.write(minimal_mp3)
        return out_path

    def _synthesize_podcast(self, discussion: list, out_dir: str, name: str) -> str:
        """Synthesize multi-voice podcast from discussion array."""
        print(f"🎙️ Synthesizing podcast: {len(discussion)} dialogue segments")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, name)
        
        try:
            if Config.ELEVENLABS_API_KEY and discussion:
                print("🎤 Creating multi-voice podcast with ElevenLabs...")
                from elevenlabs.client import ElevenLabs
                from pydub import AudioSegment
                
                client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
                
                # Voice mapping
                voices = {
                    "Host": "EXAVITQu4vr4xnSDxMaL",     # Sarah - clear, professional
                    "Expert": "JBFqnCBsd6RMkjVDRZzb"    # George - warm, explanatory
                }
                
                # Generate audio for each dialogue segment
                audio_segments = []
                for i, segment in enumerate(discussion):
                    speaker = segment.get('speaker', 'Host')
                    text = segment.get('text', '')
                    voice_id = voices.get(speaker, voices["Host"])
                    
                    print(f"  Segment {i+1}/{len(discussion)}: {speaker} ({len(text)} chars)")
                    
                    # Generate audio
                    audio_generator = client.text_to_speech.convert(
                        text=text[:1000],  # Limit per segment
                        voice_id=voice_id,
                        model_id="eleven_multilingual_v2",
                        output_format="mp3_44100_128",
                    )
                    
                    # Collect audio bytes
                    audio_bytes = b''
                    for chunk in audio_generator:
                        audio_bytes += chunk
                    
                    # Convert to AudioSegment
                    from io import BytesIO
                    segment_audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
                    audio_segments.append(segment_audio)
                    
                    # Add pause between speakers (500ms)
                    if i < len(discussion) - 1:
                        pause = AudioSegment.silent(duration=500)
                        audio_segments.append(pause)
                
                # Combine all segments
                combined = audio_segments[0]
                for seg in audio_segments[1:]:
                    combined += seg
                
                # Export
                combined.export(out_path, format="mp3")
                file_size = os.path.getsize(out_path)
                print(f"✅ Podcast synthesized: {file_size} bytes")
            else:
                # Fallback: single voice with all text
                all_text = ' '.join(seg.get('text', '') for seg in discussion)
                return self._synthesize_audio(all_text, out_dir, name)
                
        except Exception as e:
            print(f"⚠️ Podcast synthesis failed: {e}, using fallback")
            all_text = ' '.join(seg.get('text', '') for seg in discussion)
            return self._synthesize_audio(all_text, out_dir, name)
        
        return out_path

    def _render_manim(self, manim_code: str, out_dir: str, name: str) -> Tuple[str, str, bool]:
        """Write Manim code to file and render it using Manim CLI. Returns (video_path, script_path, success)."""
        print(f"🎬 Rendering Manim animation: {len(manim_code)} chars of code")
        os.makedirs(out_dir, exist_ok=True)
        script_path = os.path.join(out_dir, 'scene.py')
        with open(script_path, 'w') as f:
            f.write(manim_code)
        print(f"📝 Manim script written to {script_path}")
        
        video_path = os.path.join(out_dir, name)
        
        # Try to render with Manim CLI
        try:
            import subprocess
            import re
            
            # Extract class name from the Manim code
            class_match = re.search(r'class\s+(\w+)\s*\(Scene\)', manim_code)
            scene_class = class_match.group(1) if class_match else 'TitleScene'
            
            print(f"🎬 Executing Manim render for scene '{scene_class}'...")
            print(f"⏱️  Estimated time: 10-30 seconds depending on complexity...")
            
            # Run manim with low quality for faster rendering (-ql = 480p, 15fps)
            # -p = preview (don't open), --media_dir = output location
            result = subprocess.run(
                ['manim', '-ql', '--disable_caching', '-o', name, script_path, scene_class],
                cwd=out_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                # Manim outputs to media/videos/scene/<quality>/output.mp4
                # Find the rendered video
                media_dir = os.path.join(out_dir, 'media', 'videos', 'scene', '480p15')
                if os.path.exists(media_dir):
                    rendered_files = [f for f in os.listdir(media_dir) if f.endswith('.mp4')]
                    if rendered_files:
                        src = os.path.join(media_dir, rendered_files[0])
                        # Move to our desired location
                        import shutil
                        shutil.copy(src, video_path)
                        file_size = os.path.getsize(video_path)
                        print(f"✅ Manim video rendered successfully: {file_size} bytes")
                        return video_path, script_path, True
            
            # Check if error is due to missing LaTeX
            if 'latex: command not found' in result.stderr or 'latex' in result.stderr.lower():
                print("⚠️ Manim rendering failed: LaTeX not installed")
                print("💡 Tip: Install LaTeX with: brew install --cask mactex-no-gui (macOS)")
            else:
                print(f"⚠️ Manim rendering failed (code {result.returncode}): {result.stderr[:200]}")
            print("📦 Creating fallback placeholder...")
            
        except subprocess.TimeoutExpired:
            print("⚠️ Manim rendering timed out (>60s), creating placeholder...")
        except FileNotFoundError:
            print("⚠️ Manim command not found. Install with: pip install manim")
        except Exception as e:
            print(f"⚠️ Manim rendering error: {e}")
        
        # Fallback: create placeholder
        if not os.path.exists(video_path):
            print("🎬 Creating minimal valid MP4 placeholder...")
            minimal_mp4 = (
                b'\x00\x00\x00\x20ftypisom'  # ftyp box
                b'\x00\x00\x02\x00isom'  # compatible brands
                b'iso2avc1mp41'
                b'\x00\x00\x00\x08free'  # free box for padding
            )
            with open(video_path, 'wb') as f:
                f.write(minimal_mp4)
            print(f"✅ Placeholder video created: {video_path}")
        
        return video_path, script_path, False

    def _add_audio_to_video(self, video_path: str, audio_path: str, out_dir: str, name: str) -> str:
        """Combine video and audio using ffmpeg."""
        import subprocess
        
        output_path = os.path.join(out_dir, name)
        
        # Check if video file is valid (not a tiny placeholder)
        if not os.path.exists(video_path):
            print(f"⚠️ Video file doesn't exist: {video_path}")
            return video_path
        
        video_size = os.path.getsize(video_path)
        if video_size < 10000:  # Less than 10KB = placeholder
            print(f"⚠️ Video file too small ({video_size} bytes), likely placeholder. Skipping ffmpeg.")
            return video_path
        
        try:
            print(f"🎬 Combining video {video_path} ({video_size} bytes) with audio {audio_path}...")
            
            # Use ffmpeg to combine video and audio
            # -i video.mp4 = input video
            # -i audio.mp3 = input audio
            # -c:v copy = copy video codec (no re-encoding)
            # -c:a aac = encode audio as AAC
            # -shortest = end when shortest stream ends
            # -y = overwrite output file
            result = subprocess.run([
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Video and audio combined successfully: {file_size} bytes")
                return output_path
            else:
                print(f"⚠️ ffmpeg failed (code {result.returncode}): {result.stderr[:200]}")
                print("📦 Using original video without audio...")
                return video_path
                
        except FileNotFoundError:
            print("⚠️ ffmpeg not found. Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
            print("📦 Using original video without audio...")
            return video_path
        except subprocess.TimeoutExpired:
            print("⚠️ ffmpeg timed out, using original video...")
            return video_path
        except Exception as e:
            print(f"⚠️ Error combining video and audio: {e}")
            print("📦 Using original video without audio...")
            return video_path

    # ------------- Helpers -------------
    def _parse_json(self, text: str, fallback_keys: Dict):
        import re, json as _json
        
        if not text or not text.strip():
            print("⚠️ Empty response from Gemini, using fallback")
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
        
        # Fix common escaping issues
        # Replace problematic Unicode characters that might cause issues
        replacements = {
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Ellipsis
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
            print(f"⚠️ Received text (first 200 chars): {text[:200]}")
            
            # Try to show the problematic area
            if e.pos and e.pos < len(cleaned):
                start = max(0, e.pos - 50)
                end = min(len(cleaned), e.pos + 50)
                print(f"⚠️ Problem area: ...{cleaned[start:end]}...")
            
            return fallback_keys
        except Exception as e:
            print(f"⚠️ Unexpected error parsing JSON: {str(e)[:100]}")
            return fallback_keys

    def _default_manim_code(self, title: str) -> str:
        # Sanitize title for use in Python string literal
        safe = (title or "Lesson")[:60]
        # Escape quotes and replace newlines/special chars
        safe = safe.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
        # Remove any other problematic characters
        safe = ''.join(c if c.isprintable() or c.isspace() else ' ' for c in safe)
        # Collapse multiple spaces
        safe = ' '.join(safe.split())
        
        return (
            "from manim import *\n\n"
            "class TitleScene(Scene):\n"
            "    def construct(self):\n"
            f"        title = Text(\"{safe}\")\n"
            "        self.play(Write(title))\n"
            "        self.wait(1)\n"
        )

    def _persist_variant(self, assignment: Assignment, vtype: str, subject: str, *, content_text: Optional[str], assets: Optional[Dict]):
        print(f"💾 Saving {vtype} variant to database...")
        version = AssignmentVersion(
            assignment_id=assignment.id,
            variant_type=vtype,
            subject=subject,
            content_text=content_text,
            assets=assets or {},
            ready=True,
            created_at=datetime.utcnow(),
        )
        db.session.add(version)
        db.session.commit()
        print(f"✅ {vtype} variant saved (ID: {version.id})")

    # Deprecated: use extract_text
    def _read_file_text(self, path: Optional[str]):
        return extract_text(path) if path else None
    
    def _write_json(self, data: Dict, path: str) -> str:
        """Write dict to JSON file and return path."""
        print(f"📄 Writing JSON file: {path}")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ JSON file written ({len(json.dumps(data))} chars)")
        return path
