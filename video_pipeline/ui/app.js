// Video RAG Chat Application

const chatContainer = document.getElementById('chat-container');
const inputForm = document.getElementById('input-form');
const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');

let hasMessages = false;

// Handle form submission
inputForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = questionInput.value.trim();
    if (question) {
        await askQuestion(question);
        questionInput.value = '';
    }
});

// Example question handler
function askExample(question) {
    askQuestion(question);
}

// Ask question and display answer
async function askQuestion(question) {
    // Remove welcome message on first question
    if (!hasMessages) {
        chatContainer.innerHTML = '';
        hasMessages = true;
    }
    
    // Add user message
    addMessage(question, 'user');
    
    // Disable input while loading
    setLoading(true);
    
    // Add loading message
    const loadingId = addMessage('<span class="loading"></span> Thinking...', 'assistant', 'loading');
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                limit: 10
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add answer
        addAnswer(data);
        
    } catch (error) {
        // Remove loading message
        removeMessage(loadingId);
        
        // Add error message
        addMessage(`Error: ${error.message}`, 'error');
    }
    
    setLoading(false);
    questionInput.focus();
}

// Add message to chat
function addMessage(text, type, id = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    if (id) messageDiv.id = id;
    messageDiv.innerHTML = text;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return messageDiv.id;
}

// Add answer with sources
function addAnswer(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    // Add LLM status indicator
    let statusBadge = '';
    if (data.llm_used) {
        statusBadge = '<div style="font-size:0.75rem;color:#2c5530;margin-bottom:0.5rem;">✨ AI-generated answer</div>';
    } else {
        statusBadge = '<div style="font-size:0.75rem;color:#c60;margin-bottom:0.5rem;">📄 Transcript excerpts (LLM unavailable)</div>';
    }
    
    let html = statusBadge + `<div style="white-space:pre-wrap;">${escapeHtml(data.answer)}</div>`;
    
    if (data.sources && data.sources.length > 0) {
        html += '<div class="sources">';
        html += '<h4>📖 Sources</h4>';
        data.sources.slice(0, 5).forEach((source, i) => {
            html += `<div class="source-item">`;
            html += `<strong>Video ${i + 1}:</strong> ${escapeHtml(source.video_id)} @ ${escapeHtml(source.timestamp)}`;
            html += `</div>`;
        });
        html += '</div>';
    }
    
    messageDiv.innerHTML = html;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Remove message by ID
function removeMessage(id) {
    const msg = document.getElementById(id);
    if (msg) msg.remove();
}

// Set loading state
function setLoading(loading) {
    sendBtn.disabled = loading;
    questionInput.disabled = loading;
    if (!loading) {
        questionInput.focus();
    }
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Focus input on load
questionInput.focus();
