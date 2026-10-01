/* ==========================================================================
   AI Technical Error Analysis System - Client JavaScript App logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    initTabs();
    initSamplePills();
    initAnalyzeForm();
    initDropzones();
    initCopyButtons();
    initSettingsForm();
    initKBForm();
});

// Tab Switcher
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const target = this.getAttribute('data-tab');
            const parent = this.closest('.tab-container') || document;
            
            parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            parent.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            this.classList.add('active');
            const content = parent.querySelector(`#${target}`);
            if (content) content.classList.add('active');
        });
    });
}

// Pre-fill Sample Error Buttons
function initSamplePills() {
    const pills = document.querySelectorAll('.sample-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', function () {
            const rawError = this.getAttribute('data-error');
            const codeContext = this.getAttribute('data-code');
            const framework = this.getAttribute('data-framework');

            const errorTextarea = document.getElementById('raw_error');
            const codeTextarea = document.getElementById('code_context');
            const frameworkSelect = document.getElementById('framework');

            if (errorTextarea) errorTextarea.value = rawError;
            if (codeTextarea) codeTextarea.value = codeContext || '';
            if (frameworkSelect && framework) frameworkSelect.value = framework;

            // Switch to paste tab if in file mode
            const pasteTabBtn = document.querySelector('[data-tab="tab-paste"]');
            if (pasteTabBtn) pasteTabBtn.click();
        });
    });
}

// Drag & Drop File Uploads
function initDropzones() {
    const dropzone = document.getElementById('file-dropzone');
    const fileInput = document.getElementById('error_file');
    const filePreview = document.getElementById('file-preview-info');

    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', function () {
            if (this.files.length > 0) {
                filePreview.innerHTML = `<i class="fa-solid fa-file-code"></i> File selected: <strong>${this.files[0].name}</strong> (${(this.files[0].size/1024).toFixed(1)} KB)`;
            }
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                filePreview.innerHTML = `<i class="fa-solid fa-file-code"></i> File uploaded: <strong>${files[0].name}</strong>`;
            }
        });
    }
}

// Main Analyze Error Form Submission
function initAnalyzeForm() {
    const form = document.getElementById('analyze-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const spinner = document.getElementById('analysis-spinner');
        const resultsCard = document.getElementById('analysis-results');

        if (spinner) spinner.style.display = 'block';
        if (resultsCard) resultsCard.style.display = 'none';

        fetch('/api/analyze/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (spinner) spinner.style.display = 'none';
            if (data.success) {
                renderAnalysisResults(data.data);
            } else {
                alert('Error performing analysis: ' + (data.error || 'Unknown server error'));
            }
        })
        .catch(err => {
            if (spinner) spinner.style.display = 'none';
            alert('Request failed: ' + err.message);
        });
    });
}

// Render Analysis Output Card
function renderAnalysisResults(data) {
    const resultsCard = document.getElementById('analysis-results');
    if (!resultsCard) return;

    document.getElementById('res-title').textContent = data.title;
    document.getElementById('res-ai-badge').textContent = data.ai_model_used || 'Smart RAG';
    document.getElementById('res-explanation').textContent = data.explanation;
    document.getElementById('res-root-cause').textContent = data.root_cause;

    // Solution steps
    const stepsList = document.getElementById('res-solution-steps');
    stepsList.innerHTML = '';
    if (data.solution_steps && data.solution_steps.length > 0) {
        data.solution_steps.forEach(step => {
            const li = document.createElement('li');
            li.textContent = step;
            stepsList.appendChild(li);
        });
    } else {
        stepsList.innerHTML = '<li>Inspect code logic and configuration options.</li>';
    }

    // Code suggestion
    const codeBox = document.getElementById('res-code-suggestion');
    const codeWrapper = document.getElementById('res-code-wrapper');
    if (data.code_suggestion && data.code_suggestion.trim() !== '') {
        codeBox.textContent = data.code_suggestion;
        codeWrapper.style.display = 'block';
    } else {
        codeWrapper.style.display = 'none';
    }

    // RAG Citations
    const ragContainer = document.getElementById('res-rag-citations');
    ragContainer.innerHTML = '';
    if (data.matched_kb_items && data.matched_kb_items.length > 0) {
        data.matched_kb_items.forEach(kb => {
            const cit = document.createElement('div');
            cit.className = 'rag-citation-card';
            cit.innerHTML = `
                <div class="rag-citation-header">
                    <span><i class="fa-solid fa-book-bookmark"></i> KB Reference: <strong>${kb.title}</strong> (${kb.category})</span>
                    <span class="rag-match-score">Match Score: ${(kb.similarity_score * 100).toFixed(0)}%</span>
                </div>
                <div style="font-size:0.85rem; margin-top:0.4rem; color: #9ca3af;">${kb.explanation}</div>
            `;
            ragContainer.appendChild(cit);
        });
    } else {
        ragContainer.innerHTML = '<div style="font-size:0.85rem; color:#6b7280;">No direct pre-seeded KB article match; generated using AI synthesis.</div>';
    }

    resultsCard.style.display = 'block';
    resultsCard.scrollIntoView({ behavior: 'smooth' });
}

// Copy Code Snippet
function initCopyButtons() {
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('code-copy-btn')) {
            const codeBlock = e.target.closest('.code-box-wrapper').querySelector('.code-content');
            if (codeBlock) {
                navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                    const origText = e.target.textContent;
                    e.target.textContent = 'Copied!';
                    setTimeout(() => e.target.textContent = origText, 2000);
                });
            }
        }
    });
}

// System Settings Save
function initSettingsForm() {
    const form = document.getElementById('settings-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/api/settings/save/', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.reload();
            } else {
                alert('Error saving settings: ' + data.error);
            }
        });
    });
}

// Knowledge Base Add Form
function initKBForm() {
    const form = document.getElementById('add-kb-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/api/knowledge-base/add/', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.reload();
            } else {
                alert('Error adding KB item: ' + data.error);
            }
        });
    });
}

// Open Analysis History Detail Modal
function openHistoryModal(logId) {
    fetch(`/api/history/${logId}/`)
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            const log = res.data;
            document.getElementById('modal-title').textContent = log.title;
            document.getElementById('modal-meta').textContent = `${log.framework} | ${log.created_at} | Engine: ${log.ai_model_used}`;
            document.getElementById('modal-raw-error').textContent = log.raw_error;
            document.getElementById('modal-explanation').textContent = log.explanation;
            document.getElementById('modal-root-cause').textContent = log.root_cause;
            
            const stepsUl = document.getElementById('modal-solution-steps');
            stepsUl.innerHTML = '';
            if (log.solution_steps) {
                log.solution_steps.forEach(s => {
                    const li = document.createElement('li');
                    li.textContent = s;
                    stepsUl.appendChild(li);
                });
            }

            document.getElementById('modal-code-suggestion').textContent = log.code_suggestion || '// No specific code snippet provided.';
            document.getElementById('modal-export-md').href = `/api/history/${log.id}/export/?format=md`;
            document.getElementById('modal-export-json').href = `/api/history/${log.id}/export/?format=json`;

            document.getElementById('history-modal').classList.add('active');
        }
    });
}

function closeHistoryModal() {
    const modal = document.getElementById('history-modal');
    if (modal) modal.classList.remove('active');
}
