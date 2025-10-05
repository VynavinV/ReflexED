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
    const saved = localStorage.getItem('reflexed-preferences');
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
    localStorage.setItem('reflexed-preferences', JSON.stringify(state.preferences));
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
                <div class="lesson-item" data-assignment-id="${a.id}">
                    <div class="lesson-info">
                        <span class="lesson-subject ${subjectClass}">${a.subject}</span>
                        <h3>${escapeHtml(a.title)}</h3>
                        <p>${timeText} • ${statusBadge}</p>
                    </div>
                    <div class="lesson-actions">
                        <button class="btn btn-outline btn-sm" onclick="viewAssignment('${a.id}')">View</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteAssignment('${a.id}', event)" title="Delete this assignment">
                            <span style="margin-right: 4px;">🗑️</span>Delete
                        </button>
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

async function deleteAssignment(assignmentId, event) {
    // Prevent event bubbling
    if (event) {
        event.stopPropagation();
    }
    
    // Confirm deletion
    const confirmed = confirm('Are you sure you want to delete this assignment? This action cannot be undone.');
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/api/assignments/${assignmentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(`Failed to delete assignment: ${error.error || 'Unknown error'}`);
            return;
        }
        
        // Success - remove the item from the UI with animation
        const lessonItem = document.querySelector(`[data-assignment-id="${assignmentId}"]`);
        if (lessonItem) {
            lessonItem.style.opacity = '0';
            lessonItem.style.transform = 'translateX(-20px)';
            lessonItem.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                lessonItem.remove();
                
                // Check if there are no more lessons
                const lessonsList = document.querySelector('.lessons-list');
                if (lessonsList && lessonsList.children.length === 0) {
                    lessonsList.innerHTML = '<p style="text-align: center; color: var(--gray-600); padding: 40px;">No lessons created yet. Upload your first assignment above!</p>';
                }
            }, 300);
        }
        
        // Show success message
        showNotification('Assignment deleted successfully', 'success');
        
    } catch (error) {
        console.error('Failed to delete assignment:', error);
        alert('Error deleting assignment. Please try again.');
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
        // Parse audio data to check if it's podcast format
        try {
            const audioData = JSON.parse(version.content_text || '{}');
            const discussion = audioData.discussion || [];
            
            if (discussion.length > 0) {
                // Podcast format
                content += `
                    <div style="background: var(--primary-100); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h4>🎙️ Educational Podcast Discussion</h4>
                        <p>${escapeHtml(audioData.summary || 'An engaging discussion about the lesson content')}</p>
                    </div>
                `;
                
                if (version.assets?.audio_mp3) {
                    content += `
                        <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h4>🎧 Listen to the Discussion</h4>
                            <audio controls style="width: 100%; margin-top: 10px;">
                                <source src="${version.assets.audio_mp3}" type="audio/mpeg">
                                Your browser does not support audio playback.
                            </audio>
                        </div>
                    `;
                }
                
                // Show transcript
                content += `
                    <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h4>📝 Podcast Transcript</h4>
                        <div style="margin-top: 15px;">
                `;
                
                discussion.forEach((segment, index) => {
                    const isHost = segment.speaker === 'Host';
                    const bgColor = isHost ? '#e3f2fd' : '#f3e5f5';
                    const icon = isHost ? '👤' : '🎓';
                    content += `
                        <div style="background: ${bgColor}; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid ${isHost ? '#2196f3' : '#9c27b0'};">
                            <div style="font-weight: 600; margin-bottom: 8px; color: ${isHost ? '#1976d2' : '#7b1fa2'};">
                                ${icon} ${escapeHtml(segment.speaker || 'Speaker')}
                            </div>
                            <div style="line-height: 1.6;">
                                ${escapeHtml(segment.text || '')}
                            </div>
                        </div>
                    `;
                });
                
                content += `
                        </div>
                    </div>
                `;
            } else {
                // Fallback to simple audio script
                throw new Error('Not podcast format');
            }
        } catch (e) {
            // Simple audio format
            content += `<p>Audio script has been generated and narration synthesized.</p>`;
            if (version.assets?.audio_mp3) {
                content += `
                    <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h4>🎧 Audio Narration</h4>
                        <audio controls style="width: 100%; margin-top: 10px;">
                            <source src="${version.assets.audio_mp3}" type="audio/mpeg">
                            Your browser does not support audio playback.
                        </audio>
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
        }
    } else if (materialType === 'visual') {
        // Parse visual data to show narration if available
        try {
            const visualData = JSON.parse(version.content_text || '{}');
            const narration = visualData.narration || [];
            const description = visualData.description || '';
            
            content += `
                <div style="background: var(--primary-100); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h4>🎬 Visual Learning Experience</h4>
                    <p>${escapeHtml(description || 'An engaging visual explanation of the concepts')}</p>
                </div>
            `;
            
            if (version.assets?.video_mp4) {
                content += `
                    <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h4>📹 Watch the Animation</h4>
                        <video controls style="width: 100%; max-height: 400px; margin-top: 10px; border-radius: 8px;">
                            <source src="${version.assets.video_mp4}" type="video/mp4">
                            Your browser does not support video playback.
                        </video>
                    </div>
                `;
            }
            
            // Show narration timeline if available
            if (narration.length > 0) {
                content += `
                    <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h4>🎙️ Narration Timeline</h4>
                        <div style="margin-top: 15px;">
                `;
                
                narration.forEach((segment, index) => {
                    content += `
                        <div style="display: flex; gap: 15px; padding: 12px; margin-bottom: 10px; background: white; border-radius: 6px; border-left: 4px solid var(--primary-500);">
                            <div style="min-width: 60px; text-align: center; background: var(--primary-100); padding: 8px; border-radius: 4px;">
                                <div style="font-weight: 600; color: var(--primary-700);">${segment.duration || '?'}s</div>
                            </div>
                            <div style="flex: 1;">
                                <p style="line-height: 1.6;">${escapeHtml(segment.text || '')}</p>
                            </div>
                        </div>
                    `;
                });
                
                content += `
                        </div>
                    </div>
                `;
            }
        } catch (e) {
            // Fallback to simple text display
            if (version.assets?.video_mp4) {
                content += `
                    <div style="background: var(--gray-100); padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h4>🎬 Visual Animation</h4>
                        <video controls style="width: 100%; max-height: 400px; margin-top: 10px; border-radius: 8px;">
                            <source src="${version.assets.video_mp4}" type="video/mp4">
                            Your browser does not support video playback.
                        </video>
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
        }
    } else if (materialType === 'quiz') {
        try {
            const parsed = JSON.parse(version.content_text || '{}');
            content += renderQuizContent(parsed);
        } catch (e) {
            console.error('Quiz parsing error:', e);
            content += `<p>Quiz with multiple questions generated.</p>`;
        }
    }
    
    modalBody.innerHTML = content;
    modal.classList.add('active');
}

// Enhanced quiz rendering functions
function renderQuizContent(parsed) {
    const quizType = parsed.quiz_type || 'standard';
    let content = `
        <div style="background: var(--primary-100); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h4>🧠 ${getQuizTitle(quizType)}</h4>
            <p>${escapeHtml(parsed.summary || 'Test your understanding with this interactive exercise!')}</p>
        </div>
    `;
    
    // Render based on quiz type
    switch (quizType) {
        case 'socratic':
            content += renderSocraticQuiz(parsed.questions || []);
            break;
        case 'practice':
            content += renderPracticeQuiz(parsed.questions || []);
            break;
        case 'practice_repeatable':
            content += renderRepeatablePractice(parsed.questions || []);
            break;
        case 'timeline_fill':
            content += renderTimelineFill(parsed);
            break;
        default:
            content += renderStandardQuiz(parsed.questions || []);
    }
    
    return content;
}

function getQuizTitle(quizType) {
    const titles = {
        'socratic': 'Guided Learning Questions',
        'practice': 'Practice Problems',
        'practice_repeatable': 'Practice Exercise',
        'timeline_fill': 'Timeline & Historical Figures',
        'standard': 'Interactive Quiz'
    };
    return titles[quizType] || 'Interactive Quiz';
}

function renderSocraticQuiz(questions) {
    let html = '';
    questions.forEach((q, index) => {
        html += `
            <div class="quiz-question" data-question-id="${index}" style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <h5 style="margin-bottom: 15px; color: var(--primary-700);">Question ${index + 1}</h5>
                <p style="font-size: 1.1em; margin-bottom: 15px;">${escapeHtml(q.question)}</p>
                
                <details style="margin-top: 15px; padding: 15px; background: var(--blue-50); border-radius: 4px; border-left: 4px solid var(--primary-500);">
                    <summary style="cursor: pointer; font-weight: 600; color: var(--primary-700);">💭 Guidance</summary>
                    <p style="margin-top: 10px; line-height: 1.6;">${escapeHtml(q.guidance || '')}</p>
                    ${q.follow_up ? `<p style="margin-top: 10px; font-style: italic;">Next: ${escapeHtml(q.follow_up)}</p>` : ''}
                </details>
                
                <div style="margin-top: 15px;">
                    <textarea class="student-answer" placeholder="Your thoughts here..." style="width: 100%; min-height: 80px; padding: 10px; border-radius: 4px; border: 2px solid var(--gray-300); resize: vertical;"></textarea>
                </div>
                
                <div style="margin-top: 10px; display: flex; gap: 10px;">
                    <button class="btn btn-primary" onclick="submitQuizAnswer(${index}, 'socratic')" style="flex: 1;">
                        📝 Submit Answer
                    </button>
                    <button class="btn btn-outline" onclick="getAIFeedback(${index}, 'socratic')" style="flex: 1;">
                        🤖 Get AI Check
                    </button>
                </div>
                
                <div class="feedback-area" style="display: none; margin-top: 15px; padding: 15px; border-radius: 8px;"></div>
            </div>
        `;
    });
    return html;
}

function renderPracticeQuiz(questions) {
    let html = '';
    questions.forEach((q, index) => {
        const difficultyColor = {
            'easy': 'green',
            'medium': 'orange',
            'hard': 'red'
        }[q.difficulty] || 'gray';
        
        html += `
            <div class="quiz-question" data-question-id="${index}" style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h5 style="margin: 0;">Problem ${index + 1}</h5>
                    <span style="background: ${difficultyColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; text-transform: uppercase;">${escapeHtml(q.difficulty || 'medium')}</span>
                </div>
                <p style="font-size: 1.1em; margin-bottom: 15px;">${escapeHtml(q.question)}</p>
                
                <div style="margin-bottom: 15px;">
                    <input type="text" class="student-answer" placeholder="Your answer..." style="width: 100%; padding: 12px; border-radius: 4px; border: 2px solid var(--gray-300); font-size: 1em;">
                </div>
                
                <div style="margin-bottom: 10px; display: flex; gap: 10px;">
                    <button class="btn btn-primary" onclick="submitQuizAnswer(${index}, 'practice')" style="flex: 1;">
                        ✓ Submit Solution
                    </button>
                    <button class="btn btn-outline" onclick="getAIFeedback(${index}, 'practice')" style="flex: 1;">
                        🤖 Get AI Check
                    </button>
                </div>
                
                <div class="feedback-area" style="display: none; margin-top: 15px; padding: 15px; border-radius: 8px;"></div>
                
                <details style="margin-top: 15px; padding: 15px; background: white; border-radius: 4px;">
                    <summary style="cursor: pointer; font-weight: 600; color: var(--primary-700);">📝 Show Solution</summary>
                    <div style="margin-top: 15px;">
                        <h6>Step-by-Step Solution:</h6>
                        <p style="white-space: pre-wrap; line-height: 1.8;">${escapeHtml(q.solution || '')}</p>
                    </div>
                    ${q.common_mistakes && q.common_mistakes.length > 0 ? `
                        <div style="margin-top: 15px; padding: 10px; background: var(--yellow-50); border-radius: 4px;">
                            <h6>⚠️ Common Mistakes:</h6>
                            <ul style="margin-top: 8px;">
                                ${q.common_mistakes.map(m => `<li>${escapeHtml(m)}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </details>
            </div>
        `;
    });
    return html;
}

function renderRepeatablePractice(questions) {
    let html = '';
    questions.forEach((q, index) => {
        html += `
            <div class="quiz-question" data-question-id="${index}" style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <h5 style="margin-bottom: 15px;">Question ${index + 1}</h5>
                <p style="font-size: 1.1em; margin-bottom: 15px;">${escapeHtml(q.question)}</p>
                
                <div style="margin-bottom: 15px;">
                    <input type="text" class="student-answer" placeholder="Your answer..." style="width: 100%; padding: 12px; border-radius: 4px; border: 2px solid var(--gray-300); font-size: 1em;">
                </div>
                
                <div style="margin-bottom: 10px; display: flex; gap: 10px;">
                    <button class="btn btn-primary" onclick="submitQuizAnswer(${index}, 'practice_repeatable')" style="flex: 1;">
                        ✓ Check Answer
                    </button>
                    <button class="btn btn-outline" onclick="getAIFeedback(${index}, 'practice_repeatable')" style="flex: 1;">
                        🤖 Get AI Check
                    </button>
                </div>
                
                <div class="feedback-area" style="display: none; margin-top: 15px; padding: 15px; border-radius: 8px;"></div>
                
                ${q.hint ? `
                    <details style="margin-bottom: 10px; padding: 10px; background: var(--blue-50); border-radius: 4px;">
                        <summary style="cursor: pointer; font-weight: 600;">💡 Hint</summary>
                        <p style="margin-top: 8px;">${escapeHtml(q.hint)}</p>
                    </details>
                ` : ''}
                
                <details style="padding: 15px; background: white; border-radius: 4px;">
                    <summary style="cursor: pointer; font-weight: 600; color: var(--primary-700);">✓ Show Answer</summary>
                    <div style="margin-top: 15px;">
                        <p style="font-weight: 600; color: var(--success-700);">Answer: ${escapeHtml(q.answer || '')}</p>
                        ${q.explanation ? `<p style="margin-top: 10px; line-height: 1.6;">${escapeHtml(q.explanation)}</p>` : ''}
                        ${q.real_world_example || q.interesting_fact ? `
                            <div style="margin-top: 12px; padding: 12px; background: var(--blue-50); border-radius: 4px;">
                                <p style="font-size: 0.95em;"><strong>💫 Did you know?</strong> ${escapeHtml(q.real_world_example || q.interesting_fact)}</p>
                            </div>
                        ` : ''}
                    </div>
                </details>
            </div>
        `;
    });
    return html;
}

function renderTimelineFill(parsed) {
    let html = '';
    
    // Timeline events
    if (parsed.timeline_events && parsed.timeline_events.length > 0) {
        html += `<h5 style="margin: 20px 0;">📅 Timeline Events</h5>`;
        parsed.timeline_events.forEach((event, index) => {
            html += `
                <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="background: var(--primary-600); color: white; padding: 8px 16px; border-radius: 8px; font-weight: 600; min-width: 80px; text-align: center;">${escapeHtml(event.year || '????')}</span>
                        <p style="flex: 1; font-size: 1.05em;">${escapeHtml(event.event_description || '')}</p>
                    </div>
                    <details style="margin-top: 15px; padding: 10px; background: white; border-radius: 4px;">
                        <summary style="cursor: pointer; font-weight: 600;">✓ Show Answer</summary>
                        <p style="margin-top: 8px; color: var(--success-700); font-weight: 600;">${escapeHtml(event.answer || '')}</p>
                    </details>
                </div>
            `;
        });
    }
    
    // Famous people
    if (parsed.famous_people && parsed.famous_people.length > 0) {
        html += `<h5 style="margin: 30px 0 20px;">👤 Historical Figures</h5>`;
        parsed.famous_people.forEach((person, index) => {
            html += `
                <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <p style="font-size: 1.05em; margin-bottom: 15px;">${escapeHtml(person.description || '')}</p>
                    <details style="padding: 10px; background: white; border-radius: 4px;">
                        <summary style="cursor: pointer; font-weight: 600;">✓ Show Answer</summary>
                        <p style="margin-top: 8px; color: var(--success-700); font-weight: 600;">${escapeHtml(person.answer || '')}</p>
                        ${person.significance ? `<p style="margin-top: 8px; font-style: italic;">${escapeHtml(person.significance)}</p>` : ''}
                    </details>
                </div>
            `;
        });
    }
    
    return html || '<p>No timeline items found.</p>';
}

function renderStandardQuiz(questions) {
    let html = '';
    questions.forEach((q, index) => {
        html += `
            <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <h5 style="margin-bottom: 15px;">Question ${index + 1}: ${escapeHtml(q.question)}</h5>
                <div style="margin-left: 20px;">
        `;
        
        if (q.options && Array.isArray(q.options)) {
            q.options.forEach((option, optIndex) => {
                const letter = String.fromCharCode(65 + optIndex);
                html += `
                    <div style="padding: 10px; margin-bottom: 8px; background: white; border-radius: 4px; border: 2px solid var(--gray-200);">
                        <label style="cursor: pointer; display: block;">
                            <input type="radio" name="quiz_q${index}" value="${optIndex}" style="margin-right: 10px;">
                            <strong>${letter}.</strong> ${escapeHtml(option)}
                        </label>
                    </div>
                `;
            });
        }
        
        html += `
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
    return html;
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
                    // Try to parse visual content for narration timeline
                    try {
                        const visualData = JSON.parse(version.content_text);
                        if (visualData.description) {
                            content += `<p style="margin-top: 10px;"><strong>Description:</strong> ${escapeHtml(visualData.description)}</p>`;
                        }
                        if (visualData.narration && Array.isArray(visualData.narration)) {
                            content += '<div style="margin-top: 10px;"><strong>Narration Timeline:</strong></div>';
                            content += '<div style="margin-top: 10px;">';
                            visualData.narration.forEach((segment, idx) => {
                                content += `
                                    <div style="background: var(--gray-100); padding: 10px; margin: 5px 0; border-radius: 4px;">
                                        <span style="background: var(--primary-500); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; margin-right: 8px;">${segment.duration}s</span>
                                        <span>${escapeHtml(segment.text)}</span>
                                    </div>
                                `;
                            });
                            content += '</div>';
                        }
                    } catch (e) {
                        content += `<p style="margin-top: 10px;">${escapeHtml(version.content_text || 'Visual lesson created')}</p>`;
                    }
                } else if (version.variant_type === 'quiz') {
                    content += '<h4>🎯 Interactive Quiz</h4>';
                    // Parse and render the quiz content
                    try {
                        const quizData = JSON.parse(version.content_text);
                        content += renderQuizContent(quizData);
                    } catch (e) {
                        console.error('Failed to parse quiz data:', e);
                        content += '<p style="margin-top: 10px; color: var(--error-500);">Error loading quiz content. Please try regenerating.</p>';
                    }
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
            adjustQuizLevel();
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

// ==================== QUIZ SUBMISSION & AI FEEDBACK ====================
function submitQuizAnswer(questionId, quizType) {
    const questionEl = document.querySelector(`.quiz-question[data-question-id="${questionId}"]`);
    if (!questionEl) return;
    
    const answerEl = questionEl.querySelector('.student-answer');
    const feedbackEl = questionEl.querySelector('.feedback-area');
    const answer = answerEl ? answerEl.value.trim() : '';
    
    if (!answer) {
        showNotification('Please enter an answer first!');
        return;
    }
    
    // Show submission feedback
    feedbackEl.style.display = 'block';
    feedbackEl.style.background = 'var(--blue-50)';
    feedbackEl.style.borderLeft = '4px solid var(--primary-500)';
    feedbackEl.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">✅</span>
            <div>
                <p style="font-weight: 600; margin: 0;">Answer Submitted!</p>
                <p style="margin: 5px 0 0; font-size: 0.95em;">Your response has been saved. Click "Get AI Check" for detailed feedback.</p>
            </div>
        </div>
    `;
    
    showNotification('Answer submitted successfully!');
}

async function getAIFeedback(questionId, quizType) {
    const questionEl = document.querySelector(`.quiz-question[data-question-id="${questionId}"]`);
    if (!questionEl) {
        console.error('Question element not found for ID:', questionId);
        return;
    }
    
    const answerEl = questionEl.querySelector('.student-answer');
    const feedbackEl = questionEl.querySelector('.feedback-area');
    const answer = answerEl ? answerEl.value.trim() : '';
    
    if (!answer) {
        showNotification('Please enter an answer first!');
        return;
    }
    
    // Get the correct answer from the current quiz data
    let correctAnswer = null;
    let questionData = null;
    
    console.log('Current assignment:', state.currentAssignment);
    
    if (state.currentAssignment && state.currentAssignment.versions) {
        const quizVersion = state.currentAssignment.versions.find(v => v.variant_type === 'quiz');
        console.log('Quiz version:', quizVersion);
        
        if (quizVersion) {
            try {
                const quizData = JSON.parse(quizVersion.content_text);
                console.log('Quiz data:', quizData);
                console.log('Question ID:', questionId);
                
                const questions = quizData.questions || [];
                console.log('Questions array:', questions);
                
                questionData = questions[questionId];
                console.log('Question data:', questionData);
                
                // Try multiple possible answer field names
                if (questionData) {
                    correctAnswer = questionData.answer || questionData.correct_answer;
                    
                    // If no answer field, try to extract from solution field
                    if (!correctAnswer && questionData.solution) {
                        // Try to extract answer from solution text
                        // Common patterns: "So, the answer is X", "Therefore X", "= X", etc.
                        const solution = questionData.solution;
                        
                        // Pattern 1: "So, the factored form is (x + 3)(x + 6)"
                        let match = solution.match(/(?:So,?\s+(?:the\s+)?(?:answer|result|factored form|solution)\s+is\s+)(.+?)(?:\.|$)/i);
                        
                        // Pattern 2: "Therefore, x = 4"
                        if (!match) {
                            match = solution.match(/(?:Therefore,?\s+)(.+?)(?:\.|$)/i);
                        }
                        
                        // Pattern 3: Last sentence or expression after "="
                        if (!match) {
                            const lastSentence = solution.split('.').filter(s => s.trim()).pop();
                            match = lastSentence ? lastSentence.match(/=\s*(.+)$/) : null;
                        }
                        
                        correctAnswer = match ? match[1].trim() : null;
                    }
                } else {
                    correctAnswer = null;
                }
                
                console.log('Correct answer:', correctAnswer);
            } catch (e) {
                console.error('Error parsing quiz data:', e);
            }
        } else {
            console.warn('No quiz version found in assignment versions');
        }
    } else {
        console.warn('No current assignment or versions available');
    }
    
    // Show loading state
    feedbackEl.style.display = 'block';
    feedbackEl.style.background = 'var(--gray-100)';
    feedbackEl.style.borderLeft = '4px solid var(--primary-500)';
    feedbackEl.innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 32px; margin-bottom: 10px;">🤖</div>
            <p style="margin: 0;">AI is analyzing your answer...</p>
        </div>
    `;
    
    // Simulate AI feedback (replace with actual API call to Gemini)
    setTimeout(() => {
        const feedback = generateAIFeedback(answer, quizType, correctAnswer, questionData);
        
        // Determine if answer is correct
        const isCorrect = correctAnswer ? checkAnswerCorrectness(answer, correctAnswer) : null;
        
        console.log('Answer check - Student:', answer, 'Correct:', correctAnswer, 'Is Correct:', isCorrect);
        
        // Style based on correctness
        let bgColor = 'var(--gray-50)';
        let borderColor = 'var(--gray-500)';
        
        if (isCorrect === true) {
            bgColor = 'var(--success-50)';
            borderColor = 'var(--success-500)';
        } else if (isCorrect === false) {
            bgColor = 'var(--warning-50)';
            borderColor = 'var(--warning-500)';
        }
        
        feedbackEl.style.background = bgColor;
        feedbackEl.style.borderLeft = `4px solid ${borderColor}`;
        feedbackEl.innerHTML = `
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <span style="font-size: 28px;">🤖</span>
                    <h6 style="margin: 0; color: var(--gray-800);">AI Feedback</h6>
                </div>
                <div style="background: white; padding: 15px; border-radius: 6px; line-height: 1.6;">
                    ${feedback}
                </div>
            </div>
        `;
    }, 1500);
}

function checkAnswerCorrectness(studentAnswer, correctAnswer) {
    if (!correctAnswer) return null;
    
    // Normalize both answers for comparison
    const normalize = (str) => str.toString().toLowerCase().trim()
        .replace(/[^\w\s]/g, '') // Remove punctuation
        .replace(/\s+/g, ' ');   // Normalize spaces
    
    const normalizedStudent = normalize(studentAnswer);
    const normalizedCorrect = normalize(correctAnswer);
    
    // Exact match
    if (normalizedStudent === normalizedCorrect) return true;
    
    // Check if student answer contains the correct answer (for longer responses)
    if (normalizedStudent.includes(normalizedCorrect)) return true;
    
    // For numeric answers, check numerical equality
    const studentNum = parseFloat(studentAnswer);
    const correctNum = parseFloat(correctAnswer);
    if (!isNaN(studentNum) && !isNaN(correctNum)) {
        return Math.abs(studentNum - correctNum) < 0.01; // Allow small rounding errors
    }
    
    return false;
}

function generateAIFeedback(answer, quizType, correctAnswer, questionData) {
    // Check if answer is correct
    const isCorrect = correctAnswer ? checkAnswerCorrectness(answer, correctAnswer) : null;
    
    // Generate feedback based on correctness and quiz type
    if (quizType === 'socratic') {
        // Socratic questions are open-ended, provide thoughtful feedback
        return `
            <p><strong>🤔 Thoughtful Response!</strong> You're engaging with the question meaningfully.</p>
            <p><strong>💡 Consider:</strong> How does your answer connect to the broader concept? Can you think of examples that support your reasoning?</p>
            <p><strong>🎯 Next Step:</strong> Try to elaborate on the implications of your answer. What real-world applications can you think of?</p>
        `;
    }
    
    if (isCorrect === true) {
        // Answer is CORRECT
        const correctFeedback = {
            'practice': `
                <p><strong>🎉 Excellent work!</strong> Your answer is correct!</p>
                <p><strong>✓ You got it:</strong> ${escapeHtml(correctAnswer)}</p>
                <p><strong>💪 Great job!</strong> You've demonstrated a solid understanding of this concept. Keep up the excellent work!</p>
                ${questionData?.solution ? `<p><strong>📝 Solution approach:</strong> ${escapeHtml(questionData.solution)}</p>` : ''}
            `,
            'practice_repeatable': `
                <p><strong>🎉 Perfect!</strong> Your answer is absolutely correct!</p>
                <p><strong>✓ Correct answer:</strong> ${escapeHtml(correctAnswer)}</p>
                <p><strong>🌟 Outstanding!</strong> You've mastered this concept. Ready for the next challenge?</p>
                ${questionData?.explanation ? `<p><strong>� Why it's correct:</strong> ${escapeHtml(questionData.explanation)}</p>` : ''}
            `
        };
        return correctFeedback[quizType] || correctFeedback['practice_repeatable'];
        
    } else if (isCorrect === false) {
        // Answer is INCORRECT
        const incorrectFeedback = {
            'practice': `
                <p><strong>🤔 Not quite right.</strong> Let's work through this together.</p>
                <p><strong>❌ Your answer:</strong> ${escapeHtml(answer)}</p>
                <p><strong>✓ Correct answer:</strong> ${escapeHtml(correctAnswer)}</p>
                <p><strong>� Tip:</strong> Review the problem step-by-step. ${questionData?.common_mistakes ? `Common mistakes include: ${questionData.common_mistakes.join(', ')}.` : 'Make sure you understand each part before moving forward.'}</p>
                ${questionData?.solution ? `<p><strong>📝 How to solve it:</strong> ${escapeHtml(questionData.solution)}</p>` : ''}
                <p><strong>🔄 Try again!</strong> Understanding mistakes is a key part of learning.</p>
            `,
            'practice_repeatable': `
                <p><strong>🤔 Not quite there yet.</strong> That's okay - learning takes practice!</p>
                <p><strong>❌ Your answer:</strong> ${escapeHtml(answer)}</p>
                <p><strong>✓ Correct answer:</strong> ${escapeHtml(correctAnswer)}</p>
                ${questionData?.explanation ? `<p><strong>📚 Explanation:</strong> ${escapeHtml(questionData.explanation)}</p>` : ''}
                ${questionData?.real_world_example ? `<p><strong>🌍 Real-world context:</strong> ${escapeHtml(questionData.real_world_example)}</p>` : ''}
                <p><strong>💪 Keep trying!</strong> Review the explanation and give it another shot!</p>
            `
        };
        return incorrectFeedback[quizType] || incorrectFeedback['practice_repeatable'];
        
    } else {
        // No correct answer available (shouldn't happen often)
        return `
            <p><strong>📝 Your answer:</strong> ${escapeHtml(answer)}</p>
            <p><strong>💡 Feedback:</strong> Your response shows engagement with the material. Keep thinking critically!</p>
            <p><strong>🎯 Tip:</strong> Compare your answer with the provided solution to verify your understanding.</p>
        `;
    }
}

// ==================== ADJUST LEVEL (REGENERATE QUIZ) ====================
async function adjustQuizLevel() {
    if (!state.currentAssignment) {
        showNotification('No assignment loaded!');
        return;
    }
    
    // Ask user for difficulty level
    const difficulty = prompt('Choose difficulty level:\n- easy\n- medium\n- hard\n\nEnter your choice:', 'medium');
    
    if (!difficulty || !['easy', 'medium', 'hard'].includes(difficulty.toLowerCase())) {
        if (difficulty !== null) {  // User didn't cancel
            showNotification('Invalid difficulty level. Please choose: easy, medium, or hard');
        }
        return;
    }
    
    const confirmed = confirm(`This will regenerate the quiz at ${difficulty.toLowerCase()} difficulty level. Continue?`);
    if (!confirmed) return;
    
    showNotification('Regenerating quiz questions...');
    
    // Call API to regenerate quiz variant
    try {
        const response = await fetch(`/api/assignments/${state.currentAssignment.id}/regenerate/quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty: difficulty.toLowerCase() })
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification('Quiz regenerated successfully!');
            // Reload the assignment to show new quiz
            setTimeout(() => window.location.reload(), 1000);
        } else {
            const error = await response.json();
            showNotification(`Failed to regenerate quiz: ${error.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error regenerating quiz:', error);
        showNotification('Error regenerating quiz. Please try again.');
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
