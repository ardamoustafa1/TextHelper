/**
 * Chat Renderer - Sohbet Görüntüleyici
 * Mesajları ve sohbet arayüzünü render eder
 */

class ChatRenderer {
    constructor(containerElement) {
        this.container = containerElement;
        this.messages = [];

        // Konfigürasyon
        this.config = {
            maxMessages: 100,
            animateMessages: true,
            showTimestamps: true,
            groupMessages: true,
            typingIndicatorDuration: 1000
        };

        // Typing indicator
        this.typingTimeout = null;
    }

    /**
     * Mesaj ekle
     * @param {Object} message - Mesaj objesi
     */
    addMessage(message) {
        const messageData = {
            id: message.id || Date.now().toString(36) + Math.random().toString(36).substr(2),
            text: message.text,
            type: message.type || 'outgoing', // 'outgoing' veya 'incoming'
            timestamp: message.timestamp || new Date(),
            sender: message.sender || 'Agent',
            status: message.status || 'sent'
        };

        this.messages.push(messageData);

        // Limiti kontrol et
        if (this.messages.length > this.config.maxMessages) {
            this.messages.shift();
            this._removeFirstMessage();
        }

        // DOM'a ekle
        this._renderMessage(messageData);

        // Scroll to bottom
        this._scrollToBottom();

        return messageData;
    }

    /**
     * Mesajı render et
     */
    _renderMessage(message) {
        // Karşılama mesajını kaldır
        const welcomeMessage = this.container.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}`;
        messageElement.dataset.messageId = message.id;

        if (this.config.animateMessages) {
            messageElement.style.animation = 'messageIn 0.3s ease';
        }

        const formattedTime = this._formatTime(message.timestamp);
        const statusIcon = message.type === 'outgoing' ? '<i class="fas fa-check-double"></i>' : '';

        messageElement.innerHTML = `
            <div class="message-bubble">
                <p class="message-text">${this._escapeHtml(message.text)}</p>
                <span class="message-time">
                    ${formattedTime}
                    ${statusIcon}
                </span>
            </div>
        `;

        this.container.appendChild(messageElement);
    }

    /**
     * İlk mesajı kaldır
     */
    _removeFirstMessage() {
        const firstMessage = this.container.querySelector('.message');
        if (firstMessage) {
            firstMessage.remove();
        }
    }

    /**
     * Zaman formatla
     */
    _formatTime(date) {
        const d = new Date(date);
        return d.toLocaleTimeString('tr-TR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * HTML escape
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    /**
     * En alta scroll
     */
    _scrollToBottom() {
        const parent = this.container.closest('.messages-container');
        if (parent) {
            setTimeout(() => {
                parent.scrollTop = parent.scrollHeight;
            }, 50);
        }
    }

    /**
     * Yazıyor göstergesi göster
     */
    showTypingIndicator() {
        let indicator = this.container.querySelector('.typing-message');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'message incoming typing-message';
            indicator.innerHTML = `
                <div class="message-bubble typing-bubble">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            this.container.appendChild(indicator);
        }

        this._scrollToBottom();
    }

    /**
     * Yazıyor göstergesini gizle
     */
    hideTypingIndicator() {
        const indicator = this.container.querySelector('.typing-message');
        if (indicator) {
            indicator.remove();
        }
    }

    /**
     * Tüm mesajları temizle
     */
    clearMessages() {
        this.messages = [];
        this.container.innerHTML = '';

        // Karşılama mesajını tekrar göster
        this._showWelcomeMessage();
    }

    /**
     * Karşılama mesajını göster
     */
    _showWelcomeMessage() {
        const welcomeHtml = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <i class="fas fa-comments"></i>
                </div>
                <h3>TextHelper'a Hoş Geldiniz!</h3>
                <p>Yazmaya başlayın, akıllı öneriler otomatik olarak görünecek.</p>
                <div class="tips">
                    <div class="tip">
                        <i class="fas fa-keyboard"></i>
                        <span><strong>Tab</strong> veya <strong>Enter</strong> ile öneriyi kabul edin</span>
                    </div>
                    <div class="tip">
                        <i class="fas fa-arrow-up"></i>
                        <span><strong>↑↓</strong> tuşları ile öneriler arasında gezinin</span>
                    </div>
                    <div class="tip">
                        <i class="fas fa-slash"></i>
                        <span><strong>/</strong> ile şablon komutlarını kullanın</span>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = welcomeHtml;
    }

    /**
     * Mesaj güncelle
     */
    updateMessage(messageId, updates) {
        const message = this.messages.find(m => m.id === messageId);
        if (message) {
            Object.assign(message, updates);

            const element = this.container.querySelector(`[data-message-id="${messageId}"]`);
            if (element) {
                const textElement = element.querySelector('.message-text');
                if (textElement && updates.text) {
                    textElement.innerHTML = this._escapeHtml(updates.text);
                }
            }
        }
    }

    /**
     * Mesaj sil
     */
    deleteMessage(messageId) {
        const index = this.messages.findIndex(m => m.id === messageId);
        if (index !== -1) {
            this.messages.splice(index, 1);

            const element = this.container.querySelector(`[data-message-id="${messageId}"]`);
            if (element) {
                element.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => element.remove(), 300);
            }
        }
    }

    /**
     * Mesaj sayısını al
     */
    getMessageCount() {
        return this.messages.length;
    }

    /**
     * Tüm mesajları al
     */
    getMessages() {
        return [...this.messages];
    }

    /**
     * Son mesajı al
     */
    getLastMessage() {
        return this.messages[this.messages.length - 1] || null;
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.ChatRenderer = ChatRenderer;
}
