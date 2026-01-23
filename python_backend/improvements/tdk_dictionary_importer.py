"""
TDK Sözlük Import Script
Türkçe kelimeleri büyük sözlüğe ekler
"""

import json
import os
from typing import List, Dict

class TDKDictionaryImporter:
    """TDK sözlük import"""
    
    def __init__(self):
        self.words = []
        self.frequencies = {}
        
    def load_from_file(self, file_path: str):
        """Dosyadan yükle"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                    self.words = data.get('words', [])
                    self.frequencies = data.get('frequencies', {})
                else:
                    # Text dosyası - her satır bir kelime
                    self.words = [line.strip() for line in f if line.strip()]
                    # Frekansları hesapla
                    for i, word in enumerate(self.words):
                        self.frequencies[word.lower()] = max(100 - i, 1)
            
            print(f"✅ {len(self.words)} kelime yüklendi")
            return True
        except Exception as e:
            print(f"Yükleme hatası: {e}")
            return False
    
    def generate_large_dictionary(self, output_file: str = "turkish_dictionary.json"):
        """Büyük sözlük oluştur"""
        # TDK'dan gelen kelimeler + ek kelimeler
        all_words = []
        
        # TDK kelimeleri
        for word in self.words:
            all_words.append({
                'word': word,
                'frequency': self.frequencies.get(word.lower(), 1),
                'category': 'tdk'
            })
        
        # Ek müşteri hizmetleri kelimeleri
        customer_service_words = [
            'merhaba', 'selam', 'hoşgeldiniz', 'günaydın', 'iyi günler',
            'teşekkür', 'teşekkürler', 'teşekkür ederim', 'sağolun',
            'özür', 'özür dilerim', 'pardon', 'affedersiniz',
            'lütfen', 'rica', 'yardım', 'destek', 'hizmet',
            'sorun', 'problem', 'çözüm', 'bilgi', 'detay',
            'sipariş', 'ürün', 'fiyat', 'ücret', 'ödeme',
            'kargo', 'teslimat', 'iade', 'değişim', 'garanti'
        ]
        
        for word in customer_service_words:
            if word not in [w['word'] for w in all_words]:
                all_words.append({
                    'word': word,
                    'frequency': 50,
                    'category': 'customer_service'
                })
        
        # JSON'a kaydet
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'words': [w['word'] for w in all_words],
                'frequencies': {w['word'].lower(): w['frequency'] for w in all_words},
                'categories': {w['word'].lower(): w['category'] for w in all_words},
                'total_count': len(all_words)
            }, f, ensure_ascii=False, indent=2)
        
            print(f"[OK] Buyuk sozluk olusturuldu: {len(all_words)} kelime")
        return output_path

# Kullanım örneği
if __name__ == "__main__":
    importer = TDKDictionaryImporter()
    
    # Örnek: TDK kelimeleri dosyası varsa yükle
    # importer.load_from_file("tdk_words.txt")
    
    # Büyük sözlük oluştur
    importer.generate_large_dictionary()
