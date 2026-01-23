"""
Büyük Türkçe Sözlük - 50,000+ Kelime
"""

import json
import os
from typing import List, Dict

class LargeTurkishDictionary:
    """Büyük Türkçe sözlük yöneticisi"""
    
    def __init__(self):
        self.words = []
        self.word_frequencies = {}
        self.categories = {}
        self.load_dictionary()
    
    def load_dictionary(self):
        """Sözlüğü yükle"""
        # JSON dosyasından yükle
        dict_file = os.path.join(os.path.dirname(__file__), "turkish_dictionary.json")
        
        if os.path.exists(dict_file):
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.words = data.get('words', [])
                    self.word_frequencies = data.get('frequencies', {})
                    self.categories = data.get('categories', {})
                    print(f"[OK] Buyuk sozluk yuklendi: {len(self.words)} kelime")
            except Exception as e:
                print(f"Sözlük yükleme hatası: {e}, varsayılan kullanılıyor")
                self.words = self._get_default_words()
                self._calculate_frequencies()
        else:
            # Varsayılan sözlük
            self.words = self._get_default_words()
            self._calculate_frequencies()
            print(f"[OK] Varsayilan sozluk yuklendi: {len(self.words)} kelime")
    
    def _get_default_words(self) -> List[str]:
        """Varsayılan kelime listesi (genişletilmiş)"""
        return [
            # Mantık kelimeleri (genişletilmiş)
            'mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal', 'mantıkça',
            'mantıkçı', 'mantıksallık', 'mantıksızca', 'mantıklılık',
            
            # Merhaba ve selamlaşma (genişletilmiş)
            'merhaba', 'merhaba size', 'merhaba nasıl', 'merhaba hoş', 'merhabalar',
            'selam', 'selamlar', 'selamun aleyküm', 'hoş geldiniz', 'hoş geldin',
            'hoşgeldiniz', 'hoşgeldin', 'günaydın', 'iyi günler', 'iyi akşamlar',
            'iyi geceler', 'merhaba nasılsınız', 'merhaba nasılsın',
            
            # Teşekkür (genişletilmiş)
            'teşekkür', 'teşekkürler', 'teşekkür ederim', 'teşekkür ederiz',
            'teşekkür ediyorum', 'teşekkür ediyoruz', 'teşekkürler ederim',
            'sağolun', 'sağ olun', 'sağol', 'sağ ol', 'minnettarım', 'minnettarız',
            
            # Yardım (genişletilmiş)
            'yardım', 'yardımcı', 'yardımcı olabilirim', 'yardım etmek',
            'yardımcı olmak', 'destek', 'destek olmak', 'destek vermek',
            'yardım edebilirim', 'yardımcı olabiliriz', 'destek verebilirim',
            'yardım istiyorum', 'yardıma ihtiyacım var',
            
            # Müşteri (genişletilmiş)
            'müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti',
            'müşteri temsilcisi', 'müşteri danışmanı', 'müşteri ilişkileri',
            'müşteri hizmeti', 'müşteri desteği', 'müşteri sorunları',
            
            # Sipariş (genişletilmiş)
            'sipariş', 'siparişiniz', 'sipariş takibi', 'sipariş durumu',
            'sipariş vermek', 'sipariş almak', 'sipariş iptal', 'sipariş iptali',
            'sipariş numarası', 'sipariş sorgulama', 'sipariş bilgisi',
            
            # Ara (genişletilmiş)
            'ara', 'araba', 'arama', 'aramak', 'arayabilirsiniz', 'arayabilirim',
            'arama yapmak', 'arama sonuçları', 'arama motoru', 'arama yap',
            'arama yapabilir misiniz', 'arama yapabilir miyim',
            
            # Aç (genişletilmiş)
            'açık', 'açmak', 'açıklama', 'açıklamak', 'açıklayabilirim',
            'açıklayabilir misiniz', 'açıklayabilir misin', 'açıklama yapmak',
            'açıklama istiyorum', 'açıklama yapabilir misiniz',
            
            # Nasıl (genişletilmiş)
            'nasıl', 'nasıl yardımcı', 'nasıl olabilirim', 'nasıl yapabilirim',
            'nasıl yapılır', 'nasıl kullanılır', 'nasıl çalışır', 'nasıl yapıyoruz',
            'nasıl yapabilirsiniz', 'nasıl yardımcı olabilirim',
            
            # Diğer yaygın kelimeler (genişletilmiş)
            'iyi', 'kötü', 'güzel', 'büyük', 'küçük', 'yeni', 'eski',
            'yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek', 'vermek', 'almak',
            'sorun', 'problem', 'çözüm', 'bilgi', 'detay', 'fiyat', 'ücret',
            'ürün', 'hizmet', 'kargo', 'teslimat', 'iade', 'değişim',
            'garanti', 'kampanya', 'indirim', 'ödeme', 'fatura', 'fiyat',
            'müşteri', 'destek', 'yardım', 'bilgi', 'sorun', 'çözüm',
            
            # Ek kelimeler (1000+ daha eklenebilir)
            # ... buraya binlerce kelime daha eklenecek
        ]
    
    def _calculate_frequencies(self):
        """Frekansları hesapla"""
        for i, word in enumerate(self.words):
            # İlk kelimeler daha yüksek frekans
            self.word_frequencies[word.lower()] = max(100 - i, 1)
    
    def search(self, prefix: str, max_results: int = 10) -> List[Dict]:
        """Prefix ile arama"""
        prefix_lower = prefix.lower()
        results = []
        
        for word in self.words:
            word_lower = word.lower()
            
            if word_lower.startswith(prefix_lower) and word_lower != prefix_lower:
                frequency = self.word_frequencies.get(word_lower, 1)
                score = (len(prefix_lower) / len(word_lower)) * (frequency / 100) * 8.0
                
                results.append({
                    'word': word,
                    'score': score,
                    'frequency': frequency
                })
        
        # Skora göre sırala
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def get_word_count(self) -> int:
        """Toplam kelime sayısı"""
        return len(self.words)
    
    def add_word(self, word: str, frequency: int = 1):
        """Yeni kelime ekle"""
        if word.lower() not in [w.lower() for w in self.words]:
            self.words.append(word)
            self.word_frequencies[word.lower()] = frequency

# Global instance
large_dictionary = LargeTurkishDictionary()
