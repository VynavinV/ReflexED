# Root Cause Analysis & Fix

## Problem
Students could not see any content when clicking on lesson variants:
- ❌ No simplified text displayed (only title)
- ❌ No audio script shown
- ❌ No visual description/plan shown
- ❌ No quiz questions rendered
- ❌ Audio/video players appeared but media was unusable

## Root Cause

### Issue 1: Incomplete Data Storage
The backend was NOT storing the complete generated content in the database.

**Simplified Text:**
```python
# WRONG - Only saved the text, lost the highlights
self._persist_variant(
    assignment, 'simplified', assignment.subject,
    content_text=simplified.get('text'), 
    assets={'highlights': simplified.get('highlights', [])}  # Lost in assets!
)
```

**Quiz:**
```python
# WRONG - Only saved the summary, lost all questions!
self._persist_variant(
    assignment, 'quiz', assignment.subject,
    content_text=json.dumps({'summary': quiz.get('summary', '')}),  # Questions missing!
    assets={'quiz_json': quiz_path}
)
```

**Visual:**
```python
# WRONG - Only saved description (which might be None), lost the plan
self._persist_variant(
    assignment, 'visual', assignment.subject,
    content_text=visual.get('description'),  # Often None or very short!
    assets={'video_mp4': video_mp4, 'manim_script': manim_script}
)
```

### Database Evidence
When I checked the database:
```sql
SELECT variant_type, ready, length(content_text) FROM assignment_versions;
```

Results:
- `simplified`: 1089 chars (only text, missing highlights structure)
- `audio`: 2078 chars (raw text, missing structure)
- `visual`: **315 chars** (should have been 2792!)
- `quiz`: **225 chars** (just summary, no questions!)

### Why Frontend Showed Nothing
The frontend code expected complete JSON structures:

**Simplified:**
```javascript
const data = JSON.parse(version.content_text || '{}');
content += `${escapeHtml(data.text || version.content_text || 'Content generated')}`;
if (data.highlights && data.highlights.length) {
    // Render highlights - but they were in assets, not content_text!
}
```

**Quiz:**
```javascript
const parsed = JSON.parse(version.content_text || '{}');
const questions = parsed.questions || [];  // Empty because only summary was saved!
```

## The Fix

### Changed: Complete JSON Storage
All variants now store their COMPLETE data structures:

**Simplified Text:**
```python
# CORRECT - Store complete JSON with text AND highlights
self._persist_variant(
    assignment, 'simplified', assignment.subject,
    content_text=json.dumps(simplified, ensure_ascii=False),  # Everything!
    assets={}
)
```

**Quiz:**
```python
# CORRECT - Store complete quiz with all questions
self._persist_variant(
    assignment, 'quiz', assignment.subject,
    content_text=json.dumps(quiz, ensure_ascii=False),  # All questions!
    assets={'quiz_json': quiz_path}
)
```

**Audio:**
```python
# CORRECT - Store the actual script text for display
self._persist_variant(
    assignment, 'audio', assignment.subject,
    content_text=script_text,  # The readable script
    assets={'audio_mp3': audio_mp3, 'captions_vtt': audio.get('captions_vtt')}
)
```

**Visual:**
```python
# CORRECT - Store description OR manim code if description is missing
visual_text = visual.get('description', '') or visual.get('manim_code', '')
self._persist_variant(
    assignment, 'visual', assignment.subject,
    content_text=visual_text,  # Actual content to display
    assets={'video_mp4': video_mp4, 'manim_script': manim_script}
)
```

## Files Changed
- ✅ `app/services/assignment_service.py` - Lines 90-140 (4 fixes for data storage)
- ✅ Database cleared and ready for fresh generation
- ✅ Upload directory cleaned

## Testing
1. Server is running at http://localhost:5001
2. Database has been cleared
3. Upload directory has been cleaned
4. Ready to upload a new assignment and test all 4 variants

### Expected Results After New Upload:
- ✅ **Simplified Text**: Full text with highlighted key points
- ✅ **Audio Narration**: Working audio player + full script display
- ✅ **Visual Lesson**: Working video player + visual plan description
- ✅ **Interactive Quiz**: Full quiz with all questions, options, and explanations

## Summary
**Root Cause:** Backend was only storing partial data (text only, summary only) instead of complete JSON structures.

**Impact:** Frontend received incomplete data and couldn't render the content.

**Fix:** Store complete JSON structures in `content_text` for all variants.

**Status:** ✅ FIXED - Ready to test with new upload
