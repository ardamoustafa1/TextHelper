/**
 * Keyboard Handler - Klavye İşleyici
 * Klavye kısayollarını ve navigasyonu yönetir
 */

class KeyboardHandler {
    constructor(inputElement, autocompleteEngine, suggestionDropdown) {
        this.input = inputElement;
        this.engine = autocompleteEngine;
        this.dropdown = suggestionDropdown;

        // Kısayol tanımları
        this.shortcuts = {
            'Tab': this._handleTab.bind(this),
            'Enter': this._handleEnter.bind(this),
            'Escape': this._handleEscape.bind(this),
            'ArrowUp': this._handleArrowUp.bind(this),
            'ArrowDown': this._handleArrowDown.bind(this),
            'Ctrl+Space': this._handleCtrlSpace.bind(this),
            'Ctrl+Enter': this._handleCtrlEnter.bind(this)
        };

        // Callbacks
        this.onSendMessage = null;
        this.onToggleSuggestions = null;

        // Event listener'ları bağla
        this._bindEvents();
    }

    /**
     * Event listener'ları bağla
     */
    _bindEvents() {
        this.input.addEventListener('keydown', this._handleKeyDown.bind(this));
    }

    /**
     * Keydown olayını işle
     */
    _handleKeyDown(event) {
        const key = this._getKeyCombo(event);
        const handler = this.shortcuts[key];

        if (handler) {
            handler(event);
        }
    }

    /**
     * Tuş kombinasyonunu al
     */
    _getKeyCombo(event) {
        const parts = [];

        if (event.ctrlKey) parts.push('Ctrl');
        if (event.altKey) parts.push('Alt');
        if (event.shiftKey) parts.push('Shift');

        parts.push(event.key);

        return parts.join('+');
    }

    /**
     * Tab tuşu - İlk öneriyi kabul et
     */
    _handleTab(event) {
        if (this.dropdown.isOpen() && this.dropdown.suggestions.length > 0) {
            event.preventDefault();
            this.engine.selectSuggestion(0);
        }
    }

    /**
     * Enter tuşu - Seçili öneriyi kabul et veya mesaj gönder
     */
    _handleEnter(event) {
        // Shift+Enter = yeni satır
        if (event.shiftKey) {
            return; // Varsayılan davranış
        }

        // Dropdown açıksa ve bir öğe seçiliyse
        if (this.dropdown.isOpen() && this.dropdown.selectedIndex >= 0) {
            event.preventDefault();
            this.engine.selectSuggestion(this.dropdown.selectedIndex);
            return;
        }

        // Mesaj gönder
        event.preventDefault();
        if (this.onSendMessage) {
            this.onSendMessage();
        }
    }

    /**
     * Escape tuşu - Dropdown'u kapat
     */
    _handleEscape(event) {
        if (this.dropdown.isOpen()) {
            event.preventDefault();
            this.dropdown.hide();
        }
    }

    /**
     * Yukarı ok - Önceki öneri
     */
    _handleArrowUp(event) {
        if (this.dropdown.isOpen()) {
            event.preventDefault();

            let newIndex = this.dropdown.selectedIndex - 1;
            if (newIndex < 0) {
                newIndex = this.dropdown.suggestions.length - 1;
            }

            this.dropdown.updateSelection(newIndex);
        }
    }

    /**
     * Aşağı ok - Sonraki öneri
     */
    _handleArrowDown(event) {
        if (this.dropdown.isOpen()) {
            event.preventDefault();

            let newIndex = this.dropdown.selectedIndex + 1;
            if (newIndex >= this.dropdown.suggestions.length) {
                newIndex = 0;
            }

            this.dropdown.updateSelection(newIndex);
        }
    }

    /**
     * Ctrl+Space - Önerileri manuel tetikle
     */
    _handleCtrlSpace(event) {
        event.preventDefault();

        if (this.onToggleSuggestions) {
            this.onToggleSuggestions();
        }
    }

    /**
     * Ctrl+Enter - Mesajı gönder
     */
    _handleCtrlEnter(event) {
        event.preventDefault();

        if (this.onSendMessage) {
            this.onSendMessage();
        }
    }

    /**
     * Yeni kısayol ekle
     */
    addShortcut(keyCombo, handler) {
        this.shortcuts[keyCombo] = handler;
    }

    /**
     * Kısayolu kaldır
     */
    removeShortcut(keyCombo) {
        delete this.shortcuts[keyCombo];
    }

    /**
     * Tüm kısayolları al
     */
    getShortcuts() {
        return Object.keys(this.shortcuts);
    }

    /**
     * Temizle
     */
    destroy() {
        this.input.removeEventListener('keydown', this._handleKeyDown);
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.KeyboardHandler = KeyboardHandler;
}
