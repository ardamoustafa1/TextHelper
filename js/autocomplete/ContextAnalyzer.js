/**
 * Context Analyzer - Bağlam Analizi Modülü
 * Sohbet bağlamını analiz ederek uygun önerileri belirler
 */

class ContextAnalyzer {
    constructor() {
        // Bağlam türleri
        this.contextTypes = {
            GREETING: 'greeting',
            FAREWELL: 'farewell',
            THANKS: 'thanks',
            APOLOGY: 'apology',
            QUESTION: 'question',
            ANSWER: 'answer',
            COMPLAINT: 'complaint',
            REQUEST: 'request',
            CONFIRMATION: 'confirmation',
            NEUTRAL: 'neutral'
        };

        // Anahtar kelime eşleştirmeleri
        this.keywords = {
            greeting: ['merhaba', 'selam', 'hoşgeldin', 'günaydın', 'iyi günler', 'iyi akşamlar', 'nasılsın', 'nasılsınız'],
            farewell: ['görüşürüz', 'hoşçakal', 'güle güle', 'iyi günler', 'görüşmek üzere', 'kendine iyi bak', 'elveda'],
            thanks: ['teşekkür', 'teşekkürler', 'sağol', 'sağ olun', 'minnettarım', 'çok sağol'],
            apology: ['özür', 'pardon', 'kusura bakma', 'affedersin', 'üzgünüm', 'maalesef'],
            question: ['nasıl', 'neden', 'ne zaman', 'nerede', 'kim', 'kaç', 'hangi', 'acaba', 'mı', 'mi', 'mu', 'mü', '?'],
            complaint: ['şikayet', 'sorun', 'problem', 'sıkıntı', 'hata', 'arıza', 'berbat', 'kötü', 'rezalet', 'kabul edilemez'],
            request: ['lütfen', 'ister misin', 'rica', 'yapabilir misin', 'yardım', 'destek', 'istiyorum', 'ihtiyacım var'],
            confirmation: ['tamam', 'oldu', 'anladım', 'evet', 'tabi', 'tabii', 'olur', 'kabul', 'onay', 'doğru']
        };

        // Duygu analizi kelimeleri
        this.sentimentWords = {
            positive: ['harika', 'mükemmel', 'süper', 'güzel', 'iyi', 'mutlu', 'memnun', 'teşekkür', 'başarılı', 'sevindim'],
            negative: ['kötü', 'berbat', 'rezalet', 'korkunç', 'üzgün', 'sinir', 'kızgın', 'hata', 'sorun', 'problem'],
            neutral: ['normal', 'fena değil', 'idare eder', 'eh işte', 'bir şey değil']
        };

        // Sohbet geçmişi
        this.conversationHistory = [];
        this.maxHistoryLength = 20;
    }

    /**
     * Metni analiz et ve bağlam türünü belirle
     * @param {string} text - Analiz edilecek metin
     * @returns {Object} - Analiz sonucu
     */
    analyze(text) {
        const normalizedText = text.toLowerCase().trim();

        const analysis = {
            text: text,
            type: this.contextTypes.NEUTRAL,
            sentiment: 'neutral',
            sentimentScore: 0,
            isQuestion: false,
            isCommand: false,
            keywords: [],
            suggestedResponses: []
        };

        // Bağlam türünü belirle
        analysis.type = this._detectContextType(normalizedText);

        // Duygu analizi
        const sentimentResult = this._analyzeSentiment(normalizedText);
        analysis.sentiment = sentimentResult.sentiment;
        analysis.sentimentScore = sentimentResult.score;

        // Soru mu kontrol et
        analysis.isQuestion = this._isQuestion(normalizedText);

        // Komut mu kontrol et
        analysis.isCommand = normalizedText.startsWith('/');

        // Anahtar kelimeleri bul
        analysis.keywords = this._extractKeywords(normalizedText);

        // Önerilen cevapları belirle
        analysis.suggestedResponses = this._getSuggestedResponses(analysis);

        // Geçmişe ekle
        this._addToHistory(analysis);

        return analysis;
    }

    /**
     * Bağlam türünü belirle
     */
    _detectContextType(text) {
        const scores = {};

        Object.entries(this.keywords).forEach(([type, words]) => {
            scores[type] = 0;
            words.forEach(word => {
                if (text.includes(word)) {
                    scores[type] += 1;
                }
            });
        });

        // En yüksek skoru bul
        let maxType = this.contextTypes.NEUTRAL;
        let maxScore = 0;

        Object.entries(scores).forEach(([type, score]) => {
            if (score > maxScore) {
                maxScore = score;
                maxType = type;
            }
        });

        return maxScore > 0 ? maxType : this.contextTypes.NEUTRAL;
    }

    /**
     * Duygu analizi yap
     */
    _analyzeSentiment(text) {
        let positiveCount = 0;
        let negativeCount = 0;

        this.sentimentWords.positive.forEach(word => {
            if (text.includes(word)) positiveCount++;
        });

        this.sentimentWords.negative.forEach(word => {
            if (text.includes(word)) negativeCount++;
        });

        const score = (positiveCount - negativeCount) / Math.max(positiveCount + negativeCount, 1);

        let sentiment = 'neutral';
        if (score > 0.2) sentiment = 'positive';
        else if (score < -0.2) sentiment = 'negative';

        return { sentiment, score };
    }

    /**
     * Metnin soru olup olmadığını kontrol et
     */
    _isQuestion(text) {
        const questionIndicators = ['?', ' mi ', ' mı ', ' mu ', ' mü ', 'nasıl', 'neden', 'ne zaman', 'nerede', 'kim', 'kaç', 'hangi'];
        return questionIndicators.some(indicator => text.includes(indicator));
    }

    /**
     * Anahtar kelimeleri çıkar
     */
    _extractKeywords(text) {
        const allKeywords = Object.values(this.keywords).flat();
        return allKeywords.filter(keyword => text.includes(keyword));
    }

    /**
     * Bağlama göre önerilen cevaplar
     */
    _getSuggestedResponses(analysis) {
        const responses = [];

        if (typeof CommonPhrases === 'undefined') return responses;

        switch (analysis.type) {
            case 'greeting':
                responses.push(...(CommonPhrases.greetings?.followUp || []));
                break;
            case 'farewell':
                responses.push(...(CommonPhrases.closings?.formal || []));
                break;
            case 'thanks':
                responses.push(...(CommonPhrases.thanks?.receiving || []));
                break;
            case 'apology':
                responses.push(...(CommonPhrases.apologies?.customerService || []));
                break;
            case 'question':
                responses.push(...(CommonPhrases.helpOffers || []));
                break;
            case 'complaint':
                responses.push(...(CommonPhrases.apologies?.customerService || []));
                break;
            case 'request':
                responses.push(...(CommonPhrases.confirmations || []));
                break;
            default:
                responses.push(...(CommonPhrases.helpOffers || []).slice(0, 3));
        }

        return responses.slice(0, 5);
    }

    /**
     * Geçmişe ekle
     */
    _addToHistory(analysis) {
        this.conversationHistory.push({
            ...analysis,
            timestamp: Date.now()
        });

        // Geçmiş limitini kontrol et
        if (this.conversationHistory.length > this.maxHistoryLength) {
            this.conversationHistory.shift();
        }
    }

    /**
     * Son bağlamı al
     */
    getLastContext() {
        return this.conversationHistory[this.conversationHistory.length - 1] || null;
    }

    /**
     * Sohbet akışını analiz et
     */
    analyzeConversationFlow() {
        if (this.conversationHistory.length < 2) return null;

        const recentHistory = this.conversationHistory.slice(-5);
        const types = recentHistory.map(h => h.type);

        // Akış kalıplarını tespit et
        const flow = {
            isEscalating: this._isEscalating(recentHistory),
            needsResolution: types.includes('complaint') && !types.includes('confirmation'),
            isEnding: types[types.length - 1] === 'farewell',
            dominantType: this._getDominantType(types),
            averageSentiment: this._getAverageSentiment(recentHistory)
        };

        return flow;
    }

    /**
     * Durumun kötüleşip kötüleşmediğini kontrol et
     */
    _isEscalating(history) {
        if (history.length < 3) return false;

        const sentiments = history.map(h => h.sentimentScore);
        let escalating = 0;

        for (let i = 1; i < sentiments.length; i++) {
            if (sentiments[i] < sentiments[i - 1]) escalating++;
        }

        return escalating >= Math.floor(sentiments.length / 2);
    }

    /**
     * Baskın bağlam türünü bul
     */
    _getDominantType(types) {
        const counts = {};
        types.forEach(type => {
            counts[type] = (counts[type] || 0) + 1;
        });

        return Object.entries(counts).reduce((a, b) => a[1] > b[1] ? a : b)[0];
    }

    /**
     * Ortalama duygu skorunu hesapla
     */
    _getAverageSentiment(history) {
        if (history.length === 0) return 0;
        const sum = history.reduce((acc, h) => acc + h.sentimentScore, 0);
        return sum / history.length;
    }

    /**
     * Geçmişi temizle
     */
    clearHistory() {
        this.conversationHistory = [];
    }

    /**
     * Bağlama göre öneri önceliklendirmesi
     */
    prioritizeSuggestions(suggestions, context) {
        if (!context) return suggestions;

        return suggestions.map(suggestion => {
            let priorityBoost = 0;
            const suggestionLower = suggestion.text?.toLowerCase() || suggestion.word?.toLowerCase() || '';

            // Bağlam türüne göre boost
            if (context.type === 'greeting' && this.keywords.greeting.some(k => suggestionLower.includes(k))) {
                priorityBoost += 2;
            }
            if (context.type === 'thanks' && (suggestionLower.includes('rica') || suggestionLower.includes('bir şey'))) {
                priorityBoost += 2;
            }
            if (context.type === 'complaint' && suggestionLower.includes('özür')) {
                priorityBoost += 3;
            }
            if (context.isQuestion && (suggestionLower.includes('evet') || suggestionLower.includes('hayır'))) {
                priorityBoost += 1;
            }

            return {
                ...suggestion,
                score: (suggestion.score || 1) + priorityBoost,
                contextBoosted: priorityBoost > 0
            };
        }).sort((a, b) => b.score - a.score);
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.ContextAnalyzer = ContextAnalyzer;
}
