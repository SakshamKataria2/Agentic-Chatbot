const modelSelect = document.getElementById('model-select');
const apiKeyInput = document.getElementById('api-key-input');
const chatWindow = document.getElementById('chat-window');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

let chatHistory = [];

// Handle Dynamic API Key Input Visibility
modelSelect.addEventListener('change', (e) => {
    const model = e.target.value;
    
    if (model === 'claude') {
        apiKeyInput.style.display = 'block';
        apiKeyInput.placeholder = 'Enter Claude API Key...';
    } else if (model === 'groq') {
        apiKeyInput.style.display = 'block';
        apiKeyInput.placeholder = 'Enter Groq API Key...';
    } else {
        // Gemini uses server-side .env, Ollama is local
        apiKeyInput.style.display = 'none'; 
    }
    
    // Clear chat when switching models to prevent context mixing
    chatHistory = []; 
    chatWindow.innerHTML = ''; 
    appendMessage(`Switched to ${modelSelect.options[modelSelect.selectedIndex].text}`, 'bot');
});

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    const model = modelSelect.value;
    const dynamicKey = apiKeyInput.value.trim();

    if ((model === 'claude' || model === 'groq') && !dynamicKey) {
        alert(`Please enter your ${model} API key first.`);
        return;
    }

    appendMessage(text, 'user');
    messageInput.value = '';
    
    const loadingId = Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot');
    loadingDiv.id = `load-${loadingId}`;
    loadingDiv.textContent = 'Thinking...';
    chatWindow.appendChild(loadingDiv);

    try {
        const response = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: text, 
                model: model, 
                dynamic_key: (model === 'claude' || model === 'groq') ? dynamicKey : null,
                history: chatHistory
            })
        });

        const data = await response.json();
        document.getElementById(`load-${loadingId}`).remove();

        if (response.ok) {
            chatHistory.push({ role: 'user', content: text });

            if (data.action) {
                handleAgentAction(data.action, data.payload);
                chatHistory.push({ role: 'assistant', content: `[Action performed: ${data.action}]` });
            } else {
                appendMessage(data.reply, 'bot');
                chatHistory.push({ role: 'assistant', content: data.reply });
            }
        } else {
            appendMessage(`Error: ${data.detail}`, 'bot');
        }
    } catch (error) {
        document.getElementById(`load-${loadingId}`).remove();
        appendMessage('Failed to connect to the server.', 'bot');
    }
}

function handleAgentAction(action, payload) {
    if (action === 'open_tab') {
        window.open(payload, '_blank');
        appendMessage(`I have opened ${payload} in a new tab.`, 'bot');
    } else if (action === 'change_color') {
        document.body.style.backgroundColor = payload;
        appendMessage(`Interface color updated to ${payload}.`, 'bot');
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});