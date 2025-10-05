# Quick Testing Guide for PolyLearn Enhancements

## 🚀 Quick Start

1. **Server Running**: http://127.0.0.1:5001
2. **Teacher Dashboard**: http://127.0.0.1:5001/teacher.html
3. **Student Portal**: http://127.0.0.1:5001/student.html

---

## ✅ Test Scenarios

### Test 1: Math Lesson with Practice Problems
```
1. Go to Teacher Dashboard
2. Enter text: "Solve linear equations: 2x + 5 = 15, then solve 3(x-2) = 9"
3. Select Subject: "math"
4. Click "Generate Materials"
5. Wait 30-60 seconds
6. Click "Preview" on any generated material

Expected Results:
- 🎙️ Audio: Podcast discussion explaining equations
- 🎬 Visual: Animated video showing step-by-step solutions
- 🧠 Quiz: Practice problems with difficulty levels and solutions
```

### Test 2: History Lesson with Timeline
```
1. Enter text: "World War II: 1939 Germany invades Poland, 1941 Pearl Harbor attacked, 1945 War ends. Key figures: Winston Churchill, Franklin Roosevelt"
2. Select Subject: "history"
3. Generate and preview

Expected Results:
- 🎙️ Audio: Host & Expert discuss WWII events
- 🎬 Visual: Animated timeline or battle scenes  
- 🧠 Quiz: Timeline events + Famous people fill-in-the-blanks
```

### Test 3: Language Lesson with Socratic Questions
```
1. Enter text: "French past tense: passé composé vs imparfait. Example: J'ai mangé (I ate) vs Je mangeais (I was eating)"
2. Select Subject: "language"
3. Generate and preview

Expected Results:
- 🎙️ Audio: Conversational explanation of grammar
- 🎬 Visual: Animated examples with translations
- 🧠 Quiz: Guided questions to discover grammar rules
```

### Test 4: Science Lesson with Practice Questions
```
1. Enter text: "Photosynthesis: Plants convert CO2 + H2O + sunlight into glucose and oxygen. Chlorophyll in chloroplasts captures light energy"
2. Select Subject: "science"
3. Generate and preview

Expected Results:
- 🎙️ Audio: Discussion about photosynthesis process
- 🎬 Visual: Animated cellular process
- 🧠 Quiz: Repeatable practice questions with real-world examples
```

### Test 5: Geography Lesson
```
1. Enter text: "The Amazon Rainforest spans 9 countries, produces 20% of Earth's oxygen, contains the Amazon River (6,400 km long)"
2. Select Subject: "geography"
3. Generate and preview

Expected Results:
- 🎙️ Audio: Geographic discussion about the Amazon
- 🎬 Visual: Animated map showing rainforest extent
- 🧠 Quiz: Practice questions with interesting facts
```

---

## 🎯 What to Look For

### ✅ Audio (Podcast) Checklist:
- [ ] Two different speakers (Host & Expert)
- [ ] Color-coded transcript (blue for Host, purple for Expert)
- [ ] Natural conversation, not word-for-word reading
- [ ] Audio player controls work
- [ ] Discussion teaches concepts through dialogue

### ✅ Visual (Video) Checklist:
- [ ] Video player displays
- [ ] Narration timeline shows below video
- [ ] Each narration segment has duration
- [ ] Description explains what video teaches
- [ ] Video is more than 3 seconds (if Manim renders)

### ✅ Quiz Checklist by Subject:

**Math:**
- [ ] Shows "Practice Problems" title
- [ ] Problems have difficulty badges (easy/medium/hard)
- [ ] "Show Solution" reveals step-by-step answers
- [ ] Common mistakes section appears

**History:**
- [ ] Shows "Timeline & Historical Figures" title
- [ ] Year badges displayed for events
- [ ] Fill-in-the-blank format
- [ ] Famous people section with significance

**Language:**
- [ ] Shows "Guided Learning Questions" title
- [ ] Questions guide discovery, not test knowledge
- [ ] Guidance section with thinking prompts
- [ ] Textarea for student responses

**Science:**
- [ ] Shows "Practice Exercise" title
- [ ] Input fields for answers
- [ ] Hints available
- [ ] "Did you know?" facts included

**Geography:**
- [ ] Shows "Practice Exercise" title
- [ ] Similar to science format
- [ ] Interesting geographical facts

---

## 🐛 Common Issues & Fixes

### Issue: "Quiz shows placeholder text"
**Cause**: Old browser cache
**Fix**: Hard refresh (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

### Issue: "Audio is placeholder/silent"
**Cause**: No ElevenLabs API key configured
**Status**: Expected behavior - system creates minimal MP3 placeholder
**Note**: For real audio, add ELEVENLABS_API_KEY to environment

### Issue: "Video is very short"
**Cause**: Manim failed to render or timed out
**Status**: Expected behavior - system creates MP4 placeholder
**Note**: Check terminal output for Manim errors

### Issue: "Generation takes too long"
**Cause**: Gemini API calls + processing time
**Expected**: 30-90 seconds for full generation
**Tip**: Watch progress bar and terminal output

---

## 📊 Success Criteria

### Minimum for Demo:
- ✅ All 4 variants generate without errors
- ✅ Quiz displays properly (not placeholder text)
- ✅ Audio shows podcast transcript
- ✅ Video shows narration timeline
- ✅ Different quiz types for different subjects

### Ideal for Demo:
- ✅ Real audio with 2 voices (requires API key)
- ✅ Full Manim-rendered videos (requires Manim installed)
- ✅ All content AI-generated and educational
- ✅ Smooth UI with no errors in console

---

## 💡 Demo Tips

1. **Pre-generate content**: Create lessons before demo to avoid waiting
2. **Show variety**: Demo different subjects to showcase quiz types
3. **Highlight podcast**: Open audio transcript to show 2-voice conversation
4. **Show narration**: Expand video narration timeline
5. **Interactive**: Try the quiz yourself to show interactivity

---

## 📝 Quick Debug Commands

```bash
# Check server status
curl http://127.0.0.1:5001/api/assignments

# View server logs
tail -f terminal_output.log

# Test Gemini API
curl http://127.0.0.1:5001/api/test/gemini

# Check database
sqlite3 instance/polylearn.db "SELECT id, title, subject, status FROM assignment;"
```

---

## 🎬 Demo Script

1. **Open Teacher Dashboard**
   - "Let me create a math lesson about algebra"
   
2. **Enter Content**
   - Type: "Linear equations: 2x + 5 = 15"
   - Select: Math
   
3. **Generate**
   - Click "Generate Materials"
   - "The AI is now creating 4 different learning versions"
   
4. **Show Results**
   - Audio: "Notice the podcast format with two speakers discussing concepts"
   - Video: "Here's the narration timeline tied to the visuals"
   - Quiz: "Math gets practice problems with solutions and difficulty levels"
   
5. **Show Another Subject**
   - History: "Timeline format with historical events and figures"
   - Language: "Socratic questions that guide learning"

---

**Status**: Ready for testing! 🎉
**Server**: http://127.0.0.1:5001
**All features implemented and functional**
