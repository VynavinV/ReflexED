# Video Generation Retry Logic - Enhancement

## 🎯 Problem Fixed

**Issues observed:**
1. Manim rendering fails mid-animation (e.g., 27% complete then crashes)
2. ffmpeg tries to process invalid placeholder videos, causing exit code 183
3. No retry mechanism when video generation fails

## 🔧 Changes Implemented

### 1. Retry Loop for Visual Generation (Up to 2 Attempts)

**Location**: `app/services/assignment_service.py` lines 202-254

```python
# Try up to 2 times to generate a valid visual plan and video
for attempt in range(2):
    print(f"🎬 Visual generation attempt {attempt + 1}/2...")
    
    visual = self._gen_visual_plan(assignment.subject, base_text)
    
    # Generate narration audio
    narration_segments = visual.get('narration', [])
    if narration_segments:
        full_narration = ' '.join(seg.get('text', '') for seg in narration_segments)
        narration_audio = self._synthesize_audio(full_narration, ...)
    
    # Render Manim video (returns success flag now)
    video_mp4, manim_script, success = self._render_manim(...)
    
    # Check if we got a valid video (not a placeholder)
    if success and os.path.getsize(video_mp4) > 10000:
        print(f"✅ Valid video generated on attempt {attempt + 1}")
        break
    else:
        print(f"⚠️ Attempt {attempt + 1} failed, retrying with new script...")
```

**Behavior:**
- Attempt 1: Generate Gemini visual plan → Render with Manim
- If fails: Attempt 2: Generate NEW Gemini visual plan → Render with Manim
- If both fail: Use placeholder video + separate narration audio

### 2. Enhanced Manim Rendering with Success Flag

**Changed return type**: `Tuple[str, str]` → `Tuple[str, str, bool]`

```python
def _render_manim(...) -> Tuple[str, str, bool]:
    # ... rendering logic ...
    
    if successful:
        return video_path, script_path, True  # Real video
    else:
        return video_path, script_path, False  # Placeholder
```

### 3. Smart ffmpeg Processing (Skip Invalid Videos)

**Location**: `_add_audio_to_video()` method

```python
# Check if video file is valid (not a tiny placeholder)
video_size = os.path.getsize(video_path)
if video_size < 10000:  # Less than 10KB = placeholder
    print(f"⚠️ Video too small ({video_size} bytes), skipping ffmpeg.")
    return video_path

# Only process valid videos
print(f"🎬 Combining video ({video_size} bytes) with audio...")
result = subprocess.run(['ffmpeg', ...])
```

**Behavior:**
- Valid video (>10KB): Combine with audio using ffmpeg
- Placeholder (<10KB): Skip ffmpeg, keep placeholder separate from audio

## 🎬 New Workflow

### Successful Generation
```
Attempt 1:
  🎬 Generating visual plan with Gemini... ✅
  🎤 Synthesizing narration audio... ✅ 847KB
  🎬 Rendering Manim video... ✅ 678KB
  ✅ Valid video generated on attempt 1
  🎬 Combining video with audio via ffmpeg... ✅ 1.2MB
  ✅ Visual variant created
```

### First Attempt Fails → Retry Success
```
Attempt 1:
  🎬 Generating visual plan with Gemini... ✅
  🎤 Synthesizing narration audio... ✅ 850KB
  🎬 Rendering Manim video... ❌ Failed at 27%
  ⚠️ Attempt 1 failed, retrying with new script...

Attempt 2:
  🎬 Generating NEW visual plan with Gemini... ✅
  🎤 Synthesizing narration audio... ✅ 820KB (new)
  🎬 Rendering Manim video... ✅ 650KB
  ✅ Valid video generated on attempt 2
  🎬 Combining video with audio via ffmpeg... ✅ 1.1MB
  ✅ Visual variant created
```

### Both Attempts Fail → Graceful Fallback
```
Attempt 1:
  🎬 Generating visual plan with Gemini... ✅
  🎤 Synthesizing narration audio... ✅ 840KB
  🎬 Rendering Manim video... ❌ Failed
  ⚠️ Attempt 1 failed, retrying with new script...

Attempt 2:
  🎬 Generating NEW visual plan with Gemini... ✅
  🎤 Synthesizing narration audio... ✅ 835KB (new)
  🎬 Rendering Manim video... ❌ Failed
  ⚠️ Attempt 2 failed, using placeholder

  ⚠️ Video is placeholder (500 bytes), skipping ffmpeg
  ✅ Visual variant created (placeholder video + narration.mp3)
```

## 📋 Key Improvements

### 1. **Automatic Retry**
- System tries 2 different Gemini-generated scripts
- Each attempt gets fresh Manim code from Gemini
- Increases chance of successful video generation

### 2. **No More ffmpeg Errors on Placeholders**
- Validates video size before ffmpeg processing
- Placeholder videos (<10KB) skip ffmpeg entirely
- Prevents "exit code 183" errors

### 3. **Separate Audio for Fallback**
- Even if video fails, narration audio is saved
- Students can still listen to lesson audio
- Better than complete failure

### 4. **Better Logging**
- Shows attempt numbers (1/2, 2/2)
- Reports video file sizes
- Clear success/failure messages

## 🔍 Validation Logic

### Valid Video Check
```python
success = (
    manim_returncode == 0 AND
    video_file_exists AND
    file_size > 10000  # More than 10KB
)
```

### ffmpeg Processing Check
```python
should_combine_audio = (
    narration_audio_exists AND
    video_file_exists AND
    video_size > 10000  # Not a placeholder
)
```

## 📊 Expected Logs (New Assignment)

```
🎬 Generating visual/Manim variant...
🎬 Visual generation attempt 1/2...
🎬 Creating visual plan for math...
🤖 Calling Gemini API (attempt 1/2)...
✅ Gemini response received (3238 chars)
🎬 Visual plan generated: 228 chars description, 1999 chars code
🎤 Generating narration audio from 4 segments...
🔊 Synthesizing audio: 737 chars of script
🎤 Calling ElevenLabs API...
✅ Audio synthesized: 847666 bytes
🎬 Rendering Manim animation: 1999 chars of code
📝 Manim script written to .../scene.py
🎬 Executing Manim render for scene 'PolynomialLesson'...
⏱️  Estimated time: 10-30 seconds depending on complexity...

[If successful]
✅ Manim video rendered successfully: 678191 bytes
✅ Valid video generated on attempt 1
🎬 Combining video (.../visual_silent.mp4, 678191 bytes) with audio...
✅ Video and audio combined successfully: 1245000 bytes
✅ Visual variant created

[If failed, retry]
⚠️ Manim rendering failed (code 1): ...
📦 Creating fallback placeholder...
✅ Placeholder video created: .../visual_silent.mp4
⚠️ Attempt 1 failed, retrying with new script...

🎬 Visual generation attempt 2/2...
🎬 Creating visual plan for math...
[... attempt 2 continues ...]
```

## 🐛 Error Handling

### Scenario 1: Manim Crashes Mid-Render
- **Before**: Single attempt, fails completely
- **Now**: Retry with different Gemini script

### Scenario 2: ffmpeg Exit Code 183
- **Before**: Tries to process 500-byte placeholder, fails
- **Now**: Detects placeholder (<10KB), skips ffmpeg

### Scenario 3: Both Attempts Fail
- **Before**: Placeholder video, no audio context
- **Now**: Placeholder video + narration.mp3 available separately

## ✅ Testing Recommendations

### Test Case 1: Normal Success
1. Create math assignment
2. Wait for generation
3. Check logs for "attempt 1" success
4. Verify video has audio in student view

### Test Case 2: Force Retry
1. Create complex math assignment (long formulas)
2. Watch logs for potential retry
3. Verify attempt 2 succeeds
4. Check final video quality

### Test Case 3: Complete Fallback
1. If both attempts fail (rare)
2. Verify narration.mp3 exists
3. Check placeholder video doesn't crash student view
4. Audio should still be available

## 📁 Files Modified

- `app/services/assignment_service.py`
  - Lines 202-254: Visual generation with retry loop
  - Lines 620-625: Manim return type changed (added success flag)
  - Lines 641-645: Return success=True for real videos
  - Lines 660-675: Return success=False for placeholders
  - Lines 710-728: ffmpeg validation (skip placeholders <10KB)

## 🚀 Benefits

1. **Higher Success Rate**: 2 attempts instead of 1
2. **No ffmpeg Errors**: Validates video before processing
3. **Better UX**: Even failures provide narration audio
4. **Clear Diagnostics**: Logs show which attempt succeeded
5. **Automatic Recovery**: System tries different approaches

---

**Status**: ✅ Implemented and ready for testing
**Impact**: Reduces video generation failures by ~50% (estimated)
**Fallback**: Always provides audio even if video fails
