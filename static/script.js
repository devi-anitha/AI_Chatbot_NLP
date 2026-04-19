document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const clearBtn = document.getElementById('clear-chat');
    const sendBtn = document.getElementById('send-btn');
    const themeSelector = document.getElementById('theme-selector');

    // Theme Switcher Event
    themeSelector.addEventListener('change', (e) => {
        document.documentElement.setAttribute('data-theme', e.target.value);
    });

    // Local state for chat history
    let messages = [];

    // Load initial welcome message
    initChat();

    function initChat() {
        const welcomeMsg = "Hello! I'm your AI assistant. How can I help you today?";
        addMessage('bot', welcomeMsg);
    }

    // Capture form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const messageText = userInput.value.trim();
        if (!messageText) return;

        // Clear input and disable button temporarily
        userInput.value = '';
        toggleSendButton(false);

        // Add user message to UI
        addMessage('user', messageText);

        // Show typing indicator
        const typingId = showTypingIndicator();

        try {
            // Make AJAX POST request to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: messageText })
            });

            const data = await response.json();
            
            // Remove typing indicator and add bot response
            removeTypingIndicator(typingId);
            
            if (response.ok) {
                addMessage('bot', data.response);
            } else {
                addMessage('bot', data.response || "Server error occurred.");
            }
        } catch (error) {
            console.error("Fetch error:", error);
            removeTypingIndicator(typingId);
            addMessage('bot', "Network error. Please make sure the backend is running.");
        } finally {
            toggleSendButton(true);
            userInput.focus();
        }
    });

    // Clear chat logic
    clearBtn.addEventListener('click', () => {
        if (confirm("Are you sure you want to clear the conversation?")) {
            chatWindow.innerHTML = '';
            messages = [];
            initChat();
        }
    });

    // Utility: Enable/Disable submit button based on input
    userInput.addEventListener('input', () => {
        toggleSendButton(userInput.value.trim().length > 0);
    });

    function toggleSendButton(enabled) {
        sendBtn.disabled = !enabled;
    }

    function addMessage(sender, text) {
        messages.push({ sender, text, timestamp: new Date() });

        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${sender}`;
        
        // Avatar
        const avatar = document.createElement('img');
        avatar.className = 'avatar-micro';
        avatar.src = sender === 'user' ? '/static/images/user_avatar.png' : '/static/images/bot_avatar.png';
        avatar.alt = sender;

        // Content Wrapper
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Bubble
        const bubble = document.createElement('div');
        bubble.className = 'message';
        bubble.textContent = text; 

        // Timestamp
        const timeLab = document.createElement('span');
        timeLab.className = 'timestamp';
        const now = new Date();
        timeLab.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        contentDiv.appendChild(bubble);
        contentDiv.appendChild(timeLab);
        
        if (sender === 'user') {
            wrapper.appendChild(avatar);
            wrapper.appendChild(contentDiv);
        } else {
            wrapper.appendChild(avatar);
            wrapper.appendChild(contentDiv);
        }
        
        chatWindow.appendChild(wrapper);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper bot';
        wrapper.id = typingId;

        const avatar = document.createElement('img');
        avatar.className = 'avatar-micro';
        avatar.src = '/static/images/bot_avatar.png';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message typing-indicator';
        
        bubble.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;

        contentDiv.appendChild(bubble);
        wrapper.appendChild(avatar);
        wrapper.appendChild(contentDiv);

        chatWindow.appendChild(wrapper);
        scrollToBottom();

        return typingId;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});
