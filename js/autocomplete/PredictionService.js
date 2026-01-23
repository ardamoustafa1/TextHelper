/**
 * Prediction Service - Tahmin Servisi
 * Tüm tahmin kaynaklarını birleştirip en iyi sonuçları döndürür
 */

class PredictionService {
    constructor() {
        // Alt modüller
        this.ngramModel = null;
        this.contextAnalyzer = null;
        this.templateManager = null;
        this.historyManager = null;
        this.spellChecker = null;

        // Konfigürasyon
        this.config = {
            maxSuggestions: 7,
            minWordLength: 1,  // Tek harf için de öneriler
            debounceMs: 30,
            weights: {
                template: 10,       // Şablon eşleşmeleri en yüksek
                history: 8,         // Geçmiş kullanımlar
                ngram: 6,           // N-gram tahminleri
                dictionary: 5,      // Sözlük eşleşmeleri (artırıldı)
                spellcheck: 9,      // Yazım düzeltmeleri (yüksek öncelik)
                context: 2          // Bağlam önerileri
            }
        };

        // Önbellek
        this.cache = new Map();
        this.cacheMaxSize = 100;
        this.cacheTimeout = 5000; // 5 saniye

        // Başlat
        this._initialize();
    }

    /**
     * Modülleri başlat
     */
    _initialize() {
        // NGramModel
        if (typeof NGramModel !== 'undefined') {
            this.ngramModel = new NGramModel();
        }

        // ContextAnalyzer
        if (typeof ContextAnalyzer !== 'undefined') {
            this.contextAnalyzer = new ContextAnalyzer();
        }

        // TemplateManager
        if (typeof TemplateManager !== 'undefined') {
            this.templateManager = new TemplateManager();
            this.templateManager.loadCustomTemplates();
        }

        // HistoryManager
        if (typeof HistoryManager !== 'undefined') {
            this.historyManager = new HistoryManager();
        }

        // SpellChecker
        if (typeof SpellChecker !== 'undefined') {
            this.spellChecker = new SpellChecker();
        }

        console.log('PredictionService initialized');
    }

    /**
     * Ana tahmin fonksiyonu
     * @param {string} input - Kullanıcı girdisi
     * @returns {Array} - Tahmin sonuçları
     */
    predict(input) {
        if (!input || input.trim().length === 0) {
            return this._getDefaultSuggestions();
        }

        // Önbellekte var mı?
        const cacheKey = input.toLowerCase();
        const cached = this._getFromCache(cacheKey);
        if (cached) return cached;

        const predictions = [];
        const lastWord = this._getLastWord(input);
        const context = input.slice(0, input.length - lastWord.length).trim();

        // Bağlam analizi (context-aware)
        let contextAnalysis = null;
        if (this.contextAnalyzer && context) {
            contextAnalysis = this.contextAnalyzer.analyze(context);
        }

        // 1. Komut/Şablon tahminleri (/ ile başlıyorsa)
        if (input.startsWith('/')) {
            const templateResults = this._getTemplatePredictions(input);
            predictions.push(...templateResults);
        } else {
            // 2. Geçmiş tabanlı tahminler
            const historyResults = this._getHistoryPredictions(lastWord, context);
            predictions.push(...historyResults);

            // 3. N-gram tahminleri
            const ngramResults = this._getNgramPredictions(context, lastWord);
            predictions.push(...ngramResults);

            // 4. Sözlük/kelime tamamlama (ÖNCE - en yüksek öncelik)
            const dictionaryResults = this._getDictionaryPredictions(lastWord);
            predictions.push(...dictionaryResults);

            // 5. N-gram kelime tamamlama (sözlük ile birlikte)
            if (lastWord.length >= 2) {
                const ngramCompletions = this.ngramModel?.completeWord(lastWord) || [];
                ngramCompletions.forEach(completion => {
                    // Sözlük sonuçlarında yoksa ekle
                    if (!dictionaryResults.find(r => r.text === completion.word)) {
                        predictions.push({
                            type: 'completion',
                            text: completion.word,
                            description: 'Kelime tamamla',
                            icon: 'fas fa-keyboard',
                            score: this.config.weights.dictionary * (completion.score / 100),
                            replaceWord: true
                        });
                    }
                });
            }

            // 6. Fuzzy matching tahminleri (sadece uzun prefixler için)
            if (lastWord.length > 3) {
                const fuzzyResults = this._getFuzzyPredictions(lastWord);
                predictions.push(...fuzzyResults);
            }

            // 7. Yazım düzeltme (SpellChecker ile - sadece uzun kelimeler için)
            if (lastWord.length > 3) {
                const spellCheckResults = this._getSpellCheckPredictions(lastWord);
                predictions.push(...spellCheckResults);
            }

            // 7. Eski yazım düzeltmeleri (fallback)
            const correctionResults = this._getCorrectionPredictions(lastWord);
            predictions.push(...correctionResults);
        }

        // Sonuçları birleştir ve sırala
        let merged = this._mergeAndRank(predictions);

        // Bağlama göre önceliklendir (context-aware)
        if (contextAnalysis) {
            merged = this.prioritizeByContext(merged, contextAnalysis);
        }

        // Önbelleğe kaydet
        this._addToCache(cacheKey, merged);

        return merged;
    }

    /**
     * Şablon tahminleri
     */
    _getTemplatePredictions(input) {
        if (!this.templateManager) return [];

        const results = this.templateManager.searchCommands(input);

        return results.map(template => ({
            type: 'template',
            text: template.text,
            trigger: template.trigger,
            description: template.description,
            category: template.category,
            icon: template.categoryIcon || 'fas fa-bolt',
            score: this.config.weights.template + (template.matchScore || 0),
            replaceAll: true
        }));
    }

    /**
     * Geçmiş tabanlı tahminler
     */
    _getHistoryPredictions(prefix, context) {
        if (!this.historyManager) return [];

        const results = this.historyManager.searchByPrefix(prefix);

        return results.map(item => ({
            type: 'history',
            text: item.text,
            description: 'Daha önce kullandınız',
            frequency: item.frequency,
            icon: 'fas fa-history',
            score: this.config.weights.history * (item.score / 10),
            replaceWord: item.type === 'word',
            replaceAll: item.type === 'phrase'
        }));
    }

    /**
     * N-gram tahminleri
     */
    _getNgramPredictions(context, prefix) {
        if (!this.ngramModel) return [];

        const results = [];

        // Sonraki kelime tahmini
        if (context) {
            const nextWords = this.ngramModel.predict(context, prefix);
            nextWords.forEach(prediction => {
                results.push({
                    type: 'prediction',
                    text: prediction.word,
                    description: 'Önerilen kelime',
                    source: prediction.source,
                    icon: 'fas fa-lightbulb',
                    score: this.config.weights.ngram * (prediction.score / 10),
                    replaceWord: true
                });
            });
        }

        // Kelime tamamlama
        if (prefix && prefix.length >= this.config.minWordLength) {
            const completions = this.ngramModel.completeWord(prefix);
            completions.forEach(completion => {
                results.push({
                    type: 'completion',
                    text: completion.word,
                    completion: completion.completion,
                    description: 'Kelime tamamla',
                    icon: 'fas fa-keyboard',
                    score: this.config.weights.dictionary * (completion.score / 10),
                    replaceWord: true
                });
            });
        }

        return results;
    }

    /**
     * Sözlük tahminleri
     */
    _getDictionaryPredictions(prefix) {
        if (!prefix || prefix.length < this.config.minWordLength) return [];
        if (typeof TurkishDictionary === 'undefined') return [];

        const normalizedPrefix = prefix.toLowerCase();
        const results = [];
        const maxResults = 10;

        // Common words'den ara (fuzzy matching ile)
        TurkishDictionary.commonWords.forEach((word, index) => {
            const wordLower = word.toLowerCase();
            
            // Tam eşleşme veya başlangıç eşleşmesi
            if (wordLower.startsWith(normalizedPrefix) && wordLower !== normalizedPrefix) {
                const priority = Math.max(0, 1 - index / TurkishDictionary.commonWords.length);
                results.push({
                    type: 'dictionary',
                    text: word,
                    description: 'Sözlük',
                    icon: 'fas fa-book',
                    score: this.config.weights.dictionary * priority,
                    replaceWord: true,
                    matchedPart: prefix
                });
            }
            // İçinde geçiyor mu? (sadece kısa prefixler için)
            else if (normalizedPrefix.length <= 3 && wordLower.includes(normalizedPrefix)) {
                results.push({
                    type: 'dictionary',
                    text: word,
                    description: 'Sözlük',
                    icon: 'fas fa-book',
                    score: this.config.weights.dictionary * 0.3 * (1 - index / TurkishDictionary.commonWords.length),
                    replaceWord: true,
                    matchedPart: prefix
                });
            }
        });

        // Skora göre sırala ve en iyilerini döndür
        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, maxResults);
    }
    
    /**
     * Fuzzy matching tahminleri
     */
    _getFuzzyPredictions(prefix) {
        if (!prefix || prefix.length < 1 || typeof TurkishDictionary === 'undefined') return [];
        
        const normalizedPrefix = prefix.toLowerCase();
        const results = [];
        const maxDistance = Math.min(2, Math.floor(prefix.length / 2));
        
        // Sadece kısa prefixler için fuzzy matching (performans için)
        if (prefix.length > 5) return [];
        
        TurkishDictionary.commonWords.forEach((word, index) => {
            const wordLower = word.toLowerCase();
            
            // Zaten tam eşleşme varsa atla
            if (wordLower.startsWith(normalizedPrefix)) return;
            
            // Fuzzy distance hesapla
            const distance = this._fuzzyDistance(normalizedPrefix, wordLower);
            
            if (distance <= maxDistance && distance > 0) {
                const similarity = 1 - (distance / Math.max(prefix.length, word.length));
                const priority = Math.max(0, 1 - index / TurkishDictionary.commonWords.length);
                
                results.push({
                    type: 'fuzzy',
                    text: word,
                    description: 'Benzer kelime',
                    icon: 'fas fa-search',
                    score: this.config.weights.dictionary * similarity * priority * 0.5,
                    replaceWord: true,
                    matchedPart: prefix,
                    distance: distance,
                    similarity: similarity
                });
            }
        });
        
        return results
            .sort((a, b) => b.score - a.score)
            .slice(0, 5);
    }
    
    /**
     * Basit fuzzy distance (Levenshtein benzeri ama daha hızlı)
     */
    _fuzzyDistance(str1, str2) {
        const len1 = str1.length;
        const len2 = str2.length;
        
        // Çok farklı uzunluklar
        if (Math.abs(len1 - len2) > 3) return 999;
        
        // Kısa stringler için basit karşılaştırma
        if (len1 <= 2 || len2 <= 2) {
            let matches = 0;
            for (let i = 0; i < Math.min(len1, len2); i++) {
                if (str1[i] === str2[i]) matches++;
            }
            return Math.max(len1, len2) - matches;
        }
        
        // Ortak karakter sayısına göre
        const common = this._countCommonChars(str1, str2);
        const maxLen = Math.max(len1, len2);
        const distance = maxLen - common;
        
        return distance;
    }
    
    /**
     * Ortak karakter sayısını hesapla
     */
    _countCommonChars(str1, str2) {
        const chars1 = {};
        const chars2 = {};
        
        for (const char of str1) {
            chars1[char] = (chars1[char] || 0) + 1;
        }
        
        for (const char of str2) {
            chars2[char] = (chars2[char] || 0) + 1;
        }
        
        let common = 0;
        for (const char in chars1) {
            if (chars2[char]) {
                common += Math.min(chars1[char], chars2[char]);
            }
        }
        
        return common;
    }

    /**
     * SpellChecker ile yazım düzeltme tahminleri
     */
    _getSpellCheckPredictions(word) {
        if (!word || !this.spellChecker || word.length < this.config.minWordLength) return [];

        const suggestions = this.spellChecker.check(word);
        
        return suggestions.map(suggestion => ({
            type: 'spellcheck',
            text: suggestion.word,
            originalWord: word,
            description: `Yazım düzeltmesi (${Math.round(suggestion.confidence * 100)}% güven)`,
            icon: 'fas fa-spell-check',
            score: this.config.weights.spellcheck * (1 - suggestion.distance / 5) * suggestion.confidence,
            replaceWord: true,
            isCorrection: true,
            distance: suggestion.distance,
            confidence: suggestion.confidence
        }));
    }

    /**
     * Yazım düzeltme tahminleri (eski sistem - fallback)
     */
    _getCorrectionPredictions(word) {
        if (!word || typeof TurkishDictionary === 'undefined') return [];

        const normalizedWord = word.toLowerCase();
        const correction = TurkishDictionary.corrections[normalizedWord];

        if (correction) {
            return [{
                type: 'correction',
                text: correction,
                originalWord: word,
                description: `"${word}" → "${correction}"`,
                icon: 'fas fa-spell-check',
                score: this.config.weights.dictionary + 5,
                replaceWord: true,
                isCorrection: true
            }];
        }

        // Kısaltma kontrolü
        const abbreviation = TurkishDictionary.abbreviations[normalizedWord];
        if (abbreviation) {
            return [{
                type: 'abbreviation',
                text: abbreviation,
                trigger: word,
                description: `Kısaltma: ${word}`,
                icon: 'fas fa-compress-arrows-alt',
                score: this.config.weights.template,
                replaceAll: true
            }];
        }

        return [];
    }

    /**
     * Varsayılan öneriler (boş input için)
     */
    _getDefaultSuggestions() {
        const suggestions = [];

        // Sık kullanılan ifadeler
        if (this.historyManager) {
            const frequent = this.historyManager.getFrequentPhrases(3);
            frequent.forEach(item => {
                suggestions.push({
                    type: 'frequent',
                    text: item.text,
                    description: 'Sık kullanılan',
                    icon: 'fas fa-star',
                    score: 5,
                    replaceAll: true
                });
            });
        }

        // Karşılama şablonları
        if (this.templateManager) {
            const greetings = this.templateManager.getByCategory('general').slice(0, 2);
            greetings.forEach(template => {
                suggestions.push({
                    type: 'template',
                    text: template.text,
                    trigger: template.trigger,
                    description: template.description,
                    icon: template.categoryIcon || 'fas fa-bolt',
                    score: 3,
                    replaceAll: true
                });
            });
        }

        return suggestions.slice(0, this.config.maxSuggestions);
    }

    /**
     * Sonuçları birleştir ve sırala
     */
    _mergeAndRank(predictions) {
        // Duplikatları kaldır
        const seen = new Set();
        const unique = predictions.filter(p => {
            const key = p.text.toLowerCase();
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        });

        // Skora göre sırala
        unique.sort((a, b) => b.score - a.score);

        // Maksimum sayıda döndür
        return unique.slice(0, this.config.maxSuggestions);
    }

    /**
     * Son kelimeyi al
     */
    _getLastWord(input) {
        const words = input.split(/\s+/);
        return words[words.length - 1] || '';
    }

    /**
     * Önbellekten al
     */
    _getFromCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        // Zaman aşımı kontrolü
        if (Date.now() - cached.timestamp > this.cacheTimeout) {
            this.cache.delete(key);
            return null;
        }

        return cached.data;
    }

    /**
     * Önbelleğe ekle
     */
    _addToCache(key, data) {
        // Boyut kontrolü
        if (this.cache.size >= this.cacheMaxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    /**
     * Mesaj gönderildiğinde öğren
     */
    learnFromMessage(message) {
        if (this.ngramModel) {
            this.ngramModel.learn(message);
        }

        if (this.historyManager) {
            this.historyManager.addMessage(message);
        }

        // Önbelleği temizle
        this.cache.clear();
    }

    /**
     * Bağlam analizi yap
     */
    analyzeContext(text) {
        if (this.contextAnalyzer) {
            return this.contextAnalyzer.analyze(text);
        }
        return null;
    }

    /**
     * Bağlama göre önerileri önceliklendİr
     */
    prioritizeByContext(predictions, contextAnalysis) {
        if (!this.contextAnalyzer || !contextAnalysis) return predictions;

        return this.contextAnalyzer.prioritizeSuggestions(predictions, contextAnalysis);
    }

    /**
     * Cümle tamamlama
     */
    completeSentence(context) {
        if (!this.ngramModel) return [];

        return this.ngramModel.completeSentence(context);
    }

    /**
     * Şablon değişkenlerini doldur
     */
    fillTemplateVariables(text, variables) {
        if (!this.templateManager) return text;

        return this.templateManager.fillVariables(text, variables);
    }

    /**
     * İstatistikler
     */
    getStats() {
        return {
            ngram: this.ngramModel?.getStats() || null,
            templates: this.templateManager?.getStats() || null,
            history: this.historyManager?.getStats() || null,
            cacheSize: this.cache.size
        };
    }

    /**
     * Önbelleği temizle
     */
    clearCache() {
        this.cache.clear();
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.PredictionService = PredictionService;
}
