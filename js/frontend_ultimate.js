/**
 * TextHelper ULTIMATE Frontend
 * Python FastAPI backend'e bağlanır
 */

class TextHelperUltimate {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:8000',
            wsUrl: config.wsUrl || 'ws://localhost:8000/ws',
            useWebSocket: config.useWebSocket !== false,
            maxSuggestions: config.maxSuggestions || 7,
            ...config
        };

        this.ws = null;
        this.inputElement = null;
        this.suggestionsContainer = null;
        this.currentSuggestions = [];

        this.init();
    }

    init() {
        // WebSocket bağlantısı
        if (this.config.useWebSocket) {
            this.connectWebSocket();
        }
    }

    /**
     * Input elementine bağla
     */
    attach(inputElement, suggestionsContainer) {
        this.inputElement = inputElement;
        this.suggestionsContainer = suggestionsContainer;

        // Event listener'lar
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });

        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
    }

    /**
     * WebSocket bağlantısı
     */
    connectWebSocket() {
        try {
            this.ws = new WebSocket(this.config.wsUrl);

            this.ws.onopen = () => {
                console.log('✅ WebSocket bağlantısı kuruldu');
            };

            this.ws.onmessage = (event) => {
                const response = JSON.parse(event.data);
                this.handleSuggestions(response);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket hatası:', error);
                // Fallback: REST API kullan
                this.config.useWebSocket = false;
            };

            this.ws.onclose = () => {
                console.log('WebSocket bağlantısı kapandı');
                // Yeniden bağlanmayı dene
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        } catch (error) {
            console.error('WebSocket bağlantı hatası:', error);
            this.config.useWebSocket = false;
        }
    }

    /**
     * Input değiştiğinde
     */
    async handleInput(text) {
        if (!text || text.trim().length === 0) {
            this.clearSuggestions();
            return;
        }

        // WebSocket kullanıyorsa
        if (this.config.useWebSocket && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                text: text,
                max_suggestions: this.config.maxSuggestions
            }));
        } else {
            // REST API kullan
            await this.fetchSuggestions(text);
        }
    }

    /**
     * REST API ile önerileri al
     */
    async fetchSuggestions(text) {
        try {
            const response = await fetch(`${this.config.apiUrl}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    max_suggestions: this.config.maxSuggestions,
                    use_ai: true,
                    use_search: true
                })
            });

            const data = await response.json();
            this.handleSuggestions(data);
        } catch (error) {
            console.error('API hatası:', error);
        }
    }

    /**
     * Önerileri işle ve göster
     */
    handleSuggestions(response) {
        this.currentSuggestions = response.suggestions || [];

        if (this.suggestionsContainer) {
            this.renderSuggestions(this.currentSuggestions);
        }

        // Yazım düzeltmesi varsa göster
        if (response.corrected_text) {
            console.log('Yazım düzeltmesi:', response.corrected_text);
        }

        // İstatistikler
        if (response.processing_time_ms) {
            console.log(`İşlem süresi: ${response.processing_time_ms}ms`);
        }
    }

    /**
     * Önerileri render et
     */
    renderSuggestions(suggestions) {
        if (!this.suggestionsContainer) return;

        // Container'ı bul (autocompleteDropdown veya suggestionsList)
        const container = this.suggestionsContainer.closest('.autocomplete-dropdown') || this.suggestionsContainer;
        const listElement = this.suggestionsContainer.classList.contains('suggestions-list') 
            ? this.suggestionsContainer 
            : this.suggestionsContainer.querySelector('.suggestions-list') || this.suggestionsContainer;

        if (suggestions.length === 0) {
            if (listElement) listElement.innerHTML = '';
            container.classList.remove('visible');
            return;
        }

        const html = suggestions.map((sug, index) => `
            <div class="suggestion-item ${index === 0 ? 'active' : ''}" 
                 data-index="${index}"
                 onclick="textHelperUltimate.selectSuggestion(${index})">
                <div class="suggestion-icon ${sug.source}">
                    <i class="${this.getIcon(sug.type)}"></i>
                </div>
                <div class="suggestion-content">
                    <span class="suggestion-text">${this.escapeHtml(sug.text)}</span>
                    <span class="suggestion-meta">
                        ${sug.description} 
                        <span class="suggestion-source">(${sug.source})</span>
                    </span>
                </div>
                <div class="suggestion-score">${sug.score.toFixed(1)}</div>
            </div>
        `).join('');

        if (listElement) {
            listElement.innerHTML = html;
        } else {
            this.suggestionsContainer.innerHTML = html;
        }
        container.classList.add('visible');
    }

    /**
     * Öneri seç
     */
    selectSuggestion(index) {
        if (index < 0 || index >= this.currentSuggestions.length) return;

        const suggestion = this.currentSuggestions[index];

        // Metni güncelle
        if (this.inputElement) {
            const currentText = this.inputElement.value;
            const words = currentText.split(' ');
            words[words.length - 1] = suggestion.text;
            this.inputElement.value = words.join(' ');

            // Input event tetikle
            this.inputElement.dispatchEvent(new Event('input', { bubbles: true }));
        }

        // Önerileri temizle
        this.clearSuggestions();
    }

    /**
     * Klavye olayları
     */
    handleKeyDown(event) {
        if (this.currentSuggestions.length === 0) return;

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.moveSelection(1);
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.moveSelection(-1);
                break;
            case 'Enter':
            case 'Tab':
                if (this.currentSuggestions.length > 0) {
                    event.preventDefault();
                    this.selectSuggestion(0);
                }
                break;
            case 'Escape':
                this.clearSuggestions();
                break;
        }
    }

    /**
     * Seçimi hareket ettir
     */
    moveSelection(direction) {
        // Bu özellik UI'da implement edilmeli
        const items = this.suggestionsContainer?.querySelectorAll('.suggestion-item');
        if (!items) return;

        let currentIndex = 0;
        items.forEach((item, idx) => {
            if (item.classList.contains('active')) {
                currentIndex = idx;
            }
        });

        const newIndex = Math.max(0, Math.min(items.length - 1, currentIndex + direction));

        items.forEach((item, idx) => {
            item.classList.toggle('active', idx === newIndex);
        });
    }

    /**
     * İkon al
     */
    getIcon(type) {
        const icons = {
            'ai_prediction': 'fas fa-brain',
            'dictionary': 'fas fa-book',
            'spellcheck': 'fas fa-spell-check',
            'fuzzy': 'fas fa-search'
        };
        return icons[type] || 'fas fa-comment';
    }

    /**
     * HTML escape
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Önerileri temizle
     */
    clearSuggestions() {
        this.currentSuggestions = [];
        if (this.suggestionsContainer) {
            const container = this.suggestionsContainer.closest('.autocomplete-dropdown') || this.suggestionsContainer;
            const listElement = this.suggestionsContainer.classList.contains('suggestions-list') 
                ? this.suggestionsContainer 
                : this.suggestionsContainer.querySelector('.suggestions-list');
            
            if (listElement) {
                listElement.innerHTML = '';
            } else {
                this.suggestionsContainer.innerHTML = '';
            }
            container.classList.remove('visible');
        }
    }

    /**
     * Mesaj gönderildiğinde (öğrenme için)
     */
    async learnMessage(message) {
        try {
            await fetch(`${this.config.apiUrl}/learn`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: message })
            });
        } catch (error) {
            console.error('Öğrenme hatası:', error);
        }
    }
}

// Global instance
let textHelperUltimate = null;

// Başlatma fonksiyonu
function initTextHelperUltimate(config) {
    textHelperUltimate = new TextHelperUltimate(config);
    return textHelperUltimate;
}

// Export
if (typeof window !== 'undefined') {
    window.TextHelperUltimate = TextHelperUltimate;
    window.initTextHelperUltimate = initTextHelperUltimate;
    window.textHelperUltimate = null;
}
