document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearBtn = document.getElementById('clear-chat');

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        // Enable/disable send button
        if(this.value.trim().length > 0) {
            sendBtn.removeAttribute('disabled');
        } else {
            sendBtn.setAttribute('disabled', 'true');
        }
    });

    // Handle Enter to send (Shift+Enter for newline)
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim().length > 0) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Handle Form Submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const messageText = userInput.value.trim();
        if (!messageText) return;

        // Reset input
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.setAttribute('disabled', 'true');

        // Add User Message to UI
        appendMessage(messageText, 'user');
        
        // Show Typing Indicator
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            // Call FastAPI Backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText })
            });

            const data = await response.json();
            
            // Hide Typing Indicator
            typingIndicator.classList.add('hidden');
            
            if (response.ok) {
                // Formatting text response lightly if basic markdown is present
                // Simple bolding formatting (Groq output often has **text**)
                let formattedReply = escapeHtml(data.reply).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                // Simple new line handling
                formattedReply = formattedReply.replace(/\n/g, '<br/>');
                
                appendMessage(formattedReply, 'bot', true);
            } else {
                appendMessage("Ndjesë, ndodhi një gabim në server me API-n.", 'bot');
            }
        } catch (error) {
            console.error("Fetch error:", error);
            typingIndicator.classList.add('hidden');
            appendMessage("Gabim rrjeti. Ju lutem kontrolloni lidhjen tuaj.", 'bot');
        }
    });

    // Clear Chat
    clearBtn.addEventListener('click', () => {
        // Keep only the first welcome message
        const welcomeMessage = messagesContainer.firstElementChild;
        messagesContainer.innerHTML = '';
        if(welcomeMessage) messagesContainer.appendChild(welcomeMessage);
    });

    function appendMessage(content, sender, isHtml = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`, 'entry-anim');

        let avatar = '';
        if (sender === 'user') {
            avatar = `<div class="avatar user-avatar">Ti</div>`;
        } else {
            avatar = `<div class="avatar bot-avatar">EJ</div>`;
        }

        const messageContentDiv = document.createElement('div');
        messageContentDiv.classList.add('message-content');
        
        if (isHtml) {
            messageContentDiv.innerHTML = `<p>${content}</p>`;
        } else {
            const p = document.createElement('p');
            p.textContent = content; // Safely append text
            messageContentDiv.appendChild(p);
        }

        // Add to DOM based on sender
        if (sender === 'user') {
            messageDiv.appendChild(messageContentDiv);
            messageDiv.appendChild(document.createRange().createContextualFragment(avatar));
        } else {
            messageDiv.appendChild(document.createRange().createContextualFragment(avatar));
            messageDiv.appendChild(messageContentDiv);
        }

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        const chatWindow = document.querySelector('.chat-window');
        chatWindow.scrollTo({
            top: chatWindow.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Utility to escape HTML to prevent XSS if we render it later
    function escapeHtml(unsafe) {
        return (unsafe || "")
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});
