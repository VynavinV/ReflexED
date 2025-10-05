# Video Audio Integration - Implementation Guide

## 🎯 Problem Solved

Previously, Manim-generated videos had NO audio. Now videos include ElevenLabs narration synchronized with the visual content.

## 🔧 Changes Made

### 1. Visual Variant Generation Enhanced

**File**: `app/services/assignment_service.py`

**Lines 202-222**: Updated `_generate_all_variants()` method

```python
# Visualized Lesson (Manim with narration)
print("🎬 Generating visual/Manim variant...")
visual = self._gen_visual_plan(assignment.subject, base_text)

# Generate narration audio from the visual plan
narration_segments = visual.get('narration', [])
narration_audio = None
if narration_segments and isinstance(narration_segments, list):
    print(f"🎤 Generating narration audio from {len(narration_segments)} segments...")
    # Combine all narration text
    full_narration = ' '.join(seg.get('text', '') for seg in narration_segments)
    narration_audio = self._synthesize_audio(full_narration, out_dir=a_dir, name='narration.mp3')

# Render Manim video
video_mp4, manim_script = self._render_manim(visual.get('manim_code', ''), out_dir=a_dir, name='visual_silent.mp4')

# Combine video with narration audio
final_video = video_mp4
if narration_audio and os.path.exists(narration_audio):
    print("🎬 Combining video with narration audio...")
    final_video = self._add_audio_to_video(video_mp4, narration_audio, out_dir=a_dir, name='visual.mp4')
```

### 2. New Method: Audio-Video Combination

**Lines 660-708**: Added `_add_audio_to_video()` method

```python
def _add_audio_to_video(self, video_path: str, audio_path: str, out_dir: str, name: str) -> str:
    """Combine video and audio using ffmpeg."""
    import subprocess
    
    output_path = os.path.join(out_dir, name)
    
    try:
        print(f"🎬 Combining video {video_path} with audio {audio_path}...")
        
        # Use ffmpeg to combine video and audio
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
            print(f"⚠️ ffmpeg failed, using original video without audio...")
            return video_path
            
    except FileNotFoundError:
        print("⚠️ ffmpeg not found. Install with: brew install ffmpeg")
        return video_path
    except Exception as e:
        print(f"⚠️ Error combining video and audio: {e}")
        return video_path
```

## 📋 How It Works

### Step-by-Step Process

1. **Gemini Generates Visual Plan**
   - Creates `narration` array with text segments
   - Each segment has `text` and `duration` fields
   - Example:
     ```json
     {
       "narration": [
         {"text": "Welcome to the lesson on WW2 progression", "duration": 8},
         {"text": "The war began in 1939 when Germany invaded Poland", "duration": 10},
         {"text": "Let's explore the major events...", "duration": 7}
       ]
     }
     ```

2. **Audio Generation**
   - Combines all narration text into one string
   - Calls ElevenLabs API to synthesize speech
   - Saves as `narration.mp3`
   - Uses default voice: `JBFqnCBsd6RMkjVDRZzb` (George)

3. **Video Rendering**
   - Manim renders visual animation
   - Saves as `visual_silent.mp4` (no audio)
   - Uses low quality (`-ql`) for faster rendering (480p, 15fps)

4. **Audio-Video Combination**
   - ffmpeg merges video + audio
   - Video codec: copy (no re-encoding)
   - Audio codec: AAC
   - Saves final output as `visual.mp4`

5. **Database Storage**
   - Stores both video and audio file paths
   - Assets: `{'video_mp4': 'visual.mp4', 'manim_script': 'scene.py', 'narration_audio': 'narration.mp3'}`

## 🎬 ffmpeg Command Details

```bash
ffmpeg -y \
  -i visual_silent.mp4 \    # Input video (no audio)
  -i narration.mp3 \        # Input audio
  -c:v copy \               # Copy video stream (no re-encoding)
  -c:a aac \                # Encode audio as AAC
  -shortest \               # End when shortest stream ends
  visual.mp4                # Output file
```

**Parameters Explained:**
- `-y`: Overwrite output file without asking
- `-i`: Input file
- `-c:v copy`: Copy video codec (fast, no quality loss)
- `-c:a aac`: Convert audio to AAC format (MP4 compatible)
- `-shortest`: Trim to shorter stream (prevents long silence)

## 🧪 Testing

### Prerequisites
1. **ffmpeg installed**:
   ```bash
   ffmpeg -version
   ```
   If not installed:
   ```bash
   brew install ffmpeg  # macOS
   ```

2. **ElevenLabs API key** set in environment:
   ```bash
   echo $ELEVENLABS_API_KEY
   ```

3. **Manim installed**:
   ```bash
   pip list | grep manim
   ```

### Test New Assignment Creation

1. **Create a new assignment** via Teacher view
   - Subject: Any (history, science, math, etc.)
   - Text: Any lesson content
   - Wait for generation to complete (~30-60 seconds)

2. **Check server logs** for:
   ```
   🎤 Generating narration audio from X segments...
   🔊 Synthesizing audio: XXX chars of script
   🎤 Calling ElevenLabs API...
   ✅ Audio synthesized: XXXX bytes
   🎬 Combining video with narration audio...
   ✅ Video and audio combined successfully: XXXX bytes
   ```

3. **Verify video file** has audio:
   ```bash
   ffprobe -v error -show_entries stream=codec_type,codec_name \
     -of default=noprint_wrappers=1 \
     uploads/[assignment-id]/visual.mp4
   ```
   
   Expected output:
   ```
   codec_name=h264
   codec_type=video
   codec_name=aac
   codec_type=audio
   ```

4. **Play video** in student view:
   - Go to Student Dashboard
   - Select the new assignment
   - Click Visual tab
   - Play video → should have narration audio

### Test Existing Assignments

**Note**: Existing assignments created before this update will NOT have audio in videos. Only newly created assignments will include narration.

To add audio to existing assignments:
1. Delete old assignments from teacher view
2. Recreate them with same content
3. New versions will have audio-enabled videos

## 📊 File Structure

Each assignment directory now contains:

```
uploads/[assignment-id]/
├── podcast.mp3           # Podcast audio variant
├── narration.mp3         # NEW: Video narration audio
├── visual_silent.mp4     # Intermediate: video without audio
├── visual.mp4            # Final: video WITH audio
├── scene.py              # Manim script
├── quiz.json             # Quiz data
└── media/                # Manim render artifacts
    └── videos/
        └── scene/
            └── 480p15/
                └── [rendered].mp4
```

## 🔍 Troubleshooting

### Problem: Video still has no audio

**Check 1**: ffmpeg installed?
```bash
which ffmpeg
```
If missing: `brew install ffmpeg`

**Check 2**: ElevenLabs API working?
```bash
ls -lh uploads/[assignment-id]/narration.mp3
```
Should be > 10KB. If tiny (~100 bytes), check API key.

**Check 3**: Server logs show errors?
Look for:
- `⚠️ ffmpeg failed`
- `⚠️ Audio synthesis failed`
- `⚠️ ffmpeg not found`

**Check 4**: Gemini returned narration data?
```bash
cat instance/polylearn.db | grep narration
```
Or check visual variant content_text in database.

### Problem: Audio doesn't sync with video

**Cause**: Video duration ≠ audio duration

**Fix**: Adjust narration in Gemini prompt to match video length.

Current behavior: `-shortest` flag ends video when audio ends (or vice versa).

### Problem: Audio quality poor

**Current**: Single voice (George), simple concatenation of narration segments

**Enhancement Ideas**:
1. Use different voices for different sections
2. Add pauses between narration segments
3. Adjust speech rate to match video timing
4. Use SSML for better prosody

## 🚀 Future Enhancements

### 1. Multi-Voice Narration
Similar to podcast feature, use Host + Expert voices:
```python
voices = {
    'intro': 'Sarah',    # Warm, welcoming
    'content': 'George', # Professional, clear
    'summary': 'Sarah'   # Concluding tone
}
```

### 2. Synchronized Timing
Match narration segments to video scene changes:
```python
# In Manim code, add scene markers
# In audio, add pauses between segments
# Use ffmpeg timestamps to sync precisely
```

### 3. Background Music
Add subtle background music to enhance engagement:
```bash
ffmpeg -i visual_silent.mp4 -i narration.mp3 -i background.mp3 \
  -filter_complex "[1:a][2:a]amix=inputs=2:duration=shortest[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac visual.mp4
```

### 4. Dynamic Volume
Lower background music when narration plays:
```bash
# Use ducking: compand filter
```

### 5. Accessibility
Generate captions from narration:
```python
# Use ElevenLabs or Whisper to create .srt files
# Embed in video or provide separately
```

## ✅ Summary

**Before**: Manim videos = silent animations ❌
**Now**: Manim videos = animations + ElevenLabs narration ✅

**Benefits**:
- 🎤 Professional voiceover for all videos
- 📚 Better learning experience (visual + audio)
- ♿ More accessible (audio description of visuals)
- 🌐 Consistent quality across all lessons

**Requirements**:
- ffmpeg installed (for audio-video merging)
- ElevenLabs API key (for narration synthesis)
- Gemini returns narration data in visual variant

**Next Steps**:
1. Test by creating new assignment
2. Verify video has audio stream
3. Validate narration quality
4. Consider multi-voice enhancement

---

**Status**: ✅ Implemented and ready for testing
**Created**: October 4, 2025
**Dependencies**: ffmpeg 7.1.1+, ElevenLabs SDK 2.16.0+
