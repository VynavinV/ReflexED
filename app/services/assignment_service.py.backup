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
        # Use gemini-2.5-flash for best performance and lower latency
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
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

        # Audio Guide (script + mp3)
        print("🎵 Generating audio script variant...")
        audio = self._gen_audio_script(assignment.subject, base_text)
        # Convert script to string if it's a list/dict
        raw_script = audio.get('script', '')
        if isinstance(raw_script, list):
            # If it's a list of script segments, extract text and join
            script_text = ' '.join(seg.get('text', str(seg)) if isinstance(seg, dict) else str(seg) for seg in raw_script)
        elif isinstance(raw_script, dict):
            script_text = raw_script.get('text', json.dumps(raw_script, ensure_ascii=False))
        else:
            script_text = str(raw_script)
        
        print("🔊 Synthesizing audio...")
        audio_mp3 = self._synthesize_audio(script_text, out_dir=a_dir, name='narration.mp3')
        # Store the script text for display
        self._persist_variant(
            assignment, 'audio', assignment.subject,
            content_text=script_text, assets={'audio_mp3': audio_mp3, 'captions_vtt': audio.get('captions_vtt')}
        )
        print("✅ Audio variant created")

        # Visualized Lesson (Manim)
        print("🎬 Generating visual/Manim variant...")
        visual = self._gen_visual_plan(assignment.subject, base_text)
        video_mp4, manim_script = self._render_manim(visual.get('manim_code', ''), out_dir=a_dir, name='visual.mp4')
        # Store the full description/plan as text
        visual_text = visual.get('description', '') or visual.get('manim_code', '')
        self._persist_variant(
            assignment, 'visual', assignment.subject,
            content_text=visual_text, assets={'video_mp4': video_mp4, 'manim_script': manim_script}
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
    def _call_gemini_with_retry(self, prompt: str, max_retries: int = 2) -> str:
        """Call Gemini with retry logic for timeout errors."""
        print(f"🤖 Calling Gemini API (attempt 1/{max_retries})...")
        for attempt in range(max_retries):
            try:
                resp = self.model.generate_content(prompt)
                
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
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={'text': text, 'highlights': []})
        print(f"📝 Simplified text generated: {len(result.get('text', ''))} chars")
        return result

    def _gen_audio_script(self, subject: str, text: str) -> Dict:
        print(f"🎵 Creating audio script for {subject}...")
        prompt = (
            f"Write a brief voiceover script for an {subject} lesson (90 seconds max). "
            f"Output JSON with keys: script (string), captions_vtt.\n\nLESSON:\n{text[:2000]}"
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={'script': text, 'captions_vtt': None})
        print(f"🎵 Audio script generated: {len(result.get('script', ''))} chars")
        return result

    def _gen_visual_plan(self, subject: str, text: str) -> Dict:
        print(f"🎬 Creating visual plan for {subject}...")
        prompt = (
            f"Create a Manim animation plan for teaching {subject}. "
            f"Return JSON with:\n"
            f"- description: A detailed 2-3 sentence explanation of what the animation will show\n"
            f"- manim_code: Complete Python code using Manim library to create the animation\n\n"
            f"LESSON CONTENT:\n{text[:2000]}\n\n"
            f"Make the description educational and explain what visual concepts will be shown."
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={
            'description': f'Visual animation for {subject} lesson based on the provided content.',
            'manim_code': self._default_manim_code(text)
        })
        
        # Ensure description exists and is meaningful
        description = result.get('description', '')
        if not description or len(description) < 20:
            description = f"This visual lesson uses animations to illustrate key concepts from the {subject} material. The animation breaks down complex ideas into clear, step-by-step visual explanations."
            result['description'] = description
        
        print(f"🎬 Visual plan generated: {len(description)} chars description, {len(result.get('manim_code', ''))} chars code")
        return result

    def _gen_quiz(self, subject: str, text: str) -> Dict:
        print(f"🧠 Creating quiz for {subject}...")
        prompt = (
            f"Create a 5-question quiz for {subject}. "
            f"Output JSON with keys: summary, questions (array with question, options, answer, hint).\n\nLESSON:\n{text[:2000]}"
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={'summary': 'Quick check', 'questions': []})
        print(f"🧠 Quiz generated: {len(result.get('questions', []))} questions")
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

    def _render_manim(self, manim_code: str, out_dir: str, name: str) -> Tuple[str, str]:
        """Write Manim code to file and render it using Manim CLI."""
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
                        print(f"✅ Manim video rendered successfully: {os.path.getsize(video_path)} bytes")
                        return video_path, script_path
            
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
        
        return video_path, script_path

    # ------------- Helpers -------------
    def _parse_json(self, text: str, fallback_keys: Dict):
        import re, json as _json
        cleaned = text or "{}"
        m = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL)
        if m:
            cleaned = m.group(1)
        try:
            data = _json.loads(cleaned)
            return {**fallback_keys, **data}
        except Exception:
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
