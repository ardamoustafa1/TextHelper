/**
 * Suggestion Dropdown - Öneri Açılır Listesi
 * WhatsApp/VS Code tarzı öneri dropdown UI'ı
 */

class SuggestionDropdown {
    constructor(dropdownElement, listElement) {
        this.dropdown = dropdownElement;
        this.list = listElement;

        // State
        this.suggestions = [];
        this.selectedIndex = -1;
        this.isVisible = false;

        // Callbacks
        this.onItemClick = null;
        this.onItemHover = null;

        // Animasyon süresi
        this.animationDuration = 200;

        // Event listener'ları bağla
        this._bindEvents();
    }

    /**
     * Event listener'ları bağla
     */
    _bindEvents() {
        // Liste öğelerine click
        this.list.addEventListener('click', (e) => {
            const item = e.target.closest('.suggestion-item');
            if (item) {
                const index = parseInt(item.dataset.index, 10);
                this._handleItemClick(index);
            }
        });

        // Hover efekti
        this.list.addEventListener('mouseover', (e) => {
            const item = e.target.closest('.suggestion-item');
            if (item) {
                const index = parseInt(item.dataset.index, 10);
                this._handleItemHover(index);
            }
        });
    }

    /**
     * Önerileri göster
     * @param {Array} suggestions - Öneri listesi
     * @param {number} selectedIndex - Seçili öğe indexi
     */
    show(suggestions, selectedIndex = 0) {
        if (!suggestions || suggestions.length === 0) {
            this.hide();
            return;
        }

        this.suggestions = suggestions;
        this.selectedIndex = selectedIndex;

        // Liste HTML'ini oluştur
        this._renderList();

        // Dropdown'u göster
        this.dropdown.classList.add('visible');
        this.isVisible = true;

        // Seçili öğeyi görünür yap
        this._scrollToSelected();
    }

    /**
     * Dropdown'u gizle
     */
    hide() {
        this.dropdown.classList.remove('visible');
        this.isVisible = false;
        this.suggestions = [];
        this.selectedIndex = -1;
    }

    /**
     * Seçili öğeyi güncelle
     * @param {number} index - Yeni seçili index
     */
    updateSelection(index) {
        if (index < 0 || index >= this.suggestions.length) return;

        // Önceki seçimi kaldır
        const previousSelected = this.list.querySelector('.suggestion-item.active');
        if (previousSelected) {
            previousSelected.classList.remove('active');
        }

        // Yeni seçimi ekle
        this.selectedIndex = index;
        const newSelected = this.list.querySelector(`[data-index="${index}"]`);
        if (newSelected) {
            newSelected.classList.add('active');
        }

        // Görünür yap
        this._scrollToSelected();
    }

    /**
     * Listeyi render et
     */
    _renderList() {
        this.list.innerHTML = '';

        this.suggestions.forEach((suggestion, index) => {
            const item = this._createSuggestionItem(suggestion, index);
            this.list.appendChild(item);
        });
    }

    /**
     * Öneri öğesi oluştur
     */
    _createSuggestionItem(suggestion, index) {
        const item = document.createElement('li');
        item.className = `suggestion-item ${index === this.selectedIndex ? 'active' : ''}`;
        item.dataset.index = index;

        // İkon tipi belirle
        const iconClass = this._getIconClass(suggestion.type);
        const iconType = this._getIconType(suggestion.type);

        // Eşleşen metni vurgula
        const displayText = this._highlightMatch(suggestion.text, suggestion.matchedPart);

        item.innerHTML = `
            <div class="suggestion-icon ${iconType}">
                <i class="${suggestion.icon || iconClass}"></i>
            </div>
            <div class="suggestion-content">
                <span class="suggestion-text">${displayText}</span>
                ${suggestion.description ? `<span class="suggestion-meta">${suggestion.description}</span>` : ''}
            </div>
            ${suggestion.trigger ? `<span class="suggestion-shortcut">${suggestion.trigger}</span>` : ''}
            ${index === 0 ? '<span class="suggestion-shortcut">Tab</span>' : ''}
        `;

        return item;
    }

    /**
     * İkon sınıfını belirle
     */
    _getIconClass(type) {
        const iconMap = {
            'template': 'fas fa-bolt',
            'history': 'fas fa-history',
            'prediction': 'fas fa-lightbulb',
            'completion': 'fas fa-keyboard',
            'dictionary': 'fas fa-book',
            'correction': 'fas fa-spell-check',
            'abbreviation': 'fas fa-compress-arrows-alt',
            'frequent': 'fas fa-star',
            'phrase': 'fas fa-quote-right',
            'word': 'fas fa-font'
        };

        return iconMap[type] || 'fas fa-comment';
    }

    /**
     * İkon tipini belirle (renk için)
     */
    _getIconType(type) {
        const typeMap = {
            'template': 'template',
            'history': 'history',
            'prediction': 'phrase',
            'completion': 'word',
            'dictionary': 'word',
            'correction': 'word',
            'abbreviation': 'template',
            'frequent': 'history',
            'phrase': 'phrase',
            'word': 'word'
        };

        return typeMap[type] || 'word';
    }

    /**
     * Eşleşen kısmı vurgula
     */
    _highlightMatch(text, matchedPart) {
        if (!matchedPart) return this._escapeHtml(text);

        const escapedText = this._escapeHtml(text);
        const escapedMatch = this._escapeHtml(matchedPart);

        const regex = new RegExp(`(${this._escapeRegex(escapedMatch)})`, 'gi');
        return escapedText.replace(regex, '<span class="match">$1</span>');
    }

    /**
     * HTML karakterlerini escape et
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Regex özel karakterlerini escape et
     */
    _escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Seçili öğeye scroll
     */
    _scrollToSelected() {
        const selected = this.list.querySelector('.suggestion-item.active');
        if (selected) {
            selected.scrollIntoView({
                block: 'nearest',
                behavior: 'smooth'
            });
        }
    }

    /**
     * Öğe tıklama olayı
     */
    _handleItemClick(index) {
        if (this.onItemClick) {
            this.onItemClick(index, this.suggestions[index]);
        }
    }

    /**
     * Öğe hover olayı
     */
    _handleItemHover(index) {
        this.updateSelection(index);

        if (this.onItemHover) {
            this.onItemHover(index, this.suggestions[index]);
        }
    }

    /**
     * Dropdown pozisyonunu güncelle
     * @param {DOMRect} inputRect - Input elementinin pozisyonu
     */
    updatePosition(inputRect) {
        if (!inputRect) return;

        const viewportHeight = window.innerHeight;
        const dropdownHeight = this.dropdown.offsetHeight;

        // Yukarı mı aşağı mı açılacak?
        const spaceBelow = viewportHeight - inputRect.bottom;
        const spaceAbove = inputRect.top;

        if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
            // Yukarı aç
            this.dropdown.style.bottom = 'calc(100% + 8px)';
            this.dropdown.style.top = 'auto';
        } else {
            // Aşağı aç (varsayılan)
            this.dropdown.style.top = 'calc(100% + 8px)';
            this.dropdown.style.bottom = 'auto';
        }
    }

    /**
     * Görünürlük durumu
     */
    isOpen() {
        return this.isVisible;
    }

    /**
     * Seçili öneriyi al
     */
    getSelectedSuggestion() {
        if (this.selectedIndex >= 0 && this.selectedIndex < this.suggestions.length) {
            return this.suggestions[this.selectedIndex];
        }
        return null;
    }

    /**
     * Temizle
     */
    clear() {
        this.hide();
        this.list.innerHTML = '';
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.SuggestionDropdown = SuggestionDropdown;
}
