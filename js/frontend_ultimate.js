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
            maxSuggestions: config.maxSuggestions || 80,
            ...config
        };

        this.ws = null;
        this.inputElement = null;
        this.suggestionsContainer = null;
        this.ghostOverlay = null; // Ghost Text için overlay
        this.currentSuggestions = [];

        // Zero-Latency Cache
        this.cache = new Map();
        this.MAX_CACHE_SIZE = 500;

        // Smart Personalization
        this.userVocabulary = this.loadUserVocabulary();

        this.init();
    }

    init() {
        // WebSocket bağlantısı
        if (this.config.useWebSocket) {
            this.connectWebSocket();
        }
    }

    loadUserVocabulary() {
        try {
            const vocab = localStorage.getItem('texthelper_user_vocab');
            return vocab ? JSON.parse(vocab) : {};
        } catch (e) {
            console.warn('LocalStorage erişim hatası:', e);
            return {};
        }
    }

    saveUserVocabulary() {
        try {
            localStorage.setItem('texthelper_user_vocab', JSON.stringify(this.userVocabulary));
        } catch (e) {
            // Ignore storage errors
        }
    }

    getFromCache(key) {
        return this.cache.get(key);
    }

    addToCache(key, value) {
        if (this.cache.size >= this.MAX_CACHE_SIZE) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }

    /**
     * Input elementine bağla
     */
    attach(inputElement, suggestionsContainer) {
        this.inputElement = inputElement;
        this.suggestionsContainer = suggestionsContainer;

        // Ghost Text Overlay Oluştur
        this.createGhostOverlay();

        // Event listener'lar
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
            this.updateGhostText(); // Ghost text güncelle
        });

        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });

        // Scroll senkronizasyonu
        this.inputElement.addEventListener('scroll', () => {
            if (this.ghostOverlay) {
                this.ghostOverlay.scrollTop = this.inputElement.scrollTop;
                this.ghostOverlay.scrollLeft = this.inputElement.scrollLeft;
            }
        });
    }

    createGhostOverlay() {
        if (!this.inputElement || this.ghostOverlay) return;

        // Wrapper oluştur
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.width = '100%';

        this.inputElement.parentNode.insertBefore(wrapper, this.inputElement);
        wrapper.appendChild(this.inputElement);

        // Overlay oluştur
        this.ghostOverlay = document.createElement('div');
        this.ghostOverlay.className = 'ghost-overlay';
        this.ghostOverlay.style.position = 'absolute';
        this.ghostOverlay.style.top = '0';
        this.ghostOverlay.style.left = '0';
        this.ghostOverlay.style.width = '100%';
        this.ghostOverlay.style.height = '100%';
        this.ghostOverlay.style.pointerEvents = 'none'; // Tıklamaları input'a geçir
        this.ghostOverlay.style.color = 'transparent'; // Ana metin görünmez
        this.ghostOverlay.style.whiteSpace = 'pre-wrap';
        this.ghostOverlay.style.overflow = 'hidden';
        this.ghostOverlay.style.padding = window.getComputedStyle(this.inputElement).padding;
        this.ghostOverlay.style.font = window.getComputedStyle(this.inputElement).font;
        this.ghostOverlay.style.boxSizing = 'border-box';

        wrapper.appendChild(this.ghostOverlay);
    }

    updateGhostText() {
        if (!this.ghostOverlay || !this.currentSuggestions.length) {
            if (this.ghostOverlay) this.ghostOverlay.innerHTML = '';
            return;
        }

        const text = this.inputElement.value;
        const suggestion = this.currentSuggestions[0].text;

        // Eğer öneri, yazdığımız kelimeyle eşleşiyorsa
        const words = text.split(' ');
        const lastWord = words[words.length - 1];

        if (suggestion.toLowerCase().startsWith(lastWord.toLowerCase()) && lastWord.length > 0) {
            const completion = suggestion.substring(lastWord.length);
            // Ana metin (görünmez) + Ghost Text (gri)
            this.ghostOverlay.innerHTML = text.replace(/&/g, '&amp;').replace(/</g, '&lt;') +
                '<span style="color: #9ca3af;">' + completion + '</span>';
        } else {
            this.ghostOverlay.innerHTML = '';
        }
    }

    /**
     * WebSocket bağlantısı (Geliştirilmiş)
     */
    connectWebSocket() {
        if (this._wsConnecting) return;
        this._wsConnecting = true;
        this._reconnectAttempts = this._reconnectAttempts || 0;

        try {
            console.log(`WebSocket bağlanıyor... (${this.config.wsUrl})`);
            this.ws = new WebSocket(this.config.wsUrl);

            this.ws.onopen = () => {
                console.log('✅ WebSocket bağlantısı kuruldu');
                this._wsConnecting = false;
                this._reconnectAttempts = 0;

                // UI Feedback: Bağlandı
                if (this.suggestionsContainer) {
                    const statusEl = document.getElementById('ws-status-indicator');
                    if (statusEl) {
                        statusEl.className = 'status-connected';
                        statusEl.title = 'Sunucuya bağlı';
                    }
                }
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
                this._wsConnecting = false;

                // UI Feedback: Bağlantı Koptu
                if (this.suggestionsContainer) {
                    const statusEl = document.getElementById('ws-status-indicator');
                    if (statusEl) {
                        statusEl.className = 'status-disconnected';
                        statusEl.title = 'Bağlantı koptu - Yeniden bağlanılıyor...';
                    }
                }

                // Exponential backoff ile yeniden bağlan
                const timeout = Math.min(1000 * Math.pow(2, this._reconnectAttempts), 10000);
                this._reconnectAttempts++;
                console.log(`${timeout}ms sonra yeniden bağlanılacak...`);

                setTimeout(() => {
                    this.config.useWebSocket = true; // Tekrar dene
                    this.connectWebSocket();
                }, timeout);
            };
        } catch (error) {
            console.error('WebSocket bağlantı hatası:', error);
            this.config.useWebSocket = false;
            this._wsConnecting = false;
        }
    }

    /**
     * Son gelen mesajdan bağlam (context) çıkar
     */
    getContextFromLastMessage() {
        // Chat mesajlarını bul
        if (!this.suggestionsContainer) return "";

        // Chat container (textHelperApp yapısına bağlı)
        const chatContainer = document.getElementById('messagesContainer');
        if (!chatContainer) return "";

        const incomingMessages = chatContainer.querySelectorAll('.message.incoming .message-text');
        if (incomingMessages.length === 0) return "";

        const lastMessage = incomingMessages[incomingMessages.length - 1].textContent;
        return lastMessage;
    }

    /**
     * Input değiştiğinde (Geliştirilmiş - Context Aware)
     */
    async handleInput(text) {
        if (this._debounceTimer) {
            clearTimeout(this._debounceTimer);
        }

        if (!text && text.length === 0) {
            this.clearSuggestions();
            this.updateGhostText();
            return;
        }

        this._debounceTimer = setTimeout(async () => {
            // 1. Zero-Latency Cache Check
            const cached = this.getFromCache(text);
            if (cached) {
                console.log('[Cache] Hızlı yanıt (0ms)');
                this.handleSuggestions(cached);
                return;
            }

            // 2. Offline Mode (LocalStorage Fallback)
            if (!navigator.onLine) {
                console.log('[Offline] Çevrimdışı mod aktif');
                // Basit offline öneri (User Vocabulary'den)
                const words = text.split(' ');
                const lastWord = words[words.length - 1].toLowerCase();
                if (lastWord.length >= 2) {
                    const offlineSuggestions = Object.keys(this.userVocabulary)
                        .filter(w => w.startsWith(lastWord))
                        .sort((a, b) => this.userVocabulary[b] - this.userVocabulary[a]) // Frekansa göre azalan
                        .slice(0, 5)
                        .map(w => ({
                            text: w,
                            type: 'history',
                            score: 10,
                            description: 'Geçmiş (Offline)',
                            source: 'local'
                        }));

                    if (offlineSuggestions.length > 0) {
                        this.handleSuggestions({ suggestions: offlineSuggestions });
                        return;
                    }
                }
            }

            // Boş input olsa bile, son mesaja göre öneri getir (Contextual Reply)
            const contextMsg = this.getContextFromLastMessage();

            if (this.config.useWebSocket && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    text: text, // Boş olabilir
                    context_message: contextMsg, // YENİ: Önceki mesaj
                    max_suggestions: this.config.maxSuggestions,
                    use_ai: true,
                    use_search: true,
                    user_id: "default"
                }));
            } else {
                // REST API (Context desteği eklenmeli)
                // Şimdilik sadece text varsa
                if (text.trim().length > 0) {
                    await this.fetchSuggestions(text);
                }
            }
        }, 50);
    }

    /**
     * REST API ile önerileri al
     */
    async fetchSuggestions(text) {
        try {
            // New Enterprise API Endpoint
            const response = await fetch(`${this.config.apiUrl}/api/v1/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    // Context awareness for better predictions
                    context: this.getContextFromLastMessage()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Hata kontrolü
            if (!data || !data.suggestions) {
                console.warn('API yanıtı geçersiz:', data);
                this.clearSuggestions();
                return;
            }

            this.handleSuggestions(data);
        } catch (error) {
            console.error('API hatası:', error);
            // Hata durumunda önerileri temizle
            this.clearSuggestions();
            // Kullanıcıya hata göster (opsiyonel)
            if (this.suggestionsContainer) {
                this.suggestionsContainer.innerHTML = `<div style="color: #ff4444; padding: 10px;">Bağlantı hatası. Backend çalışıyor mu kontrol edin.</div>`;
            }
        }
    }

    /**
     * Önerileri işle ve göster
     */
    handleSuggestions(response) {
        // Cache'e kaydet (Input text'i response içinde yok, bu yüzden cache key'i tam bulamayabiliriz 
        // ama handleInput'ta text ile çağırıyoruz. Buraya text parametresi eklemek ideal olurdu ama
        // state üzerinden de gidebiliriz veya response'u genişletebiliriz.
        // Basitçe, eğer bu bir response ise ve suggestions varsa, son input değeri için cache'leyelim)

        if (this.inputElement && response.suggestions.length > 0) {
            const currentInput = this.inputElement.value;
            // Sadece son kelime için cache yapmak daha mantıklı olabilir ama şimdilik tam text
            this.addToCache(currentInput, response);
        }

        let suggestions = response.suggestions || [];

        // Smart Personalization: Kullanıcının sık kullandığı kelimeleri en üste taşı
        suggestions = suggestions.map(s => {
            const userFreq = this.userVocabulary[s.text.toLowerCase()] || 0;
            if (userFreq > 0) {
                s.score += (userFreq * 0.5); // Boost score based on usage
                s.description = s.description + ' (Sık kullanılan)';
            }
            return s;
        }).sort((a, b) => b.score - a.score);

        this.currentSuggestions = suggestions;

        console.log(`[DEBUG] ${this.currentSuggestions.length} öneri alındı:`, this.currentSuggestions);

        if (this.suggestionsContainer) {
            if (this.currentSuggestions.length > 0) {
                this.renderSuggestions(this.currentSuggestions);
            } else {
                // Öneri yoksa container'ı temizle
                this.suggestionsContainer.innerHTML = '';
            }

            // Ghost Text Güncelle
            this.updateGhostText();
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
     * Önerileri temizle
     */
    clearSuggestions() {
        this.currentSuggestions = [];
        if (this.suggestionsContainer) {
            this.suggestionsContainer.innerHTML = '';
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

        // ÖĞRENME: Seçilen öneriyi kaydet
        this.learnMessage(this.inputElement.value, suggestion.text);

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
            case 'Tab':
                if (this.currentSuggestions.length > 0) {
                    event.preventDefault();
                    this.selectSuggestion(0); // İlk öneriyi seç (Ghost Text)
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
    async learnMessage(message, selectedSuggestion = "") {
        try {
            // Eğer bir öneri seçildiyse onu da gönder
            const feedback = {
                text: message,
                selected_suggestion: selectedSuggestion,
                user_id: "default" // İleride gerçek user id eklenebilir
            };

            await fetch(`${this.config.apiUrl}/learn`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(feedback)
            });

            // Local Learning (Anında etki)
            if (selectedSuggestion) {
                const word = selectedSuggestion.toLowerCase();
                this.userVocabulary[word] = (this.userVocabulary[word] || 0) + 1;
                this.saveUserVocabulary();
            }

            console.log('[Frontend] Öğrenme sinyali gönderildi:', feedback);
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
