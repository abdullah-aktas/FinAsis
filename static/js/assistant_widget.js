class FinAsisAssistant {
    constructor() {
        this.container = null;
        this.chatWindow = null;
        this.messageContainer = null;
        this.inputField = null;
        this.sessionId = null;
        this.isOpen = false;
        this.init();
    }

    init() {
        // Ana container oluÅŸtur
        this.container = document.createElement('div');
        this.container.className = 'finasis-assistant-container';
        document.body.appendChild(this.container);

        // YardÄ±m butonu
        const helpButton = document.createElement('button');
        helpButton.className = 'finasis-assistant-button';
        helpButton.innerHTML = 'ðŸ§  YardÄ±m mÄ± lazÄ±m?';
        helpButton.onclick = () => this.toggleChat();
        this.container.appendChild(helpButton);

        // Chat penceresi
        this.createChatWindow();
    }

    createChatWindow() {
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'finasis-assistant-chat';
        this.chatWindow.style.display = 'none';

        // Mesaj alanÄ±
        this.messageContainer = document.createElement('div');
        this.messageContainer.className = 'finasis-assistant-messages';
        this.chatWindow.appendChild(this.messageContainer);

        // Input alanÄ±
        const inputContainer = document.createElement('div');
        inputContainer.className = 'finasis-assistant-input-container';

        this.inputField = document.createElement('input');
        this.inputField.type = 'text';
        this.inputField.placeholder = 'MesajÄ±nÄ±zÄ± yazÄ±n...';
        this.inputField.onkeypress = (e) => {
            if (e.key === 'Enter') this.sendMessage();
        };

        const sendButton = document.createElement('button');
        sendButton.innerHTML = 'ðŸ“¤';
        sendButton.onclick = () => this.sendMessage();

        inputContainer.appendChild(this.inputField);
        inputContainer.appendChild(sendButton);
        this.chatWindow.appendChild(inputContainer);

        this.container.appendChild(this.chatWindow);
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatWindow.style.display = this.isOpen ? 'block' : 'none';
        
        if (this.isOpen) {
            this.inputField.focus();
            this.loadChatHistory();
        }
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // KullanÄ±cÄ± mesajÄ±nÄ± gÃ¶ster
        this.addMessage(message, true);
        this.inputField.value = '';

        try {
            const response = await fetch('/api/assistant/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message: message,
                    page_context: {
                        path: window.location.pathname,
                        title: document.title
                    }
                })
            });

            const data = await response.json();
            
            if (data.error) {
                this.addMessage('ÃœzgÃ¼nÃ¼m, bir hata oluÅŸtu: ' + data.error, false);
            } else {
                this.sessionId = data.session_id;
                this.addMessage(data.reply, false);
            }
        } catch (error) {
            this.addMessage('BaÄŸlantÄ± hatasÄ± oluÅŸtu. LÃ¼tfen tekrar deneyin.', false);
        }
    }

    async loadChatHistory() {
        if (!this.sessionId) return;

        try {
            const response = await fetch(`/api/assistant/history/${this.sessionId}/`);
            const data = await response.json();

            if (data.messages) {
                this.messageContainer.innerHTML = '';
                data.messages.forEach(msg => {
                    this.addMessage(msg.content, msg.is_user);
                });
            }
        } catch (error) {
            console.error('Chat geÃ§miÅŸi yÃ¼klenemedi:', error);
        }
    }

    addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `finasis-assistant-message ${isUser ? 'user' : 'assistant'}`;
        messageDiv.textContent = content;
        this.messageContainer.appendChild(messageDiv);
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Sayfa yÃ¼klendiÄŸinde asistanÄ± baÅŸlat
document.addEventListener('DOMContentLoaded', () => {
    window.finasisAssistant = new FinAsisAssistant();
}); 