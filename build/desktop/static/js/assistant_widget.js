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
        // Ana container oluştur
        this.container = document.createElement('div');
        this.container.className = 'finasis-assistant-container';
        document.body.appendChild(this.container);

        // Yardım butonu
        const helpButton = document.createElement('button');
        helpButton.className = 'finasis-assistant-button';
        helpButton.innerHTML = '🧠 Yardım mı lazım?';
        helpButton.onclick = () => this.toggleChat();
        this.container.appendChild(helpButton);

        // Chat penceresi
        this.createChatWindow();
    }

    createChatWindow() {
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'finasis-assistant-chat';
        this.chatWindow.style.display = 'none';

        // Mesaj alanı
        this.messageContainer = document.createElement('div');
        this.messageContainer.className = 'finasis-assistant-messages';
        this.chatWindow.appendChild(this.messageContainer);

        // Input alanı
        const inputContainer = document.createElement('div');
        inputContainer.className = 'finasis-assistant-input-container';

        this.inputField = document.createElement('input');
        this.inputField.type = 'text';
        this.inputField.placeholder = 'Mesajınızı yazın...';
        this.inputField.onkeypress = (e) => {
            if (e.key === 'Enter') this.sendMessage();
        };

        const sendButton = document.createElement('button');
        sendButton.innerHTML = '📤';
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

        // Kullanıcı mesajını göster
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
                this.addMessage('Üzgünüm, bir hata oluştu: ' + data.error, false);
            } else {
                this.sessionId = data.session_id;
                this.addMessage(data.reply, false);
            }
        } catch (error) {
            this.addMessage('Bağlantı hatası oluştu. Lütfen tekrar deneyin.', false);
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
            console.error('Chat geçmişi yüklenemedi:', error);
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

// Sayfa yüklendiğinde asistanı başlat
document.addEventListener('DOMContentLoaded', () => {
    window.finasisAssistant = new FinAsisAssistant();
}); 