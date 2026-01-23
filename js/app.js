/**
 * TextHelper - Ana Uygulama
 * WhatsApp/VS Code tarzı akıllı otomatik tamamlama sistemi
 */

class TextHelperApp {
    constructor() {
        // DOM Elemanları
        this.elements = {
            // Input
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            charCount: document.getElementById('charCount'),
            typingIndicator: document.getElementById('typingIndicator'),

            // Autocomplete
            autocompleteDropdown: document.getElementById('autocompleteDropdown'),
            suggestionsList: document.getElementById('suggestionsList'),

            // Chat
            messagesWrapper: document.getElementById('messagesWrapper'),
            messagesContainer: document.getElementById('messagesContainer'),

            // Panels
            settingsPanel: document.getElementById('settingsPanel'),
            templatePanel: document.getElementById('templatePanel'),
            templateCategories: document.getElementById('templateCategories'),

            // Buttons
            settingsBtn: document.getElementById('settingsBtn'),
            closeSettingsBtn: document.getElementById('closeSettingsBtn'),
            templateBtn: document.getElementById('templateBtn'),
            closeTemplateBtn: document.getElementById('closeTemplateBtn'),
            clearChatBtn: document.getElementById('clearChatBtn'),
            emojiBtn: document.getElementById('emojiBtn'),
            newChatBtn: document.getElementById('newChatBtn'),

            // Settings
            autoSuggestToggle: document.getElementById('autoSuggestToggle'),
            learnHistoryToggle: document.getElementById('learnHistoryToggle'),
            darkModeToggle: document.getElementById('darkModeToggle'),
            suggestionCountRange: document.getElementById('suggestionCountRange'),
            suggestionCountValue: document.getElementById('suggestionCountValue')
        };

        // Modüller
        this.autocompleteEngine = null;
        this.suggestionDropdown = null;
        this.keyboardHandler = null;
        this.chatRenderer = null;

        // State
        this.maxCharCount = 2000;
        this.isTyping = false;
        this.typingTimeout = null;

        // Başlat
        this._initialize();
    }

    /**
     * Uygulamayı başlat
     */
    _initialize() {
        console.log('TextHelper initializing...');

        // Modülleri oluştur
        this._initializeModules();

        // Event listener'ları bağla
        this._bindEvents();

        // Şablon panelini doldur
        this._populateTemplatePanel();

        // Ayarları yükle
        this._loadSettings();

        // Textarea auto-resize
        this._setupTextareaAutoResize();

        console.log('TextHelper initialized successfully!');
    }

    /**
     * Modülleri başlat
     */
    _initializeModules() {
        // Autocomplete Engine
        if (typeof AutocompleteEngine !== 'undefined') {
            this.autocompleteEngine = new AutocompleteEngine({
                maxSuggestions: 7,
                debounceMs: 50,
                autoLearn: true
            });

            // Input'a bağla
            this.autocompleteEngine.attach(this.elements.messageInput);

            // Öneri güncellemelerini dinle
            this.autocompleteEngine.onSuggestionsUpdate = (suggestions, selectedIndex) => {
                this._handleSuggestionsUpdate(suggestions, selectedIndex);
            };

            this.autocompleteEngine.onSuggestionSelect = (suggestion) => {
                this._handleSuggestionSelect(suggestion);
            };
        }

        // Suggestion Dropdown
        if (typeof SuggestionDropdown !== 'undefined') {
            this.suggestionDropdown = new SuggestionDropdown(
                this.elements.autocompleteDropdown,
                this.elements.suggestionsList
            );

            this.suggestionDropdown.onItemClick = (index, suggestion) => {
                this.autocompleteEngine.selectSuggestion(index);
            };
        }

        // Keyboard Handler
        if (typeof KeyboardHandler !== 'undefined' && this.autocompleteEngine && this.suggestionDropdown) {
            this.keyboardHandler = new KeyboardHandler(
                this.elements.messageInput,
                this.autocompleteEngine,
                this.suggestionDropdown
            );

            this.keyboardHandler.onSendMessage = () => {
                this._sendMessage();
            };

            this.keyboardHandler.onToggleSuggestions = () => {
                this._toggleSuggestions();
            };
        }

        // Chat Renderer
        if (typeof ChatRenderer !== 'undefined') {
            this.chatRenderer = new ChatRenderer(this.elements.messagesWrapper);
        }
    }

    /**
     * Event listener'ları bağla
     */
    _bindEvents() {
        // Send button
        this.elements.sendBtn.addEventListener('click', () => {
            this._sendMessage();
        });

        // Character count
        this.elements.messageInput.addEventListener('input', () => {
            this._updateCharCount();
            this._showTypingIndicator();
        });

        // Settings panel
        this.elements.settingsBtn.addEventListener('click', () => {
            this._toggleSettingsPanel();
        });

        this.elements.closeSettingsBtn.addEventListener('click', () => {
            this._toggleSettingsPanel(false);
        });

        // Template panel
        this.elements.templateBtn.addEventListener('click', () => {
            this._toggleTemplatePanel();
        });

        this.elements.closeTemplateBtn.addEventListener('click', () => {
            this._toggleTemplatePanel(false);
        });

        // Clear chat
        this.elements.clearChatBtn.addEventListener('click', () => {
            this._clearChat();
        });

        // Emoji button (placeholder)
        this.elements.emojiBtn.addEventListener('click', () => {
            this._insertEmoji('😊');
        });

        // New chat
        this.elements.newChatBtn.addEventListener('click', () => {
            this._clearChat();
        });

        // Settings toggles
        this.elements.autoSuggestToggle.addEventListener('change', (e) => {
            this._updateSetting('autoSuggest', e.target.checked);
        });

        this.elements.learnHistoryToggle.addEventListener('change', (e) => {
            this._updateSetting('learnHistory', e.target.checked);
        });

        this.elements.darkModeToggle.addEventListener('change', (e) => {
            this._updateSetting('darkMode', e.target.checked);
        });

        this.elements.suggestionCountRange.addEventListener('input', (e) => {
            const value = e.target.value;
            this.elements.suggestionCountValue.textContent = value;
            this._updateSetting('suggestionCount', parseInt(value));
        });

        // Paneller dışına tıklama
        document.addEventListener('click', (e) => {
            if (!this.elements.settingsPanel.contains(e.target) &&
                !this.elements.settingsBtn.contains(e.target)) {
                this._toggleSettingsPanel(false);
            }

            if (!this.elements.templatePanel.contains(e.target) &&
                !this.elements.templateBtn.contains(e.target)) {
                this._toggleTemplatePanel(false);
            }
        });
    }

    /**
     * Öneri güncellemelerini işle
     */
    _handleSuggestionsUpdate(suggestions, selectedIndex) {
        if (this.suggestionDropdown) {
            if (suggestions.length > 0) {
                this.suggestionDropdown.show(suggestions, selectedIndex);
            } else {
                this.suggestionDropdown.hide();
            }
        }
    }

    /**
     * Öneri seçimini işle
     */
    _handleSuggestionSelect(suggestion) {
        // Focus'u input'a geri ver
        this.elements.messageInput.focus();

        // Karakter sayısını güncelle
        this._updateCharCount();
    }

    /**
     * Mesaj gönder
     */
    _sendMessage() {
        const text = this.elements.messageInput.value.trim();

        if (!text) return;

        // Chat'e ekle
        if (this.chatRenderer) {
            this.chatRenderer.addMessage({
                text: text,
                type: 'outgoing'
            });
        }

        // Autocomplete'e bildir (öğrenme için)
        if (this.autocompleteEngine) {
            this.autocompleteEngine.onMessageSent(text);
        }

        // Input'u temizle
        this.elements.messageInput.value = '';
        this._updateCharCount();
        this._resetTextareaHeight();

        // Typing indicator'ı gizle
        this._hideTypingIndicator();

        // Simüle edilmiş yanıt (demo amaçlı)
        this._simulateResponse(text);
    }

    /**
     * Simüle edilmiş yanıt (demo)
     */
    _simulateResponse(userMessage) {
        // Typing indicator göster
        setTimeout(() => {
            if (this.chatRenderer) {
                this.chatRenderer.showTypingIndicator();
            }
        }, 500);

        // Yanıt
        setTimeout(() => {
            if (this.chatRenderer) {
                this.chatRenderer.hideTypingIndicator();

                // Basit yanıt mantığı
                let response = 'Mesajınız alındı, size yardımcı olmaktan memnuniyet duyarım.';

                const lowerMessage = userMessage.toLowerCase();

                if (lowerMessage.includes('merhaba') || lowerMessage.includes('selam')) {
                    response = 'Merhaba! Size nasıl yardımcı olabilirim?';
                } else if (lowerMessage.includes('teşekkür')) {
                    response = 'Rica ederim, her zaman yardımcı olmaktan memnuniyet duyarım!';
                } else if (lowerMessage.includes('görüşürüz') || lowerMessage.includes('hoşçakal')) {
                    response = 'Görüşmek üzere, iyi günler dilerim!';
                } else if (lowerMessage.includes('sipariş')) {
                    response = 'Siparişiniz hakkında bilgi almak için sipariş numaranızı paylaşır mısınız?';
                } else if (lowerMessage.includes('sorun') || lowerMessage.includes('problem')) {
                    response = 'Yaşadığınız sorunu anlıyorum. Size yardımcı olmak için detaylı bilgi alabilir miyim?';
                }

                this.chatRenderer.addMessage({
                    text: response,
                    type: 'incoming'
                });
            }
        }, 1500);
    }

    /**
     * Karakter sayısını güncelle
     */
    _updateCharCount() {
        const length = this.elements.messageInput.value.length;
        this.elements.charCount.textContent = `${length} / ${this.maxCharCount}`;

        if (length > this.maxCharCount * 0.9) {
            this.elements.charCount.style.color = '#f87171';
        } else {
            this.elements.charCount.style.color = '';
        }
    }

    /**
     * Typing indicator göster
     */
    _showTypingIndicator() {
        this.elements.typingIndicator.classList.add('visible');

        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }

        this.typingTimeout = setTimeout(() => {
            this._hideTypingIndicator();
        }, 2000);
    }

    /**
     * Typing indicator gizle
     */
    _hideTypingIndicator() {
        this.elements.typingIndicator.classList.remove('visible');
    }

    /**
     * Textarea auto-resize
     */
    _setupTextareaAutoResize() {
        this.elements.messageInput.addEventListener('input', () => {
            this._autoResizeTextarea();
        });
    }

    /**
     * Textarea boyutunu ayarla
     */
    _autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }

    /**
     * Textarea yüksekliğini sıfırla
     */
    _resetTextareaHeight() {
        this.elements.messageInput.style.height = 'auto';
    }

    /**
     * Önerileri toggle et
     */
    _toggleSuggestions() {
        if (this.suggestionDropdown?.isOpen()) {
            this.suggestionDropdown.hide();
        } else if (this.autocompleteEngine) {
            // Manuel tetikleme - mevcut input ile
            const suggestions = this.autocompleteEngine.predictionService?.predict(
                this.elements.messageInput.value
            ) || [];

            if (suggestions.length > 0 && this.suggestionDropdown) {
                this.suggestionDropdown.show(suggestions, 0);
            }
        }
    }

    /**
     * Ayarlar panelini toggle et
     */
    _toggleSettingsPanel(show = null) {
        const isVisible = this.elements.settingsPanel.classList.contains('visible');
        const shouldShow = show !== null ? show : !isVisible;

        if (shouldShow) {
            this.elements.settingsPanel.classList.add('visible');
            this._toggleTemplatePanel(false);
        } else {
            this.elements.settingsPanel.classList.remove('visible');
        }
    }

    /**
     * Şablon panelini toggle et
     */
    _toggleTemplatePanel(show = null) {
        const isVisible = this.elements.templatePanel.classList.contains('visible');
        const shouldShow = show !== null ? show : !isVisible;

        if (shouldShow) {
            this.elements.templatePanel.classList.add('visible');
            this._toggleSettingsPanel(false);
        } else {
            this.elements.templatePanel.classList.remove('visible');
        }
    }

    /**
     * Şablon panelini doldur
     */
    _populateTemplatePanel() {
        if (typeof CustomerServiceTemplates === 'undefined') return;

        const container = this.elements.templateCategories;
        container.innerHTML = '';

        Object.entries(CustomerServiceTemplates).forEach(([key, category]) => {
            const categoryElement = document.createElement('div');
            categoryElement.className = 'template-category';

            const header = document.createElement('div');
            header.className = 'template-category-header';
            header.innerHTML = `
                <i class="${category.icon}"></i>
                <span>${category.name}</span>
                <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 0.8rem;"></i>
            `;

            header.addEventListener('click', () => {
                categoryElement.classList.toggle('expanded');
            });

            const items = document.createElement('div');
            items.className = 'template-items';

            category.templates.forEach(template => {
                const item = document.createElement('div');
                item.className = 'template-item';
                item.textContent = template.description;
                item.title = template.text;

                item.addEventListener('click', () => {
                    this._insertTemplate(template);
                    this._toggleTemplatePanel(false);
                });

                items.appendChild(item);
            });

            categoryElement.appendChild(header);
            categoryElement.appendChild(items);
            container.appendChild(categoryElement);
        });
    }

    /**
     * Şablon ekle
     */
    _insertTemplate(template) {
        if (this.autocompleteEngine) {
            this.autocompleteEngine.insertTemplate(template);
        } else {
            this.elements.messageInput.value = template.text;
            this._updateCharCount();
            this._autoResizeTextarea();
        }

        this.elements.messageInput.focus();
    }

    /**
     * Emoji ekle
     */
    _insertEmoji(emoji) {
        const input = this.elements.messageInput;
        const start = input.selectionStart;
        const end = input.selectionEnd;
        const text = input.value;

        input.value = text.substring(0, start) + emoji + text.substring(end);
        input.selectionStart = input.selectionEnd = start + emoji.length;

        this._updateCharCount();
        input.focus();
    }

    /**
     * Sohbeti temizle
     */
    _clearChat() {
        if (this.chatRenderer) {
            this.chatRenderer.clearMessages();
        }
    }

    /**
     * Ayar güncelle
     */
    _updateSetting(key, value) {
        const settings = this._getSettings();
        settings[key] = value;
        localStorage.setItem('texthelper_settings', JSON.stringify(settings));

        // Ayarı uygula
        this._applySetting(key, value);
    }

    /**
     * Ayarları yükle
     */
    _loadSettings() {
        const settings = this._getSettings();

        // Toggle'ları ayarla
        this.elements.autoSuggestToggle.checked = settings.autoSuggest !== false;
        this.elements.learnHistoryToggle.checked = settings.learnHistory !== false;
        this.elements.darkModeToggle.checked = settings.darkMode !== false;
        this.elements.suggestionCountRange.value = settings.suggestionCount || 5;
        this.elements.suggestionCountValue.textContent = settings.suggestionCount || 5;

        // Ayarları uygula
        Object.entries(settings).forEach(([key, value]) => {
            this._applySetting(key, value);
        });
    }

    /**
     * Ayarları al
     */
    _getSettings() {
        try {
            return JSON.parse(localStorage.getItem('texthelper_settings')) || {};
        } catch {
            return {};
        }
    }

    /**
     * Ayarı uygula
     */
    _applySetting(key, value) {
        switch (key) {
            case 'autoSuggest':
                if (this.autocompleteEngine) {
                    this.autocompleteEngine.setEnabled(value);
                }
                break;

            case 'learnHistory':
                if (this.autocompleteEngine) {
                    this.autocompleteEngine.updateConfig({ autoLearn: value });
                }
                break;

            case 'darkMode':
                // Varsayılan olarak dark mode aktif, light mode için ek CSS gerekir
                break;

            case 'suggestionCount':
                if (this.autocompleteEngine) {
                    this.autocompleteEngine.updateConfig({ maxSuggestions: value });
                }
                break;
        }
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    window.textHelperApp = new TextHelperApp();
});
