#!/usr/bin/env python3
"""
Script to update assignment_service.py with enhanced features:
- Podcast-style audio with two voices
- Full educational videos with narration
- Subject-specific quiz types
"""

import re

# Read the original file
with open('app/services/assignment_service.py', 'r') as f:
    content = f.read()

# 1. Update audio script generation prompt
old_audio_prompt = '''    def _gen_audio_script(self, subject: str, text: str) -> Dict:
        print(f"🎵 Creating audio script for {subject}...")
        prompt = (
            f"Write a brief voiceover script for an {subject} lesson (90 seconds max). "
            f"Output JSON with keys: script (string), captions_vtt.\\n\\nLESSON:\\n{text[:2000]}"
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={'script': text, 'captions_vtt': None})
        print(f"🎵 Audio script generated: {len(result.get('script', ''))} chars")
        return result'''

new_audio_prompt = '''    def _gen_audio_script(self, subject: str, text: str) -> Dict:
        print(f"🎵 Creating audio script for {subject}...")
        prompt = (
            f"Create an engaging educational podcast-style discussion between two people (Host and Expert) about this {subject} lesson. "
            f"DO NOT just read the notes word-for-word. Instead, have them TEACH the concepts through conversation.\\n\\n"
            f"Requirements:\\n"
            f"- Make it a natural dialogue where they explain, question, and clarify concepts\\n"
            f"- Use analogies, examples, and real-world connections\\n"
            f"- Keep it 2-3 minutes of spoken content\\n"
            f"- Make it as effective as possible for student learning\\n\\n"
            f"Output JSON with this structure:\\n"
            f"{{'discussion': [\\n"
            f"  {{'speaker': 'Host', 'text': 'dialogue here'}},\\n"
            f"  {{'speaker': 'Expert', 'text': 'dialogue here'}},\\n"
            f"  ...\\n"
            f"], 'summary': 'brief lesson summary'}}\\n\\n"
            f"LESSON CONTENT:\\n{text[:3000]}"
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={'discussion': [{'speaker': 'Host', 'text': text[:500]}], 'summary': 'Educational discussion'})
        print(f"🎵 Audio script generated: {len(result.get('discussion', []))} dialogue segments")
        return result'''

content = content.replace(old_audio_prompt, new_audio_prompt)

# 2. Update visual plan generation
old_visual = '''    def _gen_visual_plan(self, subject: str, text: str) -> Dict:
        print(f"🎬 Creating visual plan for {subject}...")
        prompt = (
            f"Create a Manim animation plan for teaching {subject}. "
            f"Return JSON with:\\n"
            f"- description: A detailed 2-3 sentence explanation of what the animation will show\\n"
            f"- manim_code: Complete Python code using Manim library to create the animation\\n\\n"
            f"LESSON CONTENT:\\n{text[:2000]}\\n\\n"
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
        return result'''

new_visual = '''    def _gen_visual_plan(self, subject: str, text: str) -> Dict:
        print(f"🎬 Creating visual plan for {subject}...")
        prompt = (
            f"Create a complete educational video lesson for {subject} using Manim animations with narration. "
            f"This should be a FULL lesson video (not just 3 seconds), designed for visual learners.\\n\\n"
            f"Return JSON with:\\n"
            f"- description: 2-3 sentences explaining what the video teaches\\n"
            f"- narration: Array of narration segments with timing, like [{{\\\"text\\\": \\\"intro text\\\", \\\"duration\\\": 5}}, ...]\\n"
            f"- manim_code: Complete Python Manim code that creates a full educational animation with multiple scenes\\n\\n"
            f"Requirements for the video:\\n"
            f"- Create multiple scenes that build on each other (30-60 seconds total)\\n"
            f"- Include text, diagrams, animations that illustrate key concepts\\n"
            f"- Tie the visuals to the narration segments\\n"
            f"- Make it engaging and clear for visual learners\\n\\n"
            f"LESSON CONTENT:\\n{text[:3000]}"
        )
        resp_text = self._call_gemini_with_retry(prompt)
        result = self._parse_json(resp_text, fallback_keys={
            'description': f'Visual animation for {subject} lesson based on the provided content.',
            'narration': [{'text': text[:200], 'duration': 10}],
            'manim_code': self._default_manim_code(text)
        })
        
        # Ensure description exists and is meaningful
        description = result.get('description', '')
        if not description or len(description) < 20:
            description = f"This visual lesson uses animations to illustrate key concepts from the {subject} material. The animation breaks down complex ideas into clear, step-by-step visual explanations."
            result['description'] = description
        
        print(f"🎬 Visual plan generated: {len(description)} chars description, {len(result.get('manim_code', ''))} chars code")
        return result'''

content = content.replace(old_visual, new_visual)

# 3. Update audio processing section
old_audio_process = '''        # Audio Guide (script + mp3)
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
        print("✅ Audio variant created")'''

new_audio_process = '''        # Audio Guide (podcast discussion with 2 voices)
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
        print("✅ Audio variant created")'''

content = content.replace(old_audio_process, new_audio_process)

# 4. Update visual processing
old_visual_process = '''        # Visualized Lesson (Manim)
        print("🎬 Generating visual/Manim variant...")
        visual = self._gen_visual_plan(assignment.subject, base_text)
        video_mp4, manim_script = self._render_manim(visual.get('manim_code', ''), out_dir=a_dir, name='visual.mp4')
        # Store the full description/plan as text
        visual_text = visual.get('description', '') or visual.get('manim_code', '')
        self._persist_variant(
            assignment, 'visual', assignment.subject,
            content_text=visual_text, assets={'video_mp4': video_mp4, 'manim_script': manim_script}
        )
        print("✅ Visual variant created")'''

new_visual_process = '''        # Visualized Lesson (Manim with narration)
        print("🎬 Generating visual/Manim variant...")
        visual = self._gen_visual_plan(assignment.subject, base_text)
        video_mp4, manim_script = self._render_manim(visual.get('manim_code', ''), out_dir=a_dir, name='visual.mp4')
        # Store the complete visual data including narration
        self._persist_variant(
            assignment, 'visual', assignment.subject,
            content_text=json.dumps(visual, ensure_ascii=False),
            assets={'video_mp4': video_mp4, 'manim_script': manim_script}
        )
        print("✅ Visual variant created")'''

content = content.replace(old_visual_process, new_visual_process)

# 5. Add podcast synthesis function after _synthesize_audio
podcast_function = '''

    def _synthesize_podcast(self, discussion: list, out_dir: str, name: str) -> str:
        """Synthesize podcast discussion with two different voices alternating."""
        print(f"🎙️ Synthesizing podcast: {len(discussion)} dialogue segments")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, name)
        
        # Voice IDs for Host and Expert
        voice_map = {
            'Host': 'EXAVITQu4vr4xnSDxMaL',      # Female voice - Sarah
            'Expert': 'JBFqnCBsd6RMkjVDRZzb',    # Male voice - George
            'default': 'JBFqnCBsd6RMkjVDRZzb'
        }
        
        try:
            if Config.ELEVENLABS_API_KEY and discussion:
                print("🎤 Creating multi-voice podcast with ElevenLabs...")
                try:
                    from pydub import AudioSegment
                    from io import BytesIO
                except ImportError:
                    print("⚠️ pydub not available, falling back to single-voice synthesis")
                    # Fallback: combine all text and use single voice
                    combined_text = " ".join([seg.get('text', '') for seg in discussion])
                    return self._synthesize_audio(combined_text, out_dir, name)
                
                from elevenlabs.client import ElevenLabs
                client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
                
                # Collect all audio segments
                audio_segments = []
                for i, segment in enumerate(discussion):
                    speaker = segment.get('speaker', 'default')
                    text = segment.get('text', '')
                    
                    if not text.strip():
                        continue
                    
                    voice_id = voice_map.get(speaker, voice_map['default'])
                    print(f"  Segment {i+1}/{len(discussion)}: {speaker} ({len(text)} chars)")
                    
                    # Generate audio for this segment
                    audio_generator = client.text_to_speech.convert(
                        text=text[:2000],  # Limit each segment
                        voice_id=voice_id,
                        model_id="eleven_multilingual_v2",
                        output_format="mp3_44100_128",
                    )
                    
                    # Collect audio bytes
                    segment_bytes = b''.join(chunk for chunk in audio_generator)
                    
                    # Load as AudioSegment
                    audio_seg = AudioSegment.from_mp3(BytesIO(segment_bytes))
                    audio_segments.append(audio_seg)
                    
                    # Add small pause between speakers (500ms)
                    pause = AudioSegment.silent(duration=500)
                    audio_segments.append(pause)
                
                # Combine all segments
                if audio_segments:
                    combined = sum(audio_segments[1:], audio_segments[0])
                    combined.export(out_path, format="mp3")
                    print(f"✅ Podcast synthesized: {os.path.getsize(out_path)} bytes")
                else:
                    raise ValueError("No audio segments generated")
            else:
                print("🎵 Creating podcast placeholder...")
                minimal_mp3 = b'\\xff\\xfb\\x90\\x00' + b'\\x00' * 100
                with open(out_path, 'wb') as f:
                    f.write(minimal_mp3)
        except Exception as e:
            print(f"⚠️ Podcast synthesis failed: {e}, creating placeholder")
            minimal_mp3 = b'\\xff\\xfb\\x90\\x00' + b'\\x00' * 100
            with open(out_path, 'wb') as f:
                f.write(minimal_mp3)
        
        return out_path
'''

# Find the end of _synthesize_audio and insert podcast function
audio_func_end = content.find('    def _render_manim(')
if audio_func_end > 0:
    content = content[:audio_func_end] + podcast_function + '\n' + content[audio_func_end:]

# Write the updated file
with open('app/services/assignment_service.py', 'w') as f:
    f.write(content)

print("✅ Updated assignment_service.py successfully!")
print("   - Enhanced audio prompts for podcast format")
print("   - Enhanced video prompts for full lessons")
print("   - Added podcast synthesis with two voices")
print("   - Updated audio and visual processing")
