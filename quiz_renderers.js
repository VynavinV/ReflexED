// Enhanced quiz display for subject-specific quiz types
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
            <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <h5 style="margin-bottom: 15px; color: var(--primary-700);">Question ${index + 1}</h5>
                <p style="font-size: 1.1em; margin-bottom: 15px;">${escapeHtml(q.question)}</p>
                
                <details style="margin-top: 15px; padding: 15px; background: var(--blue-50); border-radius: 4px; border-left: 4px solid var(--primary-500);">
                    <summary style="cursor: pointer; font-weight: 600; color: var(--primary-700);">💭 Guidance</summary>
                    <p style="margin-top: 10px; line-height: 1.6;">${escapeHtml(q.guidance || '')}</p>
                    ${q.follow_up ? `<p style="margin-top: 10px; font-style: italic;">Next: ${escapeHtml(q.follow_up)}</p>` : ''}
                </details>
                
                <div style="margin-top: 15px;">
                    <textarea placeholder="Your thoughts here..." style="width: 100%; min-height: 80px; padding: 10px; border-radius: 4px; border: 2px solid var(--gray-300); resize: vertical;"></textarea>
                </div>
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
            <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h5 style="margin: 0;">Problem ${index + 1}</h5>
                    <span style="background: ${difficultyColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; text-transform: uppercase;">${escapeHtml(q.difficulty || 'medium')}</span>
                </div>
                <p style="font-size: 1.1em; margin-bottom: 15px;">${escapeHtml(q.question)}</p>
                
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
            <div style="background: var(--gray-50); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <h5 style="margin-bottom: 15px;">Question ${index + 1}</h5>
                <p style="font-size: 1.1em; margin-bottom: 15px;">${escapeHtml(q.question)}</p>
                
                <div style="margin-bottom: 15px;">
                    <input type="text" placeholder="Your answer..." style="width: 100%; padding: 12px; border-radius: 4px; border: 2px solid var(--gray-300); font-size: 1em;">
                </div>
                
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
