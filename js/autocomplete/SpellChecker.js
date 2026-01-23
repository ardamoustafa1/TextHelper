/**
 * Spell Checker - Yazım Düzeltme Servisi
 * Levenshtein distance algoritması ile yazım hatalarını düzeltir
 */

class SpellChecker {
    constructor() {
        // Kelime veritabanı
        this.dictionary = new Set();
        
        // Önbellek
        this.cache = new Map();
        this.cacheMaxSize = 500;
        
        // Konfigürasyon
        this.config = {
            maxDistance: 3,           // Maksimum edit distance
            maxSuggestions: 5,        // Maksimum öneri sayısı
            minWordLength: 2,         // Minimum kelime uzunluğu
            cacheTimeout: 300000       // 5 dakika
        };
        
        // Türkçe karakter eşleştirmeleri (klavye hataları için)
        this.charMappings = {
            'i': ['ı', 'İ'],
            'ı': ['i', 'İ'],
            'I': ['ı', 'i', 'İ'],
            'İ': ['i', 'ı', 'I'],
            'ş': ['s', 'Ş'],
            'Ş': ['s', 'ş'],
            'ğ': ['g', 'Ğ'],
            'Ğ': ['g', 'ğ'],
            'ü': ['u', 'Ü'],
            'Ü': ['u', 'ü'],
            'ö': ['o', 'Ö'],
            'Ö': ['o', 'ö'],
            'ç': ['c', 'Ç'],
            'Ç': ['c', 'ç']
        };
        
        // Başlat
        this._initialize();
    }
    
    /**
     * Sözlüğü başlat
     */
    _initialize() {
        if (typeof TurkishDictionary !== 'undefined') {
            // Tüm kelimeleri ekle
            TurkishDictionary.commonWords.forEach(word => {
                this.dictionary.add(word.toLowerCase());
            });
            
            // Genişletilmiş sözlüğü yükle
            this._loadExtendedDictionary();
            
            console.log(`SpellChecker initialized with ${this.dictionary.size} words`);
        }
    }
    
    /**
     * Genişletilmiş sözlüğü yükle
     */
    _loadExtendedDictionary() {
        // Ek Türkçe kelimeler (binlerce kelime)
        const extendedWords = [
            // A harfi ile başlayanlar
            'açık', 'açıklama', 'açmak', 'adım', 'adres', 'akıllı', 'akşam', 'alan', 'alışveriş',
            'almak', 'alt', 'amaç', 'anlamak', 'anne', 'ara', 'araba', 'aralık', 'aramak',
            'arkadaş', 'artık', 'aslında', 'atmak', 'ay', 'ayak', 'ayrı', 'az',
            
            // B harfi ile başlayanlar
            'baba', 'bakmak', 'banka', 'banyo', 'barış', 'baş', 'başarı', 'başka', 'başlamak',
            'bayram', 'bebek', 'beklemek', 'belge', 'belki', 'ben', 'beyaz', 'bırakmak',
            'bile', 'bilgi', 'bilgisayar', 'bilmek', 'bir', 'biraz', 'birçok', 'birkaç',
            'birşey', 'biz', 'boş', 'boy', 'boyun', 'bulmak', 'buluşmak', 'büyük', 'büyümek',
            
            // C harfi ile başlayanlar
            'can', 'canlı', 'cevap', 'cihaz', 'cuma', 'cumartesi', 'çabuk', 'çalışmak',
            'çanta', 'çay', 'çekmek', 'çevre', 'çıkmak', 'çift', 'çocuk', 'çok', 'çözüm',
            
            // D harfi ile başlayanlar
            'dağ', 'daha', 'dakika', 'dans', 'dar', 'değer', 'değil', 'değişmek', 'demek',
            'deniz', 'derin', 'ders', 'devam', 'devlet', 'dikkat', 'dil', 'dinlemek',
            'diş', 'doğru', 'doğum', 'doktor', 'dokunmak', 'dolmak', 'dolu', 'dönmek',
            'dönüş', 'dünya', 'düşünmek', 'düzen', 'düzgün',
            
            // E harfi ile başlayanlar
            'eğer', 'ekmek', 'el', 'elektrik', 'emek', 'en', 'enerji', 'erken', 'ertesi',
            'eski', 'etmek', 'ev', 'evet', 'evlenmek', 'eylem',
            
            // F harfi ile başlayanlar
            'fark', 'farklı', 'fayda', 'fazla', 'film', 'fiyat', 'fotoğraf', 'futbol',
            
            // G harfi ile başlayanlar
            'gazete', 'gece', 'geç', 'geçmek', 'gelmek', 'genç', 'geniş', 'gerçek',
            'getirmek', 'gezmek', 'gibi', 'girmek', 'gitmek', 'görmek', 'göz', 'güç',
            'güçlü', 'gülmek', 'gün', 'güneş', 'güzel', 'güven',
            
            // H harfi ile başlayanlar
            'haber', 'hadi', 'hak', 'haklı', 'hal', 'hala', 'halk', 'hangi', 'hanım',
            'hasta', 'hatırlamak', 'hayat', 'hayır', 'hazır', 'hemen', 'henüz', 'her',
            'herkes', 'hesap', 'heyecan', 'hızlı', 'hiç', 'hoş', 'huzur',
            
            // I-İ harfi ile başlayanlar
            'ılık', 'ısı', 'iç', 'için', 'içmek', 'için', 'ihtiyaç', 'ikinci', 'ile',
            'ileri', 'ilgili', 'ilk', 'imkan', 'inanmak', 'ince', 'insan', 'ip',
            'istemek', 'iş', 'işlem', 'iyi', 'izlemek',
            
            // J-K harfi ile başlayanlar
            'jandarma', 'kadın', 'kalem', 'kalmak', 'kalp', 'kamera', 'kan', 'kapı',
            'kar', 'karar', 'kardeş', 'kart', 'kasaba', 'kat', 'katılmak', 'kaybetmek',
            'kayıt', 'kaza', 'kazanmak', 'kendi', 'kent', 'kesmek', 'kırmızı', 'kısa',
            'kış', 'kitap', 'kız', 'kolay', 'komşu', 'konu', 'konuşmak', 'korkmak',
            'koymak', 'köy', 'kulak', 'kullanmak', 'kültür', 'küçük', 'kütüphane',
            
            // L harfi ile başlayanlar
            'lamba', 'lazım', 'lezzet', 'liman', 'liste', 'lokanta', 'lütfen',
            
            // M harfi ile başlayanlar
            'maç', 'makine', 'maliyet', 'mama', 'mavi', 'mekan', 'merhaba', 'mesaj',
            'meslek', 'metin', 'meyve', 'mezar', 'mıknatıs', 'milyon', 'mimari', 'mobil',
            'moda', 'mola', 'müzik', 'müşteri', 'mutlu', 'mutluluk',
            
            // N harfi ile başlayanlar
            'nasıl', 'ne', 'neden', 'nerede', 'neredeyse', 'neşe', 'neşeli', 'net',
            'numara', 'nüfus',
            
            // O-Ö harfi ile başlayanlar
            'oda', 'okul', 'okumak', 'olmak', 'on', 'onay', 'ön', 'önemli', 'önce',
            'öğle', 'öğrenmek', 'öğretmen', 'ölçü', 'ölmek', 'önlemek', 'örnek',
            'özel', 'özür',
            
            // P harfi ile başlayanlar
            'paket', 'para', 'park', 'parti', 'pasaport', 'patlamak', 'pazar', 'peki',
            'pencere', 'perde', 'pilot', 'plan', 'plastik', 'polis', 'portakal', 'posta',
            'program', 'proje', 'pul',
            
            // R harfi ile başlayanlar
            'radyo', 'rahat', 'rapor', 'renk', 'resim', 'rica', 'rüzgar',
            
            // S-Ş harfi ile başlayanlar
            'saat', 'sabah', 'sadece', 'sağ', 'sağlık', 'sahip', 'saklamak', 'salon',
            'sanat', 'sandalye', 'sanmak', 'sarı', 'satmak', 'sayfa', 'sayı', 'sebep',
            'seçmek', 'sefer', 'sekmek', 'selam', 'sen', 'serbest', 'sergi', 'ses',
            'sevgi', 'sevmek', 'seyahat', 'sıcak', 'sıfır', 'sık', 'sıkılmak', 'sınav',
            'sınıf', 'sıra', 'sistem', 'site', 'soğuk', 'sokak', 'sol', 'sorun',
            'sormak', 'soru', 'soy', 'spor', 'su', 'süre', 'sürmek', 'şarkı', 'şehir',
            'şekil', 'şimdi', 'şirket', 'şoför', 'şu', 'şükür',
            
            // T harfi ile başlayanlar
            'tabak', 'taban', 'tablo', 'tamam', 'tane', 'taraf', 'tarih', 'tarife',
            'tasarım', 'tatil', 'tatmak', 'tavsiye', 'taze', 'tebrik', 'tecrübe',
            'tehlike', 'tek', 'teklif', 'telefon', 'televizyon', 'temiz', 'temizlemek',
            'tenis', 'teori', 'tercih', 'terlik', 'teslim', 'test', 'teşekkür', 'teyze',
            'tıp', 'trafik', 'tren', 'turist', 'turizm', 'tutmak', 'tuz', 'tüketmek',
            'türk', 'türkçe', 'türlü',
            
            // U-Ü harfi ile başlayanlar
            'ucuz', 'uçak', 'uçmak', 'ufak', 'ulus', 'umut', 'unutmak', 'uygun',
            'uyku', 'uyumak', 'uzak', 'uzun', 'ücret', 'ülke', 'üniversite', 'ürün',
            'üst', 'üye', 'üzgün', 'üzülmek',
            
            // V harfi ile başlayanlar
            'vakit', 'vapur', 'var', 'varmak', 'vasıta', 've', 'vejetaryen', 'veri',
            'vermek', 'vesile', 'veteriner', 'video', 'vize', 'vücut',
            
            // Y harfi ile başlayanlar
            'ya', 'yabancı', 'yağ', 'yağmur', 'yakın', 'yalnız', 'yan', 'yanlış',
            'yapmak', 'yarın', 'yasak', 'yaş', 'yaşamak', 'yavaş', 'yaz', 'yazmak',
            'yemek', 'yen', 'yeni', 'yer', 'yeşil', 'yıl', 'yıldız', 'yine', 'yol',
            'yolcu', 'yorgun', 'yorum', 'yumurta', 'yurt', 'yüz', 'yüzde', 'yüzük',
            
            // Z harfi ile başlayanlar
            'zaman', 'zamir', 'zarf', 'zarif', 'zaten', 'zayıf', 'zehir', 'zeka',
            'zengin', 'zeytin', 'zil', 'ziraat', 'ziyaret', 'zor', 'zorunlu', 'zulüm'
        ];
        
        // Kelimeleri ekle
        extendedWords.forEach(word => {
            this.dictionary.add(word.toLowerCase());
        });
    }
    
    /**
     * Sözlüğe kelime ekle
     */
    addWord(word) {
        if (word && word.length >= this.config.minWordLength) {
            this.dictionary.add(word.toLowerCase());
            this.cache.clear(); // Önbelleği temizle
        }
    }
    
    /**
     * Toplu kelime ekle
     */
    addWords(words) {
        words.forEach(word => this.addWord(word));
    }
    
    /**
     * Kelimeyi kontrol et ve düzeltmeleri öner
     * @param {string} word - Kontrol edilecek kelime
     * @returns {Array} - Düzeltme önerileri [{word, distance, score}]
     */
    check(word) {
        if (!word || word.length < this.config.minWordLength) {
            return [];
        }
        
        const normalizedWord = word.toLowerCase();
        
        // Önbellekte var mı?
        const cached = this._getFromCache(normalizedWord);
        if (cached) return cached;
        
        // Kelime sözlükte var mı?
        if (this.dictionary.has(normalizedWord)) {
            return []; // Hata yok
        }
        
        // Kısa kelimeler (3 karakter ve altı) için yazım hatası kontrolünü atla
        // Çünkü bunlar genellikle prefix'lerdir (örn: "man" -> "mantık")
        if (normalizedWord.length <= 3) {
            return []; // Prefix olabilir, yazım hatası değil
        }
        
        // Düzeltme önerileri bul
        const suggestions = this._findSuggestions(normalizedWord);
        
        // Önbelleğe kaydet
        this._addToCache(normalizedWord, suggestions);
        
        return suggestions;
    }
    
    /**
     * Düzeltme önerileri bul
     */
    _findSuggestions(word) {
        const suggestions = [];
        const maxDistance = Math.min(this.config.maxDistance, Math.floor(word.length / 2));
        
        // 1. Levenshtein distance ile ara
        this.dictionary.forEach(dictWord => {
            const distance = this._levenshteinDistance(word, dictWord);
            
            if (distance <= maxDistance && distance > 0) {
                suggestions.push({
                    word: dictWord,
                    distance: distance,
                    score: this._calculateScore(word, dictWord, distance)
                });
            }
        });
        
        // 2. Türkçe karakter hatalarını kontrol et
        const turkishSuggestions = this._checkTurkishChars(word);
        turkishSuggestions.forEach(s => {
            if (!suggestions.find(ex => ex.word === s.word)) {
                suggestions.push(s);
            }
        });
        
        // 3. Prefix eşleşmeleri (hızlı tamamlama)
        const prefixSuggestions = this._checkPrefix(word);
        prefixSuggestions.forEach(s => {
            if (!suggestions.find(ex => ex.word === s.word)) {
                suggestions.push(s);
            }
        });
        
        // Skora göre sırala ve en iyilerini döndür
        return suggestions
            .sort((a, b) => a.score - b.score) // Düşük skor = daha iyi
            .slice(0, this.config.maxSuggestions)
            .map(s => ({
                word: s.word,
                distance: s.distance,
                score: s.score,
                confidence: this._calculateConfidence(s.score)
            }));
    }
    
    /**
     * Levenshtein distance hesapla
     */
    _levenshteinDistance(str1, str2) {
        const len1 = str1.length;
        const len2 = str2.length;
        
        // Kısa yol: uzunluk farkı çok büyükse
        if (Math.abs(len1 - len2) > this.config.maxDistance) {
            return this.config.maxDistance + 1;
        }
        
        // Dinamik programlama tablosu
        const matrix = [];
        
        for (let i = 0; i <= len1; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= len2; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= len1; i++) {
            for (let j = 1; j <= len2; j++) {
                if (str1[i - 1] === str2[j - 1]) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j] + 1,      // Silme
                        matrix[i][j - 1] + 1,      // Ekleme
                        matrix[i - 1][j - 1] + 1  // Değiştirme
                    );
                }
            }
        }
        
        return matrix[len1][len2];
    }
    
    /**
     * Türkçe karakter hatalarını kontrol et
     */
    _checkTurkishChars(word) {
        const suggestions = [];
        
        // Her karakter için alternatifleri dene
        for (let i = 0; i < word.length; i++) {
            const char = word[i];
            const alternatives = this.charMappings[char];
            
            if (alternatives) {
                alternatives.forEach(alt => {
                    const variant = word.substring(0, i) + alt + word.substring(i + 1);
                    
                    if (this.dictionary.has(variant)) {
                        suggestions.push({
                            word: variant,
                            distance: 1,
                            score: 0.5 // Türkçe karakter hatası düşük skor
                        });
                    }
                });
            }
        }
        
        return suggestions;
    }
    
    /**
     * Prefix eşleşmeleri kontrol et
     */
    _checkPrefix(word) {
        const suggestions = [];
        const prefix = word.substring(0, Math.max(2, word.length - 2));
        
        this.dictionary.forEach(dictWord => {
            if (dictWord.startsWith(prefix) && dictWord !== word) {
                const distance = this._levenshteinDistance(word, dictWord);
                
                if (distance <= this.config.maxDistance) {
                    suggestions.push({
                        word: dictWord,
                        distance: distance,
                        score: distance * 1.2 // Prefix eşleşmesi bonusu
                    });
                }
            }
        });
        
        return suggestions;
    }
    
    /**
     * Skor hesapla (düşük = daha iyi)
     */
    _calculateScore(word, dictWord, distance) {
        let score = distance;
        
        // Uzunluk farkı cezası
        const lengthDiff = Math.abs(word.length - dictWord.length);
        score += lengthDiff * 0.5;
        
        // Başlangıç eşleşmesi bonusu
        if (dictWord.startsWith(word[0])) {
            score -= 0.3;
        }
        
        // Ortak karakter oranı
        const commonChars = this._countCommonChars(word, dictWord);
        const commonRatio = commonChars / Math.max(word.length, dictWord.length);
        score -= commonRatio * 0.5;
        
        return Math.max(0, score);
    }
    
    /**
     * Ortak karakter sayısını hesapla
     */
    _countCommonChars(str1, str2) {
        const chars1 = str1.split('').sort();
        const chars2 = str2.split('').sort();
        let count = 0;
        let i = 0, j = 0;
        
        while (i < chars1.length && j < chars2.length) {
            if (chars1[i] === chars2[j]) {
                count++;
                i++;
                j++;
            } else if (chars1[i] < chars2[j]) {
                i++;
            } else {
                j++;
            }
        }
        
        return count;
    }
    
    /**
     * Güven skorunu hesapla
     */
    _calculateConfidence(score) {
        if (score < 1) return 0.95;      // Çok yüksek güven
        if (score < 2) return 0.85;      // Yüksek güven
        if (score < 3) return 0.70;      // Orta güven
        return 0.50;                     // Düşük güven
    }
    
    /**
     * Önbellekten al
     */
    _getFromCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;
        
        // Zaman aşımı kontrolü
        if (Date.now() - cached.timestamp > this.config.cacheTimeout) {
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
     * Önbelleği temizle
     */
    clearCache() {
        this.cache.clear();
    }
    
    /**
     * Sözlük istatistikleri
     */
    getStats() {
        return {
            dictionarySize: this.dictionary.size,
            cacheSize: this.cache.size
        };
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.SpellChecker = SpellChecker;
}
