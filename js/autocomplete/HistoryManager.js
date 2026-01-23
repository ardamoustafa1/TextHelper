/**
 * History Manager - Geçmiş Yöneticisi
 * Kullanıcının sık kullandığı ifadeleri öğrenir ve saklar
 */

class HistoryManager {
    constructor() {
        // Konfigürasyon
        this.config = {
            maxHistoryItems: 500,
            maxFrequentItems: 50,
            storageKey: 'texthelper_history',
            frequencyStorageKey: 'texthelper_frequency',
            sessionStorageKey: 'texthelper_session'
        };

        // Geçmiş veri yapıları
        this.history = [];           // Tüm geçmiş mesajlar
        this.frequencyMap = new Map(); // Kelime/ifade frekansları
        this.sessionHistory = [];    // Oturum geçmişi

        // Başlangıçta yükle
        this._loadFromStorage();
    }

    /**
     * Storage'dan verileri yükle
     */
    _loadFromStorage() {
        try {
            // Geçmiş mesajları yükle
            const historyData = localStorage.getItem(this.config.storageKey);
            if (historyData) {
                this.history = JSON.parse(historyData);
            }

            // Frekans haritasını yükle
            const frequencyData = localStorage.getItem(this.config.frequencyStorageKey);
            if (frequencyData) {
                const parsed = JSON.parse(frequencyData);
                this.frequencyMap = new Map(parsed);
            }

            console.log(`HistoryManager loaded: ${this.history.length} items, ${this.frequencyMap.size} frequency entries`);
        } catch (e) {
            console.error('Failed to load history from storage:', e);
        }
    }

    /**
     * Storage'a kaydet
     */
    _saveToStorage() {
        try {
            // Geçmişi kaydet
            localStorage.setItem(this.config.storageKey, JSON.stringify(this.history));

            // Frekans haritasını kaydet
            localStorage.setItem(this.config.frequencyStorageKey,
                JSON.stringify(Array.from(this.frequencyMap.entries()))
            );
        } catch (e) {
            console.error('Failed to save history to storage:', e);
        }
    }

    /**
     * Yeni mesaj ekle
     * @param {string} message - Mesaj metni
     * @param {Object} metadata - Ek bilgiler (opsiyonel)
     */
    addMessage(message, metadata = {}) {
        if (!message || message.trim().length === 0) return;

        const trimmedMessage = message.trim();

        // Geçmişe ekle
        const historyItem = {
            id: Date.now().toString(36) + Math.random().toString(36).substr(2),
            text: trimmedMessage,
            timestamp: Date.now(),
            ...metadata
        };

        this.history.push(historyItem);
        this.sessionHistory.push(historyItem);

        // Limiti kontrol et
        if (this.history.length > this.config.maxHistoryItems) {
            this.history = this.history.slice(-this.config.maxHistoryItems);
        }

        // Frekansları güncelle
        this._updateFrequencies(trimmedMessage);

        // Kaydet
        this._saveToStorage();
    }

    /**
     * Kelime ve ifade frekanslarını güncelle
     */
    _updateFrequencies(text) {
        // Tam metni ekle
        this._incrementFrequency(text, 'phrase');

        // Kelimeleri ekle
        const words = this._tokenize(text);
        words.forEach(word => {
            if (word.length >= 2) {
                this._incrementFrequency(word, 'word');
            }
        });

        // N-gramları ekle
        for (let i = 0; i < words.length - 1; i++) {
            const bigram = `${words[i]} ${words[i + 1]}`;
            this._incrementFrequency(bigram, 'bigram');
        }

        for (let i = 0; i < words.length - 2; i++) {
            const trigram = `${words[i]} ${words[i + 1]} ${words[i + 2]}`;
            this._incrementFrequency(trigram, 'trigram');
        }
    }

    /**
     * Frekansı artır
     */
    _incrementFrequency(text, type) {
        const key = text.toLowerCase();
        const existing = this.frequencyMap.get(key) || { count: 0, type, lastUsed: 0 };

        this.frequencyMap.set(key, {
            text,
            type,
            count: existing.count + 1,
            lastUsed: Date.now()
        });

        // Limit kontrolü
        if (this.frequencyMap.size > this.config.maxFrequentItems * 10) {
            this._pruneFrequencyMap();
        }
    }

    /**
     * Frekans haritasını temizle (az kullanılanları sil)
     */
    _pruneFrequencyMap() {
        const entries = Array.from(this.frequencyMap.entries())
            .sort((a, b) => {
                // Önce frekansa, sonra son kullanıma göre sırala
                const scoreA = a[1].count + (a[1].lastUsed / Date.now());
                const scoreB = b[1].count + (b[1].lastUsed / Date.now());
                return scoreB - scoreA;
            })
            .slice(0, this.config.maxFrequentItems * 5);

        this.frequencyMap = new Map(entries);
    }

    /**
     * Prefix ile eşleşen geçmiş öğeleri ara
     * @param {string} prefix - Arama metni
     * @returns {Array} - Eşleşen öğeler
     */
    searchByPrefix(prefix) {
        if (!prefix || prefix.length < 1) return [];

        const normalizedPrefix = prefix.toLowerCase();
        const results = [];

        // Frekans haritasında ara
        this.frequencyMap.forEach((data, key) => {
            if (key.startsWith(normalizedPrefix) || data.text.toLowerCase().startsWith(normalizedPrefix)) {
                results.push({
                    text: data.text,
                    type: data.type,
                    frequency: data.count,
                    lastUsed: data.lastUsed,
                    score: this._calculateScore(data, normalizedPrefix)
                });
            }
        });

        // Skora göre sırala
        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, 10);
    }

    /**
     * Sık kullanılan ifadeleri al
     * @param {number} limit - Maksimum sayı
     * @returns {Array} - Sık kullanılan ifadeler
     */
    getFrequentPhrases(limit = 10) {
        const phrases = [];

        this.frequencyMap.forEach((data, key) => {
            if (data.type === 'phrase' || data.type === 'trigram') {
                phrases.push({
                    text: data.text,
                    frequency: data.count,
                    lastUsed: data.lastUsed,
                    score: data.count * (1 + Math.log10(Date.now() - data.lastUsed + 1))
                });
            }
        });

        return phrases
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
    }

    /**
     * Sık kullanılan kelimeleri al
     * @param {number} limit - Maksimum sayı
     * @returns {Array} - Sık kullanılan kelimeler
     */
    getFrequentWords(limit = 20) {
        const words = [];

        this.frequencyMap.forEach((data, key) => {
            if (data.type === 'word') {
                words.push({
                    text: data.text,
                    frequency: data.count,
                    score: data.count
                });
            }
        });

        return words
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
    }

    /**
     * Öğrenme skoru hesapla
     */
    _calculateScore(data, prefix) {
        let score = data.count;

        // Tam eşleşme bonusu
        if (data.text.toLowerCase() === prefix) {
            score *= 2;
        }

        // Başlangıç eşleşmesi bonusu
        if (data.text.toLowerCase().startsWith(prefix)) {
            score *= 1.5;
        }

        // Güncellik bonusu (son 1 saat içinde kullanıldıysa)
        const hourAgo = Date.now() - 3600000;
        if (data.lastUsed > hourAgo) {
            score *= 1.3;
        }

        // Uzunluk cezası (çok uzun ifadeler için)
        if (data.text.length > 100) {
            score *= 0.7;
        }

        return score;
    }

    /**
     * Son mesajları al
     * @param {number} limit - Maksimum sayı
     * @returns {Array} - Son mesajlar
     */
    getRecentMessages(limit = 10) {
        return this.history.slice(-limit).reverse();
    }

    /**
     * Oturum geçmişini al
     */
    getSessionHistory() {
        return [...this.sessionHistory].reverse();
    }

    /**
     * Bağlama göre öneriler
     * @param {Object} context - Bağlam analizi sonucu
     * @returns {Array} - Bağlama uygun geçmiş önerileri
     */
    suggestByContext(context) {
        if (!context) return [];

        const suggestions = [];

        this.frequencyMap.forEach((data, key) => {
            let relevance = 0;
            const textLower = data.text.toLowerCase();

            // Anahtar kelime eşleşmesi
            context.keywords?.forEach(keyword => {
                if (textLower.includes(keyword.toLowerCase())) {
                    relevance += 2;
                }
            });

            // Bağlam türü eşleşmesi
            if (context.type === 'greeting' &&
                (textLower.includes('merhaba') || textLower.includes('selam'))) {
                relevance += 3;
            }
            if (context.type === 'thanks' && textLower.includes('teşekkür')) {
                relevance += 3;
            }

            if (relevance > 0) {
                suggestions.push({
                    ...data,
                    relevance,
                    score: data.count * relevance
                });
            }
        });

        return suggestions
            .sort((a, b) => b.score - a.score)
            .slice(0, 5);
    }

    /**
     * Metni tokenize et
     */
    _tokenize(text) {
        return text
            .toLowerCase()
            .replace(/[^\wğüşıöçĞÜŞİÖÇ\s]/g, ' ')
            .split(/\s+/)
            .filter(token => token.length > 0);
    }

    /**
     * Geçmişi temizle
     */
    clearHistory() {
        this.history = [];
        this.sessionHistory = [];
        this._saveToStorage();
    }

    /**
     * Frekans haritasını temizle
     */
    clearFrequencies() {
        this.frequencyMap.clear();
        this._saveToStorage();
    }

    /**
     * Tüm verileri temizle
     */
    clearAll() {
        this.history = [];
        this.sessionHistory = [];
        this.frequencyMap.clear();
        localStorage.removeItem(this.config.storageKey);
        localStorage.removeItem(this.config.frequencyStorageKey);
    }

    /**
     * İstatistikler
     */
    getStats() {
        const wordCount = Array.from(this.frequencyMap.values())
            .filter(d => d.type === 'word').length;
        const phraseCount = Array.from(this.frequencyMap.values())
            .filter(d => d.type === 'phrase').length;

        return {
            totalMessages: this.history.length,
            sessionMessages: this.sessionHistory.length,
            uniqueWords: wordCount,
            uniquePhrases: phraseCount,
            totalFrequencyEntries: this.frequencyMap.size
        };
    }

    /**
     * Verileri dışa aktar
     */
    exportData() {
        return {
            history: this.history,
            frequencies: Array.from(this.frequencyMap.entries()),
            exportDate: new Date().toISOString()
        };
    }

    /**
     * Verileri içe aktar
     */
    importData(data) {
        try {
            if (data.history) {
                this.history = [...this.history, ...data.history];
                if (this.history.length > this.config.maxHistoryItems) {
                    this.history = this.history.slice(-this.config.maxHistoryItems);
                }
            }

            if (data.frequencies) {
                data.frequencies.forEach(([key, value]) => {
                    const existing = this.frequencyMap.get(key);
                    if (existing) {
                        existing.count += value.count;
                        existing.lastUsed = Math.max(existing.lastUsed, value.lastUsed);
                    } else {
                        this.frequencyMap.set(key, value);
                    }
                });
            }

            this._saveToStorage();
            return true;
        } catch (e) {
            console.error('Failed to import data:', e);
            return false;
        }
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.HistoryManager = HistoryManager;
}
