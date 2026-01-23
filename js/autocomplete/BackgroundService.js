/**
 * Background Service - Arka Plan Servisi
 * Tüm tahmin işlemlerini arka planda yönetir ve optimize eder
 */

class BackgroundService {
    constructor() {
        // Worker benzeri yapı (Web Worker kullanmadan)
        this.isRunning = false;
        this.queue = [];
        this.processing = false;
        
        // Servis modülleri
        this.predictionService = null;
        this.spellChecker = null;
        this.historyManager = null;
        
        // Konfigürasyon
        this.config = {
            batchSize: 10,              // Toplu işlem boyutu
            maxQueueSize: 100,          // Maksimum kuyruk boyutu
            processInterval: 50,        // İşlem aralığı (ms)
            cacheTimeout: 300000,       // Önbellek zaman aşımı (5 dk)
            enablePrefetch: true,       // Önceden yükleme aktif mi?
            prefetchThreshold: 3        // Önceden yükleme eşiği (karakter)
        };
        
        // Önbellek
        this.prefetchCache = new Map();
        this.resultCache = new Map();
        
        // İstatistikler
        this.stats = {
            totalRequests: 0,
            cacheHits: 0,
            cacheMisses: 0,
            averageResponseTime: 0,
            queueOverflows: 0
        };
        
        // Başlat
        this._initialize();
    }
    
    /**
     * Servisi başlat
     */
    _initialize() {
        // Modülleri başlat
        if (typeof PredictionService !== 'undefined') {
            this.predictionService = new PredictionService();
        }
        
        if (typeof SpellChecker !== 'undefined') {
            this.spellChecker = new SpellChecker();
        }
        
        if (typeof HistoryManager !== 'undefined') {
            this.historyManager = new HistoryManager();
        }
        
        // Arka plan işlemlerini başlat
        this.start();
        
        console.log('BackgroundService initialized');
    }
    
    /**
     * Servisi başlat
     */
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this._processQueue();
        
        // Önceden yükleme aktifse başlat
        if (this.config.enablePrefetch) {
            this._startPrefetch();
        }
    }
    
    /**
     * Servisi durdur
     */
    stop() {
        this.isRunning = false;
        this.queue = [];
        this.processing = false;
    }
    
    /**
     * Tahmin isteği ekle
     * @param {string} input - Kullanıcı girdisi
     * @param {Function} callback - Sonuç callback'i
     * @returns {Promise} - Promise döndürür
     */
    async predict(input, callback = null) {
        this.stats.totalRequests++;
        
        // Önbellekte var mı?
        const cacheKey = input.toLowerCase().trim();
        const cached = this._getFromCache(cacheKey);
        if (cached) {
            this.stats.cacheHits++;
            if (callback) callback(cached);
            return Promise.resolve(cached);
        }
        
        this.stats.cacheMisses++;
        
        // Kuyruğa ekle
        return new Promise((resolve) => {
            const request = {
                id: Date.now() + Math.random(),
                input: input,
                timestamp: Date.now(),
                callback: callback || resolve,
                resolve: resolve
            };
            
            // Kuyruk doluluğu kontrolü
            if (this.queue.length >= this.config.maxQueueSize) {
                this.stats.queueOverflows++;
                // En eski isteği kaldır
                this.queue.shift();
            }
            
            this.queue.push(request);
        });
    }
    
    /**
     * Kuyruğu işle
     */
    async _processQueue() {
        if (!this.isRunning) return;
        
        if (this.queue.length > 0 && !this.processing) {
            this.processing = true;
            
            // Toplu işlem
            const batch = this.queue.splice(0, this.config.batchSize);
            const startTime = Date.now();
            
            // Paralel işle
            const promises = batch.map(request => this._processRequest(request));
            await Promise.all(promises);
            
            // İstatistik güncelle
            const responseTime = Date.now() - startTime;
            this._updateAverageResponseTime(responseTime);
        }
        
        this.processing = false;
        
        // Tekrar kontrol et
        setTimeout(() => this._processQueue(), this.config.processInterval);
    }
    
    /**
     * Tek bir isteği işle
     */
    async _processRequest(request) {
        try {
            const startTime = Date.now();
            
            // Tahmin yap
            let results = [];
            
            if (this.predictionService) {
                results = this.predictionService.predict(request.input);
            }
            
            // Sonuçları önbelleğe kaydet
            const cacheKey = request.input.toLowerCase().trim();
            this._addToCache(cacheKey, results);
            
            // Callback çağır
            if (request.callback) {
                request.callback(results);
            }
            
            if (request.resolve) {
                request.resolve(results);
            }
            
            // İstatistik
            const responseTime = Date.now() - startTime;
            this._updateAverageResponseTime(responseTime);
            
        } catch (error) {
            console.error('BackgroundService: Request processing error:', error);
            
            // Hata durumunda boş sonuç döndür
            if (request.callback) {
                request.callback([]);
            }
            if (request.resolve) {
                request.resolve([]);
            }
        }
    }
    
    /**
     * Önceden yükleme başlat
     */
    _startPrefetch() {
        // Kullanıcı yazarken olası sonraki karakterleri tahmin et
        // Bu özellik daha sonra geliştirilebilir
    }
    
    /**
     * Önceden yükleme için tahmin yap
     */
    async prefetch(prefix) {
        if (!this.config.enablePrefetch || prefix.length < this.config.prefetchThreshold) {
            return;
        }
        
        // Önbellekte var mı?
        if (this.prefetchCache.has(prefix)) {
            return;
        }
        
        // Olası sonraki karakterleri tahmin et
        const commonNextChars = ['a', 'e', 'i', 'ı', 'o', 'ö', 'u', 'ü', 'r', 'l', 'n', 'm'];
        
        for (const char of commonNextChars) {
            const nextInput = prefix + char;
            
            // Zaten işlenmiş mi?
            if (this.resultCache.has(nextInput)) {
                continue;
            }
            
            // Arka planda tahmin yap (callback olmadan)
            this.predict(nextInput).then(results => {
                this.prefetchCache.set(nextInput, results);
            }).catch(() => {
                // Hata durumunda sessizce devam et
            });
        }
    }
    
    /**
     * Önbellekten al
     */
    _getFromCache(key) {
        const cached = this.resultCache.get(key);
        if (!cached) return null;
        
        // Zaman aşımı kontrolü
        if (Date.now() - cached.timestamp > this.config.cacheTimeout) {
            this.resultCache.delete(key);
            return null;
        }
        
        return cached.data;
    }
    
    /**
     * Önbelleğe ekle
     */
    _addToCache(key, data) {
        // Boyut kontrolü
        if (this.resultCache.size >= 500) {
            // En eski kaydı sil
            const firstKey = this.resultCache.keys().next().value;
            this.resultCache.delete(firstKey);
        }
        
        this.resultCache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    /**
     * Ortalama yanıt süresini güncelle
     */
    _updateAverageResponseTime(newTime) {
        const alpha = 0.1; // Exponential moving average
        this.stats.averageResponseTime = 
            this.stats.averageResponseTime * (1 - alpha) + newTime * alpha;
    }
    
    /**
     * Öğrenme işlemi (arka planda)
     */
    async learn(text) {
        if (!text || text.trim().length === 0) return;
        
        // Arka planda öğren
        setTimeout(() => {
            if (this.predictionService) {
                this.predictionService.learnFromMessage(text);
            }
            
            if (this.historyManager) {
                this.historyManager.addMessage(text);
            }
            
            // Önbelleği temizle (yeni öğrenilen bilgiler için)
            this.resultCache.clear();
        }, 0);
    }
    
    /**
     * Toplu öğrenme
     */
    async learnBatch(texts) {
        texts.forEach(text => this.learn(text));
    }
    
    /**
     * Önbelleği temizle
     */
    clearCache() {
        this.resultCache.clear();
        this.prefetchCache.clear();
        
        if (this.predictionService) {
            this.predictionService.clearCache();
        }
        
        if (this.spellChecker) {
            this.spellChecker.clearCache();
        }
    }
    
    /**
     * İstatistikleri al
     */
    getStats() {
        return {
            ...this.stats,
            queueSize: this.queue.length,
            cacheSize: this.resultCache.size,
            prefetchCacheSize: this.prefetchCache.size,
            isRunning: this.isRunning,
            processing: this.processing
        };
    }
    
    /**
     * Konfigürasyonu güncelle
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }
    
    /**
     * Servisi yeniden başlat
     */
    restart() {
        this.stop();
        setTimeout(() => this.start(), 100);
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.BackgroundService = BackgroundService;
}
