// API Base URL
const API_BASE = '';

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const questionInput = document.getElementById('question-input');
const sendButton = document.getElementById('send-button');
const sourceFilter = document.getElementById('source-filter');
const statusDiv = document.getElementById('status');

const pdfUpload = document.getElementById('pdf-upload');
const uploadPdfButton = document.getElementById('upload-pdf-button');
const pdfStatus = document.getElementById('pdf-status');

const confluenceSpace = document.getElementById('confluence-space');
const confluenceLimit = document.getElementById('confluence-limit');
const loadConfluenceButton = document.getElementById('load-confluence-button');
const confluenceStatus = document.getElementById('confluence-status');

const slackChannel = document.getElementById('slack-channel');
const slackDays = document.getElementById('slack-days');
const loadSlackButton = document.getElementById('load-slack-button');
const slackStatus = document.getElementById('slack-status');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    
    // Event listeners
    sendButton.addEventListener('click', sendQuestion);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendQuestion();
    });
    
    uploadPdfButton.addEventListener('click', uploadPDFs);
    loadConfluenceButton.addEventListener('click', loadConfluence);
    loadSlackButton.addEventListener('click', loadSlack);
});

// Load system status
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        statusDiv.innerHTML = `
            <strong>System Status:</strong> ${data.status} | 
            <strong>Documents:</strong> ${data.document_count} | 
            <strong>Confluence:</strong> ${data.confluence_configured ? '✓' : '✗'} | 
            <strong>Slack:</strong> ${data.slack_configured ? '✓' : '✗'}
        `;
        statusDiv.style.background = '#d4edda';
        statusDiv.style.color = '#155724';
    } catch (error) {
        statusDiv.innerHTML = '❌ Unable to connect to server';
        statusDiv.style.background = '#f8d7da';
        statusDiv.style.color = '#721c24';
    }
}

// Send question
async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;
    
    // Add user message
    addMessage(question, 'user');
    questionInput.value = '';
    
    // Disable input
    sendButton.disabled = true;
    questionInput.disabled = true;
    
    // Add loading message
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                source_type: sourceFilter.value || null
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add assistant message
        addMessage(data.answer, 'assistant', data.sources);
        
    } catch (error) {
        removeMessage(loadingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        console.error('Error:', error);
    } finally {
        sendButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }
}

// Add message to chat
function addMessage(content, type, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    let html = `<div class="message-content">${escapeHtml(content)}</div>`;
    
    if (sources && sources.length > 0) {
        html += '<div class="sources"><strong>📚 Sources:</strong>';
        sources.forEach((source, idx) => {
            html += `
                <div class="source-item">
                    <div><strong>Source ${idx + 1}:</strong> ${escapeHtml(source.metadata.source || 'Unknown')}</div>
                    <div class="source-meta">Type: ${source.metadata.source_type || 'unknown'}</div>
                    ${source.metadata.page ? `<div class="source-meta">Page: ${source.metadata.page}</div>` : ''}
                    ${source.metadata.url ? `<div class="source-meta"><a href="${source.metadata.url}" target="_blank">View Source</a></div>` : ''}
                </div>
            `;
        });
        html += '</div>';
    }
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv.id = `msg-${Date.now()}`;
}

// Add loading message
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    const id = `msg-${Date.now()}`;
    messageDiv.id = id;
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = '<div class="message-content"><div class="loading"></div> Thinking...</div>';
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

// Remove message
function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) message.remove();
}

// Upload PDFs
async function uploadPDFs() {
    const files = pdfUpload.files;
    if (files.length === 0) {
        showStatus(pdfStatus, 'Please select PDF files to upload', 'error');
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    uploadPdfButton.disabled = true;
    showStatus(pdfStatus, 'Uploading and processing PDFs...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/api/upload/pdf`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        showStatus(pdfStatus, `✓ ${data.message}. Added ${data.documents_added} documents.`, 'success');
        pdfUpload.value = '';
        loadStatus();
        
    } catch (error) {
        showStatus(pdfStatus, `✗ Error: ${error.message}`, 'error');
    } finally {
        uploadPdfButton.disabled = false;
    }
}

// Load Confluence
async function loadConfluence() {
    const spaceKey = confluenceSpace.value.trim();
    if (!spaceKey) {
        showStatus(confluenceStatus, 'Please enter a Confluence space key', 'error');
        return;
    }
    
    const limit = parseInt(confluenceLimit.value) || 100;
    
    loadConfluenceButton.disabled = true;
    showStatus(confluenceStatus, 'Loading from Confluence...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/api/load/confluence`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                space_key: spaceKey,
                limit: limit
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load Confluence data');
        }
        
        const data = await response.json();
        showStatus(confluenceStatus, `✓ ${data.message}. Added ${data.documents_added} documents.`, 'success');
        confluenceSpace.value = '';
        loadStatus();
        
    } catch (error) {
        showStatus(confluenceStatus, `✗ Error: ${error.message}`, 'error');
    } finally {
        loadConfluenceButton.disabled = false;
    }
}

// Load Slack
async function loadSlack() {
    const channelId = slackChannel.value.trim();
    if (!channelId) {
        showStatus(slackStatus, 'Please enter a Slack channel ID', 'error');
        return;
    }
    
    const days = parseInt(slackDays.value) || 30;
    
    loadSlackButton.disabled = true;
    showStatus(slackStatus, 'Loading from Slack...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/api/load/slack`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                channel_id: channelId,
                days: days,
                limit: 1000
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load Slack data');
        }
        
        const data = await response.json();
        showStatus(slackStatus, `✓ ${data.message}. Added ${data.documents_added} documents.`, 'success');
        slackChannel.value = '';
        loadStatus();
        
    } catch (error) {
        showStatus(slackStatus, `✗ Error: ${error.message}`, 'error');
    } finally {
        loadSlackButton.disabled = false;
    }
}

// Show status message
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
