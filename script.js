// ==================== GLOBAL STATE ====================
const state = {
    currentPage: document.body.dataset.page || 'landing',
    uploadedFile: null,
    selectedSubject: null,
    isGenerating: false,
    audioPlaying: false,
    audioProgress: 0,
    theme: 'light',
    fontSize: 'medium',
    readingSpeed: 'normal',
    language: 'en',
    preferences: {}
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    loadPreferences();
    setupEventListeners();
});

function initializeApp() {
    // Apply saved preferences
    applyPreferences();
    
    // Set active nav link based on current page
    updateActiveNavLink();
}

// ==================== PREFERENCES MANAGEMENT ====================
function loadPreferences() {
    const saved = localStorage.getItem('polylearn-preferences');
    if (saved) {
        state.preferences = JSON.parse(saved);
        state.theme = state.preferences.theme || 'light';
        state.fontSize = state.preferences.fontSize || 'medium';
        state.readingSpeed = state.preferences.readingSpeed || 'normal';
        state.language = state.preferences.language || 'en';
    }
}

function savePreferences() {
    state.preferences = {
        theme: state.theme,
        fontSize: state.fontSize,
        readingSpeed: state.readingSpeed,
        language: state.language
    };
    localStorage.setItem('polylearn-preferences', JSON.stringify(state.preferences));
}

function applyPreferences() {
    // Apply theme
    document.body.setAttribute('data-theme', state.theme);
    
    // Apply font size
    document.body.setAttribute('data-font-size', state.fontSize);
    
    // Update UI to reflect current settings
    updateAccessibilityUI();
}

function updateAccessibilityUI() {
    // Update theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === state.theme);
    });
    
    // Update size buttons
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.size === state.fontSize);
    });
    
    // Update speed buttons
    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.speed === state.readingSpeed);
    });
    
    // Update language select
    const langSelect = document.getElementById('language-select');
    if (langSelect) {
        langSelect.value = state.language;
    }
}

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
    // Teacher Dashboard (only on teacher page)
    if (state.currentPage === 'teacher') {
        setupTeacherDashboardListeners();
    }
    
    // Student Portal (only on student page)
    if (state.currentPage === 'student') {
        setupStudentPortalListeners();
    }
    
    // Accessibility Settings
    setupAccessibilityListeners();
    
    // Modals
    setupModalListeners();
    
    // Mobile Menu
    setupMobileMenuListener();
}

// ==================== NAVIGATION ====================
function updateActiveNavLink() {
    const currentPage = state.currentPage;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href) {
            const pageName = href.replace('.html', '');
            const isActive = pageName === currentPage || (pageName === 'index' && currentPage === 'landing');
            link.classList.toggle('active', isActive);
            link.setAttribute('aria-current', isActive ? 'page' : 'false');
        }
    });
}

// ==================== MOBILE MENU ====================
function setupMobileMenuListener() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
            navLinks.classList.toggle('mobile-active');
        });
    }
}

// ==================== TEACHER DASHBOARD ====================
function setupTeacherDashboardListeners() {
    // File upload
    setupFileUploadListeners();
    
    // Generate button
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateMaterials);
    }
    
    // Material preview buttons
    document.querySelectorAll('[data-preview]').forEach(btn => {
        btn.addEventListener('click', () => {
            showMaterialPreview(btn.dataset.preview);
        });
    });
    
    // Load recent lessons on page load
    loadRecentLessons();
}

async function loadRecentLessons() {
    const lessonsList = document.querySelector('.lessons-list');
    if (!lessonsList) return;
    
    try {
        const response = await fetch('/api/assignments');
        
        if (!response.ok) {
            console.warn('Could not load assignments');
            return;
        }
        
        const assignments = await response.json();
        
        if (assignments.length === 0) {
            lessonsList.innerHTML = '<p style="text-align: center; color: var(--gray-600); padding: 40px;">No lessons created yet. Upload your first assignment above!</p>';
            return;
        }
        
        lessonsList.innerHTML = assignments.slice(0, 10).map(a => {
            const subjectClass = a.subject || 'science';
            const statusBadge = a.status === 'ready' ? '✅ Ready' : a.status === 'generating' ? '⏳ Generating...' : '❌ Failed';
            const daysAgo = Math.floor((Date.now() - new Date(a.created_at).getTime()) / (1000 * 60 * 60 * 24));
            const timeText = daysAgo === 0 ? 'Today' : daysAgo === 1 ? '1 day ago' : `${daysAgo} days ago`;
            
            return `
                <div class="lesson-item">
                    <div class="lesson-info">
                        <span class="lesson-subject ${subjectClass}">${a.subject}</span>
                        <h3>${escapeHtml(a.title)}</h3>
                        <p>${timeText} • ${statusBadge}</p>
                    </div>
                    <div class="lesson-actions">
                        <button class="btn btn-outline btn-sm" onclick="viewAssignment('${a.id}')">View</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Failed to load recent lessons:', error);
    }
}

async function viewAssignment(assignmentId) {
    try {
        const response = await fetch(`/api/assignments/${assignmentId}`);
        
        if (!response.ok) {
            alert('Could not load assignment details');
            return;
        }
        
        const assignment = await response.json();
        state.currentAssignment = assignment;
        
        // Show generated materials section if not visible
        const materialsSection = document.getElementById('generated-materials');
        if (materialsSection) {
            materialsSection.style.display = 'block';
            materialsSection.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Failed to view assignment:', error);
        alert('Error loading assignment');
    }
}

function switchTab(tabName) {
    // This function is no longer needed as we use separate pages
    // Keeping it for backwards compatibility
}

// ==================== FILE UPLOAD ====================
function setupFileUploadListeners() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const removeBtn = document.getElementById('remove-file');
    const subjectSelect = document.getElementById('subject-select');
    
    // Browse button
    if (browseBtn && fileInput) {
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }
    
    // Upload area click
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Keyboard support
        uploadArea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });
    }
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleFileSelect(e.target.files[0]);
        });
    }
    
    // Drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            handleFileSelect(e.dataTransfer.files[0]);
        });
    }
    
    // Remove file
    if (removeBtn) {
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            clearUploadedFile();
        });
    }
    
    // Lesson text input
    const lessonTextInput = document.getElementById('lesson-text');
    if (lessonTextInput) {
        lessonTextInput.addEventListener('input', () => {
            updateGenerateButton();
        });
    }
    
    // Subject select
    if (subjectSelect) {
        subjectSelect.addEventListener('change', (e) => {
            state.selectedSubject = e.target.value;
            updateGenerateButton();
            
            // Show/hide language info banner
            const languageBanner = document.getElementById('language-info-banner');
            if (languageBanner) {
                if (e.target.value === 'language') {
                    languageBanner.style.display = 'block';
                } else {
                    languageBanner.style.display = 'none';
                }
            }
        });
    }
}

function handleFileSelect(file) {
    if (!file) return;
    
    state.uploadedFile = file;
    
    // Update UI
    document.getElementById('upload-area').style.display = 'none';
    document.getElementById('file-info').style.display = 'block';
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    
    updateGenerateButton();
}

function clearUploadedFile() {
    state.uploadedFile = null;
    
    // Reset file input
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
    
    // Update UI
    document.getElementById('upload-area').style.display = 'flex';
    document.getElementById('file-info').style.display = 'none';
    
    updateGenerateButton();
}

function updateGenerateButton() {
    const generateBtn = document.getElementById('generate-btn');
    const lessonText = document.getElementById('lesson-text');
    if (generateBtn) {
        const hasFileOrText = state.uploadedFile || (lessonText && lessonText.value.trim());
        generateBtn.disabled = !(hasFileOrText && state.selectedSubject);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ==================== MATERIAL GENERATION ====================
async function generateMaterials() {
    if (state.isGenerating) return;
    
    state.isGenerating = true;
    state.currentAssignmentId = null;
    
    // Hide upload area, show loading
    document.getElementById('upload-container')?.scrollIntoView({ behavior: 'smooth' });
    document.getElementById('loading-container').style.display = 'block';
    
    // Build form data
    const formData = new FormData();
    
    // Get lesson text if provided
    const lessonTextInput = document.getElementById('lesson-text');
    const lessonText = lessonTextInput ? lessonTextInput.value.trim() : '';
    
    // Get title from file name or generate one
    const title = state.uploadedFile ? state.uploadedFile.name.replace(/\.[^/.]+$/, '') : `${state.selectedSubject} Lesson ${Date.now()}`;
    formData.append('title', title);
    formData.append('subject', state.selectedSubject);
    
    if (state.uploadedFile) {
        formData.append('file', state.uploadedFile);
    }
    
    if (lessonText) {
        formData.append('text', lessonText);
    }
    
    // Progress simulation
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 8;
        if (progress > 90) progress = 90; // Cap at 90% until real completion
        
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill) progressFill.style.width = progress + '%';
        if (progressText) progressText.textContent = Math.round(progress) + '%';
    }, 500);
    
    try {
        // Call API to create assignment (this will generate all variants)
        const response = await fetch('/api/assignments/create', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create assignment: ${response.statusText}`);
        }
        
        const assignment = await response.json();
        state.currentAssignmentId = assignment.id;
        
        // Complete progress
        clearInterval(progressInterval);
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = '100%';
        
        setTimeout(() => showGeneratedMaterials(assignment), 500);
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Generation error:', error);
        alert('Failed to generate materials. Please check your API configuration and try again.');
        state.isGenerating = false;
        document.getElementById('loading-container').style.display = 'none';
    }
}

function showGeneratedMaterials(assignment) {
    state.isGenerating = false;
    
    // Hide loading, show results
    document.getElementById('loading-container').style.display = 'none';
    document.getElementById('generated-materials').style.display = 'block';
    
    // Store assignment for preview
    state.currentAssignment = assignment;
    
    // Scroll to results
    document.getElementById('generated-materials')?.scrollIntoView({ behavior: 'smooth' });
    
    // Reload recent lessons
    if (typeof loadRecentLessons === 'function') {
        loadRecentLessons();
    }
}

// ==================== MATERIAL PREVIEW MODAL ====================
function showMaterialPreview(materialType) {
    const modal = document.getElementById('material-modal');
    const modalTitle = document.getElementById('material-modal-title');
    const modalBody = document.getElementById('material-modal-body');
    
    // If we have a real assignment, show its content
    if (state.currentAssignment && state.currentAssignment.versions) {
        const version = state.currentAssignment.versions.find(v => v.variant_type === materialType);
        if (version && version.ready) {
            showRealMaterialPreview(modalTitle, modalBody, modal, materialType, version);
            return;
        }
    }
    
    const materials = {
        simplified: {
            title: 'Simplified Text Version',
            content: `
                <h3>Easy-to-Read Lesson</h3>
                <p style="font-size: 18px; line-height: 1.8;">
                    This is a simplified version of your lesson. The text has been rewritten 
                    to use simpler words and shorter sentences. This makes it easier for younger 
                    students or those learning English to understand.
                </p>
                <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin-top: 20px;">
                    <h4>Key Concepts:</h4>
                    <ul style="font-size: 16px; line-height: 2;">
                        <li>Clear explanations</li>
                        <li>Simple vocabulary</li>
                        <li>Short paragraphs</li>
                        <li>Visual aids included</li>
                    </ul>
                </div>
            `
        },
        audio: {
            title: 'Audio Narration Version',
            content: `
                <h3>Narrated Lesson</h3>
                <p>This version includes a full audio narration of the lesson content. Students can listen while reading or on its own.</p>
                <div style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); color: white; padding: 30px; border-radius: 12px; margin-top: 20px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 15px;">🎧</div>
                    <h4>Audio Features:</h4>
                    <ul style="list-style: none; padding: 0; font-size: 16px; line-height: 2;">
                        <li>✓ Professional narration</li>
                        <li>✓ Adjustable playback speed</li>
                        <li>✓ Multiple voice options</li>
                        <li>✓ Synchronized highlighting</li>
                    </ul>
                </div>
                <p style="margin-top: 20px; font-style: italic; color: var(--gray-600);">
                    Powered by ElevenLabs AI voice technology
                </p>
            `
        },
        visual: {
            title: 'Visualized Lesson (Manim Mode)',
            content: `
                <h3>Animated Visual Explanation</h3>
                <p>This version transforms the lesson into step-by-step visual animations, perfect for visual learners.</p>
                <div style="background: var(--math-green); color: white; padding: 30px; border-radius: 12px; margin-top: 20px;">
                    <div style="font-size: 48px; margin-bottom: 15px; text-align: center;">🎨</div>
                    <h4>Visual Elements Include:</h4>
                    <ul style="font-size: 16px; line-height: 2;">
                        <li>📊 Animated diagrams and charts</li>
                        <li>🔄 Step-by-step transformations</li>
                        <li>🎯 Highlighted key concepts</li>
                        <li>📐 Interactive visualizations</li>
                    </ul>
                </div>
                <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin-top: 20px; text-align: center;">
                    <p style="margin: 0; font-style: italic;">Manim-style animations make complex concepts easier to understand</p>
                </div>
            `
        },
        quiz: {
            title: 'Interactive Quiz Mode',
            content: `
                <h3>Gamified Learning Experience</h3>
                <p>This version transforms the lesson into an interactive quiz with questions, challenges, and instant feedback.</p>
                <div style="background: var(--geography-purple); color: white; padding: 30px; border-radius: 12px; margin-top: 20px;">
                    <div style="font-size: 48px; margin-bottom: 15px; text-align: center;">🎯</div>
                    <h4>Quiz Features:</h4>
                    <ul style="font-size: 16px; line-height: 2;">
                        <li>❓ Multiple choice questions</li>
                        <li>✅ Instant feedback</li>
                        <li>🏆 Points and achievements</li>
                        <li>📈 Progress tracking</li>
                    </ul>
                </div>
                <div style="margin-top: 20px; padding: 20px; background: var(--gray-50); border-radius: 8px;">
                    <h4 style="margin-bottom: 10px;">Sample Question:</h4>
                    <p style="font-weight: 600; margin-bottom: 15px;">What is the main topic of this lesson?</p>
                    <div style="display: grid; gap: 10px;">
                        <button class="btn btn-outline" style="text-align: left;">A) Option 1</button>
                        <button class="btn btn-outline" style="text-align: left;">B) Option 2</button>
                        <button class="btn btn-outline" style="text-align: left;">C) Option 3</button>
                    </div>
                </div>
            `
        }
    };
    
    const material = materials[materialType];
    if (material && modal && modalTitle && modalBody) {
        modalTitle.textContent = material.title;
        modalBody.innerHTML = material.content;
        modal.classList.add('active');
    }
}

function showRealMaterialPreview(modalTitle, modalBody, modal, materialType, version) {
    const typeNames = {
        simplified: 'Simplified Text Version',
        audio: 'Audio Narration Version',
        visual: 'Visualized Lesson (Manim)',
        quiz: 'Interactive Quiz'
    };
    
    modalTitle.textContent = typeNames[materialType] || 'Material Preview';
    
    let content = '<h3>Generated Content</h3>';
    
    if (materialType === 'simplified') {
        try {
            const data = JSON.parse(version.content_text || '{}');
            content += `<div style="font-size: 18px; line-height: 1.8; margin-bottom: 20px;">${escapeHtml(data.text || version.content_text || 'Content generated')}</div>`;
            if (data.highlights && data.highlights.length) {
                content += '<div style="background: var(--gray-100); padding: 20px; border-radius: 8px;"><h4>Key Points:</h4><ul>';
                data.highlights.forEach(h => { content += `<li>${escapeHtml(h)}</li>`; });
                content += '</ul></div>';
            }
        } catch {
            content += `<p style="white-space: pre-wrap;">${escapeHtml(version.content_text || 'Generated')}</p>`;
        }
    } else if (materialType === 'audio') {
        content += `<p>Audio script has been generated and narration synthesized.</p>`;
        if (version.assets?.audio_mp3) {
            content += `
                <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>🎧 Audio Narration</h4>
                    <audio controls style="width: 100%; margin-top: 10px;">
                        <source src="${version.assets.audio_mp3}" type="audio/mpeg">
                        Your browser does not support audio playback.
                    </audio>
                    <p style="margin-top: 10px; font-size: 14px; color: var(--gray-600);">
                        <em>Note: This is a placeholder audio file. Enable ElevenLabs API for real narration.</em>
                    </p>
                </div>
            `;
        }
        content += `
            <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-top: 20px;">
                <h4>📝 Audio Script</h4>
                <div style="white-space: pre-wrap; max-height: 400px; overflow-y: auto; line-height: 1.6; margin-top: 10px;">
                    ${escapeHtml(version.content_text || 'Script generated')}
                </div>
            </div>
        `;
    } else if (materialType === 'visual') {
        if (version.assets?.video_mp4) {
            content += `
                <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>🎬 Visual Animation</h4>
                    <video controls style="width: 100%; max-height: 400px; margin-top: 10px; border-radius: 8px;">
                        <source src="${version.assets.video_mp4}" type="video/mp4">
                        Your browser does not support video playback.
                    </video>
                    <p style="margin-top: 10px; font-size: 14px; color: var(--gray-600);">
                        <em>Note: This is a placeholder video. Enable Manim rendering for real animations.</em>
                    </p>
                </div>
            `;
        }
        content += `
            <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-top: 20px;">
                <h4>📐 Visual Concept Plan</h4>
                <div style="white-space: pre-wrap; line-height: 1.6; margin-top: 10px;">
                    ${escapeHtml(version.content_text || 'Visual animation plan created')}
                </div>
            </div>
        `;
    } else if (materialType === 'quiz') {
        try {
            const parsed = JSON.parse(version.content_text || '{}');
            const questions = parsed.questions || [];
            
            content += `
                <div style="background: var(--primary-100); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h4>🧠 Interactive Quiz</h4>
                    <p>${escapeHtml(parsed.summary || 'Test your understanding with this interactive quiz!')}</p>
                </div>
            `;
            
            if (questions.length > 0) {
                questions.forEach((q, index) => {
                    content += `
                        <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                            <h5 style="margin-bottom: 15px;">Question ${index + 1}: ${escapeHtml(q.question)}</h5>
                            <div style="margin-left: 20px;">
                    `;
                    
                    if (q.options && Array.isArray(q.options)) {
                        q.options.forEach((option, optIndex) => {
                            const letter = String.fromCharCode(65 + optIndex); // A, B, C, D...
                            content += `
                                <div style="padding: 10px; margin-bottom: 8px; background: white; border-radius: 4px; border: 2px solid var(--gray-200);">
                                    <label style="cursor: pointer; display: block;">
                                        <input type="radio" name="quiz_q${index}" value="${optIndex}" style="margin-right: 10px;">
                                        <strong>${letter}.</strong> ${escapeHtml(option)}
                                    </label>
                                </div>
                            `;
                        });
                    }
                    
                    content += `
                            </div>
                            ${q.explanation ? `
                                <details style="margin-top: 15px; padding: 10px; background: var(--gray-100); border-radius: 4px;">
                                    <summary style="cursor: pointer; font-weight: 600;">💡 Show Explanation</summary>
                                    <p style="margin-top: 10px; line-height: 1.6;">${escapeHtml(q.explanation)}</p>
                                    ${q.correct_answer !== undefined ? `<p style="margin-top: 10px;"><strong>Correct Answer:</strong> ${String.fromCharCode(65 + q.correct_answer)}</p>` : ''}
                                </details>
                            ` : ''}
                        </div>
                    `;
                });
            } else {
                content += `<p>Quiz questions generated - check quiz JSON file for details.</p>`;
            }
        } catch (e) {
            console.error('Quiz parsing error:', e);
            content += `<p>Quiz with multiple questions generated.</p>`;
        }
    }
    
    modalBody.innerHTML = content;
    modal.classList.add('active');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// ==================== STUDENT PORTAL ====================
function setupStudentPortalListeners() {
    // Subject filter
    const subjectFilter = document.getElementById('subject-filter-select');
    if (subjectFilter) {
        subjectFilter.addEventListener('change', (e) => {
            filterLessonsBySubject(e.target.value);
        });
    }
    
    // Load real assignments for students
    loadStudentLessons();
}

async function loadStudentLessons() {
    const lessonsFeed = document.getElementById('lessons-feed');
    if (!lessonsFeed) return;
    
    try {
        const response = await fetch('/api/assignments/student');
        
        if (!response.ok) {
            console.warn('Could not load student assignments');
            return;
        }
        
        const assignments = await response.json();
        
        if (assignments.length === 0) {
            lessonsFeed.innerHTML = '<div style="text-align: center; padding: 60px; color: var(--gray-600);"><h3>No lessons available yet</h3><p>Check back soon for new assignments from your teacher!</p></div>';
            return;
        }
        
        // Render assignment cards
        lessonsFeed.innerHTML = assignments.map(a => {
            const subjectClass = a.subject || 'science';
            const hasSimplified = a.variant_types?.includes('simplified');
            const hasAudio = a.variant_types?.includes('audio');
            const hasVisual = a.variant_types?.includes('visual');
            const hasQuiz = a.variant_types?.includes('quiz');
            
            let tagText = [];
            if (hasVisual && hasAudio) tagText.push('Visualized + Narrated');
            else if (hasVisual) tagText.push('Manim Animated');
            else if (hasAudio) tagText.push('Audio Guide');
            if (hasQuiz) tagText.push('Interactive Quiz');
            if (hasSimplified) tagText.push('Simplified');
            
            const tag = tagText.join(' • ') || 'Multi-format';
            
            return `
                <div class="lesson-card" data-subject="${a.subject}" data-lesson="${a.id}">
                    <div class="lesson-card-header">
                        <span class="lesson-badge ${subjectClass}">${a.subject}</span>
                        <span class="lesson-tag">${tag}</span>
                    </div>
                    <h3 class="lesson-title">${escapeHtml(a.title)}</h3>
                    <p class="lesson-description">Personalized learning experience with ${a.variant_types?.length || 0} different formats.</p>
                    <div class="lesson-meta">
                        ${hasVisual ? '<span>🎨 Visual Animation</span>' : ''}
                        ${hasAudio ? '<span>🎧 Audio Guide</span>' : ''}
                        ${hasSimplified ? '<span>📖 Simplified Text</span>' : ''}
                        ${hasQuiz ? '<span>🎯 Quiz</span>' : ''}
                    </div>
                    <button class="btn btn-primary" onclick="openStudentLesson('${a.id}')">View Lesson</button>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Failed to load student lessons:', error);
    }
}

async function openStudentLesson(assignmentId) {
    try {
        const response = await fetch(`/api/assignments/${assignmentId}`);
        
        if (!response.ok) {
            alert('Could not load lesson');
            return;
        }
        
        const assignment = await response.json();
        showLessonModal(assignment);
    } catch (error) {
        console.error('Failed to open lesson:', error);
        alert('Error loading lesson');
    }
}

function filterLessonsBySubject(subject) {
    const lessons = document.querySelectorAll('.lesson-card');
    
    lessons.forEach(lesson => {
        if (subject === 'all' || lesson.dataset.subject === subject) {
            lesson.style.display = 'block';
        } else {
            lesson.style.display = 'none';
        }
    });
}

function showLessonModal(lessonIdOrAssignment) {
    const modal = document.getElementById('lesson-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalSubject = document.getElementById('modal-subject');
    const modalBody = document.getElementById('modal-body');
    
    // If it's an assignment object from API, render its content
    if (typeof lessonIdOrAssignment === 'object' && lessonIdOrAssignment.id) {
        const assignment = lessonIdOrAssignment;
        modalTitle.textContent = assignment.title;
        modalSubject.textContent = assignment.subject;
        modalSubject.className = `modal-subject-badge lesson-badge ${assignment.subject}`;
        
        // Render versions
        let content = '<div style="margin-bottom: 20px;">';
        
        if (assignment.versions && assignment.versions.length) {
            assignment.versions.forEach(version => {
                if (!version.ready) return;
                
                content += '<div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">';
                
                if (version.variant_type === 'simplified') {
                    content += '<h4>📖 Simplified Text</h4>';
                    try {
                        const data = JSON.parse(version.content_text || '{}');
                        content += `<p style="margin-top: 10px;">${escapeHtml(data.text || version.content_text || '')}</p>`;
                    } catch {
                        content += `<p style="margin-top: 10px; white-space: pre-wrap;">${escapeHtml(version.content_text || '')}</p>`;
                    }
                } else if (version.variant_type === 'audio') {
                    content += '<h4>🎧 Audio Guide</h4>';
                    if (version.assets?.audio_mp3) {
                        content += `<audio controls style="width: 100%; margin-top: 10px;"><source src="${version.assets.audio_mp3}" type="audio/mpeg"></audio>`;
                    }
                } else if (version.variant_type === 'visual') {
                    content += '<h4>🎨 Visual Animation</h4>';
                    if (version.assets?.video_mp4) {
                        content += `<video controls style="width: 100%; max-height: 300px; margin-top: 10px;"><source src="${version.assets.video_mp4}" type="video/mp4"></video>`;
                    }
                    content += `<p style="margin-top: 10px;">${escapeHtml(version.content_text || 'Visual lesson created')}</p>`;
                } else if (version.variant_type === 'quiz') {
                    content += '<h4>🎯 Interactive Quiz</h4>';
                    content += '<p style="margin-top: 10px;">Quiz ready with interactive questions!</p>';
                }
                
                content += '</div>';
            });
        } else {
            content += '<p>Content is being generated...</p>';
        }
        
        content += '</div>';
        modalBody.innerHTML = content;
        modal.classList.add('active');
        resetAudioPlayer();
        return;
    }
    
    // Legacy: Fallback to hardcoded examples if string ID provided
    const lessonId = lessonIdOrAssignment;
    
    const lessons = {
        photosynthesis: {
            title: 'Photosynthesis: How Plants Make Food',
            subject: 'Science',
            subjectClass: 'science',
            content: `
                <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">🌱 Understanding Photosynthesis</h3>
                    <p style="font-size: 18px; line-height: 1.8;">
                        Photosynthesis is the amazing process that plants use to make their own food using sunlight, 
                        water, and carbon dioxide from the air.
                    </p>
                </div>
                
                <h4 style="margin-top: 25px; margin-bottom: 15px;">How It Works:</h4>
                <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <ol style="font-size: 16px; line-height: 2;">
                        <li><strong>Sunlight</strong> - Plants capture light energy with their green leaves</li>
                        <li><strong>Water</strong> - Roots absorb water from the soil</li>
                        <li><strong>Carbon Dioxide</strong> - Leaves take in CO₂ from the air</li>
                        <li><strong>Glucose</strong> - Plants create sugar for energy and growth</li>
                        <li><strong>Oxygen</strong> - Plants release oxygen that we breathe!</li>
                    </ol>
                </div>
                
                <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 4px;">
                    <strong>🌟 Fun Fact:</strong> One large tree can produce enough oxygen for two people for an entire year!
                </div>
            `
        },
        'past-tense': {
            title: 'AI Translation Coach: Past Tense Practice',
            subject: 'Language Arts',
            subjectClass: 'language',
            content: `
                <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">🤖 AI-Guided Translation Learning</h3>
                    <p style="font-size: 18px; line-height: 1.8;">
                        Learn Spanish through interactive translation with AI coaching! Instead of giving you direct answers, 
                        I'll ask you guided questions to help you think critically about grammar, tense, and vocabulary.
                    </p>
                </div>
                
                <h4 style="margin-top: 25px; margin-bottom: 15px;">🎯 Translation Challenge:</h4>
                <div style="background: var(--gray-50); padding: 25px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #F59E0B;">
                    <p style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #1F2937;">
                        Translate to Spanish: <span style="color: #F59E0B;">"I went to the store yesterday."</span>
                    </p>
                    <input type="text" placeholder="Type your translation here..." style="width: 100%; padding: 12px; border: 2px solid #E5E7EB; border-radius: 8px; font-size: 16px; margin-bottom: 15px;">
                    <button style="background: #F59E0B; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Submit Answer</button>
                </div>
                
                <div style="background: #EFF6FF; border-left: 4px solid #3B82F6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="color: #1E40AF; margin-bottom: 12px;">🤖 AI Coach Response:</h4>
                    <p style="color: #1F2937; margin-bottom: 15px; font-style: italic;">
                        "Great effort! Before I show you the correct answer, let's think through this together..."
                    </p>
                    
                    <h5 style="color: #1E40AF; margin-top: 20px; margin-bottom: 10px;">💭 Think about these questions:</h5>
                    <ul style="line-height: 2; color: #374151;">
                        <li><strong>Tense:</strong> "Went" is past tense - should you use <em>preterite</em> or <em>imperfect</em>? (Hint: This is a completed action)</li>
                        <li><strong>Verb:</strong> What's the Spanish infinitive for "to go"? Is it regular or irregular in past tense?</li>
                        <li><strong>Vocabulary:</strong> For "store," would you use <em>tienda</em> or <em>almacén</em>? What's the difference?</li>
                        <li><strong>Time marker:</strong> How do you say "yesterday" - <em>ayer</em> or <em>anoche</em>?</li>
                        <li><strong>Word order:</strong> Where does the time marker typically go in Spanish sentences?</li>
                    </ul>
                    
                    <button style="background: #3B82F6; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 15px;">
                        💡 I've thought about it - Show me hints
                    </button>
                </div>
                
                <h4 style="margin-top: 25px; margin-bottom: 15px;">How This Works (vs. Google Translate):</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #FEE2E2; padding: 20px; border-radius: 8px; border-left: 4px solid #EF4444;">
                        <h5 style="color: #DC2626; margin-bottom: 10px;">❌ Google Translate</h5>
                        <p style="color: #7F1D1D; line-height: 1.6;">
                            • Gives instant translation<br>
                            • No explanation<br>
                            • No learning happens<br>
                            • Just copy/paste
                        </p>
                    </div>
                    <div style="background: #D1FAE5; padding: 20px; border-radius: 8px; border-left: 4px solid #10B981;">
                        <h5 style="color: #059669; margin-bottom: 10px;">✅ AI Coach</h5>
                        <p style="color: #065F46; line-height: 1.6;">
                            • Asks guided questions<br>
                            • Explains grammar rules<br>
                            • Builds critical thinking<br>
                            • Real understanding
                        </p>
                    </div>
                </div>
                
                <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 4px;">
                    <strong>🌟 Learning Goal:</strong> By thinking through tense, vocabulary, and structure, you'll develop the skills to translate confidently without relying on automatic translation tools!
                </div>
            `
        },
        wwi: {
            title: 'World War I: A Timeline',
            subject: 'History',
            subjectClass: 'history',
            content: `
                <div style="background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">📜 World War I Timeline</h3>
                    <p style="font-size: 18px; line-height: 1.8;">
                        World War I was a major global conflict from 1914 to 1918. Let's explore the key events through an interactive timeline.
                    </p>
                </div>
                
                <div style="position: relative; padding-left: 30px; border-left: 3px solid var(--gray-300);">
                    <div style="margin-bottom: 30px; position: relative;">
                        <div style="position: absolute; left: -38px; width: 12px; height: 12px; background: #EF4444; border-radius: 50%; border: 3px solid white;"></div>
                        <h4 style="color: #EF4444; margin-bottom: 8px;">1914 - The War Begins</h4>
                        <p>Assassination of Archduke Franz Ferdinand sparks the conflict. Nations form alliances and mobilize armies.</p>
                    </div>
                    
                    <div style="margin-bottom: 30px; position: relative;">
                        <div style="position: absolute; left: -38px; width: 12px; height: 12px; background: #F59E0B; border-radius: 50%; border: 3px solid white;"></div>
                        <h4 style="color: #F59E0B; margin-bottom: 8px;">1915-1916 - Trench Warfare</h4>
                        <p>Soldiers dig trenches across Europe. Battles like Verdun and the Somme result in heavy casualties.</p>
                    </div>
                    
                    <div style="margin-bottom: 30px; position: relative;">
                        <div style="position: absolute; left: -38px; width: 12px; height: 12px; background: #3B82F6; border-radius: 50%; border: 3px solid white;"></div>
                        <h4 style="color: #3B82F6; margin-bottom: 8px;">1917 - Turning Point</h4>
                        <p>United States enters the war. Russia experiences revolution and exits the conflict.</p>
                    </div>
                    
                    <div style="margin-bottom: 30px; position: relative;">
                        <div style="position: absolute; left: -38px; width: 12px; height: 12px; background: #10B981; border-radius: 50%; border: 3px solid white;"></div>
                        <h4 style="color: #10B981; margin-bottom: 8px;">1918 - The War Ends</h4>
                        <p>Armistice signed on November 11, 1918. The Treaty of Versailles officially ends the conflict.</p>
                    </div>
                </div>
                
                <div style="background: #FEF3C7; border-left: 4px solid #EF4444; padding: 15px; border-radius: 4px; margin-top: 20px;">
                    <strong>📖 Remember:</strong> World War I changed the world forever and led to significant political and social changes.
                </div>
            `
        },
        continents: {
            title: 'Continents Quiz Challenge',
            subject: 'Geography',
            subjectClass: 'geography',
            content: `
                <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">🌍 Learn About the Continents</h3>
                    <p style="font-size: 18px; line-height: 1.8;">
                        Our planet has seven continents! Can you name them all? Let's explore each one.
                    </p>
                </div>
                
                <h4 style="margin-top: 25px; margin-bottom: 15px;">The Seven Continents:</h4>
                <div style="display: grid; gap: 12px; margin-bottom: 20px;">
                    <div style="background: #DBEAFE; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>1. Asia</strong> - The largest continent</span>
                        <span style="font-size: 24px;">🏔️</span>
                    </div>
                    <div style="background: #D1FAE5; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>2. Africa</strong> - Home to the Sahara Desert</span>
                        <span style="font-size: 24px;">🦁</span>
                    </div>
                    <div style="background: #FEF3C7; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>3. North America</strong> - Where we are!</span>
                        <span style="font-size: 24px;">🗽</span>
                    </div>
                    <div style="background: #FECACA; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>4. South America</strong> - Amazon rainforest</span>
                        <span style="font-size: 24px;">🌴</span>
                    </div>
                    <div style="background: #E9D5FF; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>5. Antarctica</strong> - The frozen continent</span>
                        <span style="font-size: 24px;">🐧</span>
                    </div>
                    <div style="background: #FED7AA; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>6. Europe</strong> - Many countries in a small area</span>
                        <span style="font-size: 24px;">🏰</span>
                    </div>
                    <div style="background: #BAE6FD; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>7. Australia</strong> - Also called Oceania</span>
                        <span style="font-size: 24px;">🦘</span>
                    </div>
                </div>
                
                <div style="background: #FEF3C7; border-left: 4px solid #8B5CF6; padding: 15px; border-radius: 4px;">
                    <strong>🎮 Challenge:</strong> Try to point to each continent on a world map!
                </div>
            `
        },
        equations: {
            title: 'Solving Linear Equations',
            subject: 'Mathematics',
            subjectClass: 'math',
            content: `
                <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">📐 Solving Linear Equations</h3>
                    <p style="font-size: 18px; line-height: 1.8;">
                        Learn how to solve for x with step-by-step visual explanations!
                    </p>
                </div>
                
                <h4 style="margin-top: 25px; margin-bottom: 15px;">Example: Solve 2x + 6 = 14</h4>
                
                <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="margin-bottom: 20px;">
                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <strong>Step 1:</strong> Write the equation<br>
                            <div style="font-size: 24px; text-align: center; margin-top: 10px; font-family: monospace;">
                                2x + 6 = 14
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <strong>Step 2:</strong> Subtract 6 from both sides<br>
                            <div style="font-size: 24px; text-align: center; margin-top: 10px; font-family: monospace;">
                                2x + 6 - 6 = 14 - 6
                            </div>
                            <div style="font-size: 24px; text-align: center; margin-top: 10px; font-family: monospace; color: #10B981;">
                                2x = 8
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <strong>Step 3:</strong> Divide both sides by 2<br>
                            <div style="font-size: 24px; text-align: center; margin-top: 10px; font-family: monospace;">
                                2x ÷ 2 = 8 ÷ 2
                            </div>
                            <div style="font-size: 28px; text-align: center; margin-top: 10px; font-family: monospace; color: #10B981; font-weight: bold;">
                                x = 4 ✓
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="background: #DBEAFE; border-left: 4px solid #3B82F6; padding: 15px; border-radius: 4px;">
                    <strong>✅ Check your answer:</strong> Replace x with 4<br>
                    <span style="font-family: monospace;">2(4) + 6 = 8 + 6 = 14 ✓</span>
                </div>
            `
        },
        'solar-system': {
            title: 'The Solar System',
            subject: 'Science',
            subjectClass: 'science',
            content: `
                <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">🌌 Our Solar System</h3>
                    <p style="font-size: 18px; line-height: 1.8;">
                        Explore the planets orbiting our Sun in this simplified visual lesson!
                    </p>
                </div>
                
                <h4 style="margin-top: 25px; margin-bottom: 15px;">The 8 Planets (in order from the Sun):</h4>
                
                <div style="display: grid; gap: 12px;">
                    <div style="background: #FED7AA; padding: 15px; border-radius: 8px;">
                        <strong>1. ☀️ Mercury</strong> - The smallest and fastest planet
                    </div>
                    <div style="background: #FEF3C7; padding: 15px; border-radius: 8px;">
                        <strong>2. 🌕 Venus</strong> - The hottest planet (hotter than Mercury!)
                    </div>
                    <div style="background: #DBEAFE; padding: 15px; border-radius: 8px;">
                        <strong>3. 🌍 Earth</strong> - Our home! The only planet with life
                    </div>
                    <div style="background: #FECACA; padding: 15px; border-radius: 8px;">
                        <strong>4. 🔴 Mars</strong> - The "Red Planet" with rocky deserts
                    </div>
                    <div style="background: #FED7AA; padding: 15px; border-radius: 8px;">
                        <strong>5. 🪐 Jupiter</strong> - The biggest planet, a gas giant
                    </div>
                    <div style="background: #FEF3C7; padding: 15px; border-radius: 8px;">
                        <strong>6. 💫 Saturn</strong> - Famous for its beautiful rings
                    </div>
                    <div style="background: #BFDBFE; padding: 15px; border-radius: 8px;">
                        <strong>7. 🔵 Uranus</strong> - An ice giant that spins sideways
                    </div>
                    <div style="background: #93C5FD; padding: 15px; border-radius: 8px;">
                        <strong>8. 🌊 Neptune</strong> - The windiest planet in our solar system
                    </div>
                </div>
                
                <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 4px; margin-top: 20px;">
                    <strong>💡 Remember:</strong> My Very Excellent Mother Just Served Us Nachos!
                    <br><small>(Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune)</small>
                </div>
            `
        }
    };
    
    const lesson = lessons[lessonId];
    if (lesson && modal && modalTitle && modalSubject && modalBody) {
        modalTitle.textContent = lesson.title;
        modalSubject.textContent = lesson.subject;
        modalSubject.className = `modal-subject-badge lesson-badge ${lesson.subjectClass}`;
        modalBody.innerHTML = lesson.content;
        modal.classList.add('active');
        
        // Reset audio player
        resetAudioPlayer();
    }
}

// ==================== AUDIO PLAYER ====================
function resetAudioPlayer() {
    state.audioPlaying = false;
    state.audioProgress = 0;
    
    const playIcon = document.getElementById('play-icon');
    const progressBar = document.getElementById('audio-progress-bar');
    const audioTime = document.getElementById('audio-time');
    
    if (playIcon) playIcon.textContent = '▶️';
    if (progressBar) progressBar.style.width = '0%';
    if (audioTime) audioTime.textContent = '0:00 / 2:30';
}

function setupAudioPlayer() {
    const playPauseBtn = document.getElementById('play-pause-btn');
    const progressContainer = document.querySelector('.audio-progress');
    
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', toggleAudioPlayback);
    }
    
    if (progressContainer) {
        progressContainer.addEventListener('click', (e) => {
            const rect = progressContainer.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            state.audioProgress = percent * 150; // 2:30 in seconds
            updateAudioProgress();
        });
    }
}

function toggleAudioPlayback() {
    state.audioPlaying = !state.audioPlaying;
    
    const playIcon = document.getElementById('play-icon');
    if (playIcon) {
        playIcon.textContent = state.audioPlaying ? '⏸️' : '▶️';
    }
    
    if (state.audioPlaying) {
        startAudioPlayback();
    } else {
        stopAudioPlayback();
    }
}

let audioInterval;

function startAudioPlayback() {
    audioInterval = setInterval(() => {
        state.audioProgress += 1;
        if (state.audioProgress >= 150) { // 2:30 duration
            state.audioProgress = 150;
            stopAudioPlayback();
        }
        updateAudioProgress();
    }, 1000);
}

function stopAudioPlayback() {
    clearInterval(audioInterval);
    state.audioPlaying = false;
    const playIcon = document.getElementById('play-icon');
    if (playIcon) playIcon.textContent = '▶️';
}

function updateAudioProgress() {
    const progressBar = document.getElementById('audio-progress-bar');
    const audioTime = document.getElementById('audio-time');
    
    const percent = (state.audioProgress / 150) * 100;
    const currentMin = Math.floor(state.audioProgress / 60);
    const currentSec = Math.floor(state.audioProgress % 60);
    
    if (progressBar) progressBar.style.width = percent + '%';
    if (audioTime) {
        audioTime.textContent = `${currentMin}:${currentSec.toString().padStart(2, '0')} / 2:30`;
    }
}

// ==================== MODAL MANAGEMENT ====================
function setupModalListeners() {
    // Lesson modal close buttons
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            closeLessonModal();
        });
    });
    
    // Material modal close buttons
    document.querySelectorAll('[data-close-material-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            closeMaterialModal();
        });
    });
    
    // Audio player
    setupAudioPlayer();
    
    // Language and level buttons
    const changeLangBtn = document.getElementById('change-language-btn');
    const adjustLevelBtn = document.getElementById('adjust-level-btn');
    
    if (changeLangBtn) {
        changeLangBtn.addEventListener('click', () => {
            alert('Language changed to: ' + state.language + '\n(This would change the lesson content in a real application)');
        });
    }
    
    if (adjustLevelBtn) {
        adjustLevelBtn.addEventListener('click', () => {
            alert('Difficulty level adjusted!\n(This would modify the complexity of the content in a real application)');
        });
    }
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeLessonModal();
            closeMaterialModal();
        }
    });
}

function closeLessonModal() {
    const modal = document.getElementById('lesson-modal');
    if (modal) {
        modal.classList.remove('active');
        stopAudioPlayback();
    }
}

function closeMaterialModal() {
    const modal = document.getElementById('material-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// ==================== ACCESSIBILITY SETTINGS ====================
function setupAccessibilityListeners() {
    // Theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            state.theme = btn.dataset.theme;
            applyPreferences();
        });
    });
    
    // Font size buttons
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            state.fontSize = btn.dataset.size;
            applyPreferences();
        });
    });
    
    // Reading speed buttons
    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            state.readingSpeed = btn.dataset.speed;
            applyPreferences();
        });
    });
    
    // Language select
    const languageSelect = document.getElementById('language-select');
    if (languageSelect) {
        languageSelect.addEventListener('change', (e) => {
            state.language = e.target.value;
        });
    }
    
    // Save settings button
    const saveBtn = document.getElementById('save-settings');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            savePreferences();
            showNotification('Settings saved successfully!');
        });
    }
    
    // Reset settings button
    const resetBtn = document.getElementById('reset-settings');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            state.theme = 'light';
            state.fontSize = 'medium';
            state.readingSpeed = 'normal';
            state.language = 'en';
            applyPreferences();
            savePreferences();
            showNotification('Settings reset to defaults');
        });
    }
}

function showNotification(message) {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: #10B981;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        font-weight: 600;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
