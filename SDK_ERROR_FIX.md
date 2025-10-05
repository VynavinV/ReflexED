# Quick Fix: response_mime_type Error

## ❌ Error Encountered
```
ValueError: Unknown field for GenerationConfig: response_mime_type
```

## 🔍 Root Cause
The `response_mime_type` parameter is **not supported** in the current version of the Google Generative AI SDK being used in this project.

This parameter was added in newer versions of the SDK, but your environment is using an older version that doesn't recognize it.

## ✅ Fix Applied
Removed the `response_mime_type` parameter from the quiz model configuration:

**Before (caused error):**
```python
self.model_quiz = genai.GenerativeModel(
    "gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json"  # ❌ Not supported
    }
)
```

**After (fixed):**
```python
self.model_quiz = genai.GenerativeModel(
    "gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 8192
        # Note: response_mime_type not supported in current SDK version
    }
)
```

## 📊 Impact
The quiz generation will still work well because:
1. ✅ **Better model** - Using `gemini-2.0-flash-exp` (designed for structured output)
2. ✅ **Lower temperature** - 0.3 (more deterministic and consistent)
3. ✅ **Enhanced prompts** - Explicit JSON formatting instructions
4. ✅ **Better parser** - Unicode character handling and error recovery

## 🧪 Test Now
The server is already running, so just:
1. **Refresh** the teacher page
2. **Create a new assignment** with math content
3. Watch the logs - quiz generation should now complete successfully!

## 📈 Expected Results
```
🧠 Creating quiz for math with difficulty=medium...
🤖 Calling Gemini API (attempt 1/2)...
✅ Gemini response received (XXXX chars)
✅ Successfully parsed JSON with XXXX chars
🧠 Quiz generated: practice format with 8-10 items  ← SUCCESS!
```

## 🔄 Optional: Upgrade SDK (Future)
If you want to use `response_mime_type` in the future, upgrade the SDK:
```bash
pip install --upgrade google-generativeai
```

But for now, the current setup should work fine without it!

---

**The error is fixed!** You can now create assignments without the SDK error. 🎉
