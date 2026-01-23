/**
 * Autocomplete Engine - Ana Otomatik Tamamlama Motoru
 * Tüm bileşenleri koordine eder ve UI ile iletişim kurar
 */

class AutocompleteEngine {
    constructor(options = {}) {
        // Konfigürasyon
        this.config = {
            enabled: true,
            debounceMs: 30,  // Daha hızlı yanıt için azaltıldı
            minInputLength: 1,  // Tek harf yazınca da öneriler çıksın
            maxSuggestions: 7,
            autoLearn: true,
            ...options
        };

        // Bileşenler
        this.predictionService = null;
        this.backgroundService = null;

        // State
        this.currentInput = '';
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.isActive = false;

        // Debounce timer
        this.debounceTimer = null;

        // Callbacks
        this.onSuggestionsUpdate = null;
        this.onSuggestionSelect = null;
        this.onStateChange = null;

        // Input element referansı
        this.inputElement = null;

        // Başlat
        this._initialize();
    }

    /**
     * Motoru başlat
     */
    _initialize() {
        // BackgroundService oluştur (öncelikli)
        if (typeof BackgroundService !== 'undefined') {
            this.backgroundService = new BackgroundService();
            // BackgroundService içinde PredictionService var
            this.predictionService = this.backgroundService.predictionService;
        } else if (typeof PredictionService !== 'undefined') {
            // Fallback: Direkt PredictionService
            this.predictionService = new PredictionService();
        } else {
            console.error('PredictionService not found!');
        }

        console.log('AutocompleteEngine initialized');
    }

    /**
     * Input elementine bağla
     * @param {HTMLElement} inputElement - Textarea veya input elementi
     */
    attach(inputElement) {
        this.inputElement = inputElement;

        // Event listener'ları ekle
        this.inputElement.addEventListener('input', this._handleInput.bind(this));
        this.inputElement.addEventListener('keydown', this._handleKeyDown.bind(this));
        this.inputElement.addEventListener('focus', this._handleFocus.bind(this));
        this.inputElement.addEventListener('blur', this._handleBlur.bind(this));

        console.log('AutocompleteEngine attached to input element');
    }

    /**
     * Input elementinden ayır
     */
    detach() {
        if (this.inputElement) {
            this.inputElement.removeEventListener('input', this._handleInput);
            this.inputElement.removeEventListener('keydown', this._handleKeyDown);
            this.inputElement.removeEventListener('focus', this._handleFocus);
            this.inputElement.removeEventListener('blur', this._handleBlur);
            this.inputElement = null;
        }
    }

    /**
     * Input değiştiğinde
     */
    _handleInput(event) {
        if (!this.config.enabled) return;

        const input = event.target.value;
        this.currentInput = input;

        // Debounce ile tahmin yap
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        this.debounceTimer = setTimeout(() => {
            this._updateSuggestions();
        }, this.config.debounceMs);
    }

    /**
     * Önerileri güncelle
     */
    _updateSuggestions() {
        const input = this.currentInput;

        // Minimum uzunluk kontrolü
        if (input.length < this.config.minInputLength && !input.startsWith('/')) {
            this._clearSuggestions();
            return;
        }

        // BackgroundService kullanıyorsa
        if (this.backgroundService) {
            this.backgroundService.predict(input, (suggestions) => {
                this._handleSuggestions(suggestions);
            });
            
            // Önceden yükleme
            if (input.length >= 1) {
                this.backgroundService.prefetch(input);
            }
        } else if (this.predictionService) {
            // Fallback: Direkt tahmin
            const suggestions = this.predictionService.predict(input);
            this._handleSuggestions(suggestions);
        }
    }
    
    /**
     * Önerileri işle
     */
    _handleSuggestions(suggestions) {
        // Güncelle
        this.currentSuggestions = suggestions;
        this.selectedIndex = suggestions.length > 0 ? 0 : -1;
        this.isActive = suggestions.length > 0;

        // Callback
        if (this.onSuggestionsUpdate) {
            this.onSuggestionsUpdate(suggestions, this.selectedIndex);
        }

        this._triggerStateChange();
    }

    /**
     * Önerileri temizle
     */
    _clearSuggestions() {
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.isActive = false;

        if (this.onSuggestionsUpdate) {
            this.onSuggestionsUpdate([], -1);
        }

        this._triggerStateChange();
    }

    /**
     * Klavye olayları
     */
    _handleKeyDown(event) {
        if (!this.isActive || this.currentSuggestions.length === 0) return;

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this._moveSelection(1);
                break;

            case 'ArrowUp':
                event.preventDefault();
                this._moveSelection(-1);
                break;

            case 'Tab':
                if (this.currentSuggestions.length > 0) {
                    event.preventDefault();
                    this._acceptSuggestion(0);
                }
                break;

            case 'Enter':
                if (this.selectedIndex >= 0 && !event.shiftKey) {
                    event.preventDefault();
                    this._acceptSuggestion(this.selectedIndex);
                }
                break;

            case 'Escape':
                this._clearSuggestions();
                break;
        }
    }

    /**
     * Seçimi hareket ettir
     */
    _moveSelection(direction) {
        if (this.currentSuggestions.length === 0) return;

        let newIndex = this.selectedIndex + direction;

        // Döngüsel hareket
        if (newIndex < 0) {
            newIndex = this.currentSuggestions.length - 1;
        } else if (newIndex >= this.currentSuggestions.length) {
            newIndex = 0;
        }

        this.selectedIndex = newIndex;

        if (this.onSuggestionsUpdate) {
            this.onSuggestionsUpdate(this.currentSuggestions, this.selectedIndex);
        }
    }

    /**
     * Öneriyi kabul et
     */
    _acceptSuggestion(index) {
        if (index < 0 || index >= this.currentSuggestions.length) return;

        const suggestion = this.currentSuggestions[index];

        // Metni güncelle
        if (suggestion.replaceAll) {
            this._replaceAll(suggestion.text);
        } else if (suggestion.replaceWord) {
            this._replaceLastWord(suggestion.text);
        } else {
            this._insertText(suggestion.text);
        }

        // Callback
        if (this.onSuggestionSelect) {
            this.onSuggestionSelect(suggestion);
        }

        // Öğren
        if (this.config.autoLearn && this.predictionService) {
            // Seçilen öneriyi daha yüksek öncelikli yap
        }

        // Önerileri temizle
        this._clearSuggestions();
    }

    /**
     * Tüm metni değiştir
     */
    _replaceAll(text) {
        if (!this.inputElement) return;

        this.inputElement.value = text;
        this.currentInput = text;

        // Cursor'u sona taşı
        this.inputElement.selectionStart = text.length;
        this.inputElement.selectionEnd = text.length;

        // Input event tetikle
        this.inputElement.dispatchEvent(new Event('input', { bubbles: true }));
    }

    /**
     * Son kelimeyi değiştir
     */
    _replaceLastWord(text) {
        if (!this.inputElement) return;

        const currentText = this.inputElement.value;
        const words = currentText.split(/\s+/);
        words[words.length - 1] = text;

        const newText = words.join(' ');
        this.inputElement.value = newText;
        this.currentInput = newText;

        // Cursor'u sona taşı
        this.inputElement.selectionStart = newText.length;
        this.inputElement.selectionEnd = newText.length;

        // Input event tetikle
        this.inputElement.dispatchEvent(new Event('input', { bubbles: true }));
    }

    /**
     * Metin ekle
     */
    _insertText(text) {
        if (!this.inputElement) return;

        const currentText = this.inputElement.value;
        const newText = currentText + (currentText.endsWith(' ') ? '' : ' ') + text;

        this.inputElement.value = newText;
        this.currentInput = newText;

        // Cursor'u sona taşı
        this.inputElement.selectionStart = newText.length;
        this.inputElement.selectionEnd = newText.length;

        // Input event tetikle
        this.inputElement.dispatchEvent(new Event('input', { bubbles: true }));
    }

    /**
     * Focus olayı
     */
    _handleFocus(event) {
        // Focus olduğunda varsayılan önerileri göster
        if (this.inputElement.value.length === 0) {
            this._updateSuggestions();
        }
    }

    /**
     * Blur olayı
     */
    _handleBlur(event) {
        // Biraz bekle (suggestion click için)
        setTimeout(() => {
            this._clearSuggestions();
        }, 200);
    }

    /**
     * State değişikliği bildirimi
     */
    _triggerStateChange() {
        if (this.onStateChange) {
            this.onStateChange({
                isActive: this.isActive,
                suggestionsCount: this.currentSuggestions.length,
                selectedIndex: this.selectedIndex
            });
        }
    }

    /**
     * Mesaj gönderildiğinde
     */
    onMessageSent(message) {
        if (this.config.autoLearn) {
            if (this.backgroundService) {
                // Arka planda öğren
                this.backgroundService.learn(message);
            } else if (this.predictionService) {
                this.predictionService.learnFromMessage(message);
            }
        }

        this._clearSuggestions();
    }

    /**
     * Öneriyi programatik olarak seç
     */
    selectSuggestion(index) {
        this._acceptSuggestion(index);
    }

    /**
     * Şablon ekle
     */
    insertTemplate(template) {
        if (template && template.text) {
            this._replaceAll(template.text);
        }
    }

    /**
     * Motoru etkinleştir/devre dışı bırak
     */
    setEnabled(enabled) {
        this.config.enabled = enabled;

        if (!enabled) {
            this._clearSuggestions();
        }
    }

    /**
     * Konfigürasyonu güncelle
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }

    /**
     * Mevcut state'i al
     */
    getState() {
        return {
            isActive: this.isActive,
            currentInput: this.currentInput,
            suggestions: this.currentSuggestions,
            selectedIndex: this.selectedIndex,
            config: this.config
        };
    }

    /**
     * İstatistikler
     */
    getStats() {
        return this.predictionService?.getStats() || null;
    }

    /**
     * Tüm verileri temizle
     */
    clearAllData() {
        if (this.predictionService) {
            this.predictionService.clearCache();

            if (this.predictionService.historyManager) {
                this.predictionService.historyManager.clearAll();
            }
        }
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.AutocompleteEngine = AutocompleteEngine;
}
