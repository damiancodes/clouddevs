document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('chat-icon');
    const chatContainer = document.getElementById('chat-container');
    const closeChat = document.getElementById('close-chat');
    const userMessageInput = document.getElementById('user-message');
    const sendMessageBtn = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle chat widget
    chatIcon.addEventListener('click', function() {
        chatContainer.classList.remove('d-none');
    });

    closeChat.addEventListener('click', function() {
        chatContainer.classList.add('d-none');
    });

    // Send message function
    function sendMessage() {
        const message = userMessageInput.value.trim();

        if (message !== '') {
            // Add user message to chat
            addMessage(message, 'user');

            // Clear input
            userMessageInput.value = '';

            // Send to backend (will implement fully later)
            fetch('/chat/api/send-message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                // For now, just echo back a placeholder response
                setTimeout(() => {
                    addMessage("Thanks for your message! Our AI assistant will respond shortly.", 'bot');
                }, 500);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        const messagePara = document.createElement('p');
        messagePara.textContent = text;

        messageDiv.appendChild(messagePara);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Send message on button click
    sendMessageBtn.addEventListener('click', sendMessage);

    // Send message on Enter key
    userMessageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});