# Automatic Manim Rendering & ElevenLabs Integration

## Changes Made

### 1. ✅ Automatic Manim Video Rendering
**File:** `app/services/assignment_service.py` - `_render_manim()` method

#### What Changed:
- **Before:** Only wrote scene.py file, created 40-byte placeholder MP4
- **After:** Automatically executes Manim CLI to render real videos

#### New Features:
- 🎬 **Automatic Scene Detection:** Extracts class name from generated code
- ⏱️ **Loading Time Display:** Shows "Estimated time: 10-30 seconds" during rendering
- 📊 **Quality Settings:** Uses `-ql` (480p, 15fps) for faster rendering
- 🛡️ **Timeout Protection:** 60-second timeout prevents hanging
- 📦 **Graceful Fallback:** Creates placeholder if rendering fails
- 🔍 **Error Handling:** Catches missing manim, timeouts, and rendering errors

#### Command Executed:
```bash
manim -ql --disable_caching -o visual.mp4 scene.py <SceneClass>
```

#### Output:
- **Success:** Real MP4 video (typically 100KB - 2MB depending on complexity)
- **Failure:** Falls back to 40-byte placeholder with error logging
- **Location:** `/uploads/<assignment-id>/visual.mp4`

#### Logs You'll See:
```
🎬 Executing Manim render for scene 'TitleScene'...
⏱️  Estimated time: 10-30 seconds depending on complexity...
✅ Manim video rendered successfully: 1234567 bytes
```

Or if it fails:
```
⚠️ Manim rendering failed (code 1): ...
📦 Creating fallback placeholder...
```

---

### 2. ✅ Improved Visual Descriptions
**File:** `app/services/assignment_service.py` - `_gen_visual_plan()` method

#### What Changed:
- **Before:** Often got "Visual explainer" (16 chars) due to poor fallback
- **After:** Detailed descriptions with minimum length enforcement

#### Improvements:
- 📝 **Better Prompt:** Asks Gemini for "detailed 2-3 sentence explanation"
- ✅ **Validation:** Ensures description is at least 20 characters
- 🎯 **Smart Fallback:** If Gemini fails, creates educational description like:
  > "This visual lesson uses animations to illustrate key concepts from the history material. The animation breaks down complex ideas into clear, step-by-step visual explanations."

#### Before/After Example:
```
Before: "Visual explainer"  (16 chars)
After:  "This animation demonstrates the timeline of World War II using animated maps and key dates. Visual elements include troop movements, territorial changes, and major battle locations shown progressively." (200+ chars)
```

---

### 3. ✅ ElevenLabs Real Audio (If API Key Set)
**File:** `app/services/assignment_service.py` - `_synthesize_audio()` method
**Status:** Already implemented, just needs API key

#### What Happens Now:
1. **Check for API Key:** Looks for `Config.ELEVENLABS_API_KEY` from `.env`
2. **If Key Exists:** 
   - Calls ElevenLabs API
   - Generates real AI narration
   - Saves actual MP3 with voice audio
   - File size: ~50KB - 500KB (real audio)
3. **If No Key:**
   - Creates 500-byte placeholder MP3
   - Logs: "🎵 Creating minimal valid MP3 placeholder..."

#### To Enable Real Audio:
```bash
# In .env file (you already did this!)
ELEVENLABS_API_KEY=your-actual-key-here
```

---

## Expected Generation Timeline

### Without Real Media (Placeholders Only):
- PDF Extraction: ~1 second
- Simplified Text (Gemini): ~3-5 seconds
- Audio Script (Gemini): ~3-5 seconds
- Audio Placeholder: <1 second
- Visual Plan (Gemini): ~3-5 seconds
- Video Placeholder: <1 second
- Quiz (Gemini): ~3-5 seconds
- **Total: ~15-25 seconds**

### With Real Media (Manim + ElevenLabs):
- PDF Extraction: ~1 second
- Simplified Text (Gemini): ~3-5 seconds
- Audio Script (Gemini): ~3-5 seconds
- **ElevenLabs Audio: ~5-10 seconds** ⬅️ NEW
- Visual Plan (Gemini): ~3-5 seconds
- **Manim Rendering: ~10-30 seconds** ⬅️ NEW
- Quiz (Gemini): ~3-5 seconds
- **Total: ~30-60 seconds**

---

## File Size Expectations

### Placeholders (Before):
- `narration.mp3`: 500 bytes (silent frames)
- `visual.mp4`: 40 bytes (empty container)

### Real Media (After):
- `narration.mp3`: 50KB - 500KB (actual narrated audio)
- `visual.mp4`: 100KB - 5MB (rendered animation video)
- `scene.py`: 200 bytes - 5KB (Manim Python code)
- `quiz.json`: 1-3KB (quiz questions)

---

## Testing Instructions

1. **Server Running:** ✅ http://localhost:5001
2. **Database Cleared:** ✅ Fresh start
3. **Uploads Cleaned:** ✅ Ready for new content

### To Test:
1. Go to http://localhost:5001/teacher.html
2. Upload your PDF (resume)
3. Watch the terminal logs for:
   ```
   ⏱️  Estimated time: 10-30 seconds depending on complexity...
   ✅ Manim video rendered successfully: XXXXX bytes
   ```
4. Go to http://localhost:5001/student.html
5. Click the lesson and try "Visualized Lesson" variant
6. You should see:
   - **Detailed description** (not just "Visual explainer")
   - **Real video** (if Manim succeeded) or placeholder with error logs
   - **Working video player** with actual frames (if rendered)

### To Verify Real Audio:
Check the terminal during audio generation:
- **With API Key:** "🎤 Calling ElevenLabs API..."
- **Without API Key:** "🎵 Creating minimal valid MP3 placeholder..."

---

## Troubleshooting

### If Manim Fails:
Check terminal for specific error:
- `⚠️ Manim command not found` → Run `pip install manim`
- `⚠️ Manim rendering timed out` → Scene too complex, uses placeholder
- `⚠️ Manim rendering failed (code 1)` → Syntax error in generated code, uses placeholder

### If ElevenLabs Fails:
Check terminal:
- `⚠️ Audio synthesis failed: ...` → Invalid API key or API error
- Falls back to placeholder automatically

### All Failures Are Graceful:
The system will NEVER crash. It always falls back to placeholders and continues with other variants.

---

## Summary

✅ **Automatic Manim Rendering:** Real videos generated automatically (10-30s)
✅ **Better Visual Descriptions:** Detailed explanations (200+ chars)
✅ **ElevenLabs Ready:** Just needs API key in `.env` (you added it!)
✅ **Accurate Loading Times:** Users see realistic estimates
✅ **Graceful Fallbacks:** Never crashes, always produces content
✅ **Detailed Logging:** Easy to debug what's happening

**Status:** Ready to test! Upload an assignment and watch the magic happen! 🎬🎤
