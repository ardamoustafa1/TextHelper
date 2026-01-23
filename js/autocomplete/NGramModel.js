/**
 * N-Gram Model - Kelime/Cümle Tahmin Modeli
 * N-gram tabanlı dil modeli ile sonraki kelimeleri tahmin eder
 */

class NGramModel {
    constructor() {
        // N-gram veritabanları
        this.unigrams = new Map();      // Tek kelime frekansları
        this.bigrams = new Map();        // 2-gram (kelime çiftleri)
        this.trigrams = new Map();       // 3-gram (kelime üçlüleri)
        this.quadgrams = new Map();      // 4-gram

        // Konfigürasyon
        this.config = {
            smoothingFactor: 0.1,        // Laplace smoothing
            minFrequency: 1,             // Minimum frekans eşiği
            maxPredictions: 10,          // Maksimum tahmin sayısı
            weightUnigram: 0.1,
            weightBigram: 0.3,
            weightTrigram: 0.4,
            weightQuadgram: 0.2
        };

        // Başlangıç verilerini yükle
        this._initializeFromDictionary();
    }

    /**
     * Sözlükten başlangıç verilerini yükle
     */
    _initializeFromDictionary() {
        // TurkishDictionary yüklü mü kontrol et
        if (typeof TurkishDictionary === 'undefined') {
            console.warn('TurkishDictionary not loaded, NGramModel will start empty');
            return;
        }

        // Unigram'ları yükle
        TurkishDictionary.commonWords.forEach((word, index) => {
            // Frekansı sıraya göre hesapla (üsttekiler daha sık)
            const frequency = Math.max(100 - index, 1);
            this.unigrams.set(word.toLowerCase(), frequency);
        });

        // Bigram'ları yükle
        Object.entries(TurkishDictionary.bigrams).forEach(([word, followers]) => {
            const bigramMap = new Map();
            followers.forEach((follower, index) => {
                bigramMap.set(follower.toLowerCase(), Math.max(10 - index, 1));
            });
            this.bigrams.set(word.toLowerCase(), bigramMap);
        });

        // Trigram'ları yükle
        Object.entries(TurkishDictionary.trigrams).forEach(([phrase, followers]) => {
            const trigramMap = new Map();
            followers.forEach((follower, index) => {
                trigramMap.set(follower.toLowerCase(), Math.max(10 - index, 1));
            });
            this.trigrams.set(phrase.toLowerCase(), trigramMap);
        });

        console.log(`NGramModel initialized: ${this.unigrams.size} unigrams, ${this.bigrams.size} bigrams, ${this.trigrams.size} trigrams`);
    }

    /**
     * Metni öğren ve modeli güncelle
     * @param {string} text - Öğrenilecek metin
     */
    learn(text) {
        const tokens = this._tokenize(text);

        if (tokens.length === 0) return;

        // Unigram'ları güncelle
        tokens.forEach(token => {
            const current = this.unigrams.get(token) || 0;
            this.unigrams.set(token, current + 1);
        });

        // Bigram'ları güncelle
        for (let i = 0; i < tokens.length - 1; i++) {
            const key = tokens[i];
            const next = tokens[i + 1];

            if (!this.bigrams.has(key)) {
                this.bigrams.set(key, new Map());
            }

            const bigramMap = this.bigrams.get(key);
            const current = bigramMap.get(next) || 0;
            bigramMap.set(next, current + 1);
        }

        // Trigram'ları güncelle
        for (let i = 0; i < tokens.length - 2; i++) {
            const key = `${tokens[i]} ${tokens[i + 1]}`;
            const next = tokens[i + 2];

            if (!this.trigrams.has(key)) {
                this.trigrams.set(key, new Map());
            }

            const trigramMap = this.trigrams.get(key);
            const current = trigramMap.get(next) || 0;
            trigramMap.set(next, current + 1);
        }

        // Quadgram'ları güncelle
        for (let i = 0; i < tokens.length - 3; i++) {
            const key = `${tokens[i]} ${tokens[i + 1]} ${tokens[i + 2]}`;
            const next = tokens[i + 3];

            if (!this.quadgrams.has(key)) {
                this.quadgrams.set(key, new Map());
            }

            const quadgramMap = this.quadgrams.get(key);
            const current = quadgramMap.get(next) || 0;
            quadgramMap.set(next, current + 1);
        }
    }

    /**
     * Sonraki kelimeyi tahmin et
     * @param {string} context - Önceki kelimeler (bağlam)
     * @param {string} prefix - Yazılmaya başlanan kelime (opsiyonel)
     * @returns {Array} - Tahminler [{word, score, source}]
     */
    predict(context, prefix = '') {
        const tokens = this._tokenize(context);
        const predictions = new Map();

        // Quadgram tahminleri
        if (tokens.length >= 3) {
            const key = `${tokens[tokens.length - 3]} ${tokens[tokens.length - 2]} ${tokens[tokens.length - 1]}`;
            this._addPredictions(predictions, this.quadgrams.get(key), this.config.weightQuadgram, 'quadgram', prefix);
        }

        // Trigram tahminleri
        if (tokens.length >= 2) {
            const key = `${tokens[tokens.length - 2]} ${tokens[tokens.length - 1]}`;
            this._addPredictions(predictions, this.trigrams.get(key), this.config.weightTrigram, 'trigram', prefix);
        }

        // Bigram tahminleri
        if (tokens.length >= 1) {
            const key = tokens[tokens.length - 1];
            this._addPredictions(predictions, this.bigrams.get(key), this.config.weightBigram, 'bigram', prefix);
        }

        // Unigram tahminleri (prefix ile eşleşenler)
        if (prefix) {
            this._addUnigramPredictions(predictions, prefix, this.config.weightUnigram);
        }

        // Sonuçları sırala ve döndür
        return Array.from(predictions.entries())
            .map(([word, data]) => ({
                word,
                score: data.score,
                source: data.source
            }))
            .sort((a, b) => b.score - a.score)
            .slice(0, this.config.maxPredictions);
    }

    /**
     * Kelime tamamla (prefix ile başlayan kelimeler)
     * @param {string} prefix - Kelime başlangıcı
     * @returns {Array} - Tamamlama önerileri
     */
    completeWord(prefix) {
        if (!prefix || prefix.length < 1) return [];

        const normalizedPrefix = prefix.toLowerCase();
        const completions = [];

        this.unigrams.forEach((frequency, word) => {
            if (word.startsWith(normalizedPrefix) && word !== normalizedPrefix) {
                completions.push({
                    word,
                    score: frequency,
                    completion: word.slice(prefix.length),
                    source: 'dictionary'
                });
            }
        });

        // Frekansa göre sırala
        return completions
            .sort((a, b) => b.score - a.score)
            .slice(0, this.config.maxPredictions);
    }

    /**
     * Cümle tamamla (trigram tabanlı)
     * @param {string} context - Mevcut metin
     * @returns {Array} - Cümle tamamlama önerileri
     */
    completeSentence(context, maxWords = 5) {
        const tokens = this._tokenize(context);
        const completions = [];

        // Her olası devam için
        const nextPredictions = this.predict(context);

        nextPredictions.slice(0, 5).forEach(prediction => {
            let sentence = prediction.word;
            let currentContext = context + ' ' + prediction.word;
            let score = prediction.score;

            // Birkaç kelime daha tahmin et
            for (let i = 1; i < maxWords; i++) {
                const nextWord = this.predict(currentContext)[0];
                if (!nextWord || nextWord.word === '.' || nextWord.score < 0.1) break;

                sentence += ' ' + nextWord.word;
                currentContext += ' ' + nextWord.word;
                score += nextWord.score * Math.pow(0.7, i); // Sonraki kelimeler için azalan ağırlık
            }

            completions.push({
                text: sentence,
                score,
                source: 'ngram'
            });
        });

        return completions.sort((a, b) => b.score - a.score);
    }

    /**
     * N-gram haritasından tahminler ekle
     */
    _addPredictions(predictions, ngramMap, weight, source, prefix) {
        if (!ngramMap) return;

        const normalizedPrefix = prefix.toLowerCase();

        ngramMap.forEach((frequency, word) => {
            // Prefix filtresi
            if (prefix && !word.toLowerCase().startsWith(normalizedPrefix)) return;

            const existing = predictions.get(word);
            const score = frequency * weight;

            if (existing) {
                existing.score += score;
            } else {
                predictions.set(word, { score, source });
            }
        });
    }

    /**
     * Unigram tahminlerini ekle
     */
    _addUnigramPredictions(predictions, prefix, weight) {
        const normalizedPrefix = prefix.toLowerCase();

        this.unigrams.forEach((frequency, word) => {
            if (word.startsWith(normalizedPrefix) && word !== normalizedPrefix) {
                const existing = predictions.get(word);
                const score = frequency * weight;

                if (existing) {
                    existing.score += score;
                } else {
                    predictions.set(word, { score, source: 'unigram' });
                }
            }
        });
    }

    /**
     * Metni tokenize et
     */
    _tokenize(text) {
        if (!text) return [];

        return text
            .toLowerCase()
            .replace(/[^\wğüşıöçĞÜŞİÖÇ\s]/g, ' ')
            .split(/\s+/)
            .filter(token => token.length > 0);
    }

    /**
     * Modeli serialize et (localStorage için)
     */
    serialize() {
        return JSON.stringify({
            unigrams: Array.from(this.unigrams.entries()),
            bigrams: Array.from(this.bigrams.entries()).map(([k, v]) => [k, Array.from(v.entries())]),
            trigrams: Array.from(this.trigrams.entries()).map(([k, v]) => [k, Array.from(v.entries())]),
            quadgrams: Array.from(this.quadgrams.entries()).map(([k, v]) => [k, Array.from(v.entries())])
        });
    }

    /**
     * Modeli deserialize et
     */
    deserialize(data) {
        try {
            const parsed = JSON.parse(data);

            this.unigrams = new Map(parsed.unigrams);
            this.bigrams = new Map(parsed.bigrams.map(([k, v]) => [k, new Map(v)]));
            this.trigrams = new Map(parsed.trigrams.map(([k, v]) => [k, new Map(v)]));
            this.quadgrams = new Map(parsed.quadgrams.map(([k, v]) => [k, new Map(v)]));

            return true;
        } catch (e) {
            console.error('Failed to deserialize NGramModel:', e);
            return false;
        }
    }

    /**
     * Model istatistiklerini al
     */
    getStats() {
        return {
            unigrams: this.unigrams.size,
            bigrams: this.bigrams.size,
            trigrams: this.trigrams.size,
            quadgrams: this.quadgrams.size,
            totalEntries: this.unigrams.size + this.bigrams.size + this.trigrams.size + this.quadgrams.size
        };
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.NGramModel = NGramModel;
}
