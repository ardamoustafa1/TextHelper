"""
TDK Sözlük Import Script
Büyük Türkçe sözlük oluşturur
"""

import json
import os
from improvements.tdk_dictionary_importer import TDKDictionaryImporter

def main():
    print("=" * 60)
    print("TDK Sözlük Import")
    print("=" * 60)
    print()
    
    importer = TDKDictionaryImporter()
    
    # Manuel kelime listesi (TDK'dan import edilebilir)
    # Gerçek projede buraya TDK API veya dosya import edilir
    tdk_words = [
        # A harfi
        'açık', 'açıklama', 'açmak', 'adım', 'adres', 'akıllı', 'akşam', 'alan',
        'alışveriş', 'almak', 'alt', 'amaç', 'anlamak', 'anne', 'ara', 'araba',
        'aralık', 'aramak', 'arkadaş', 'artık', 'aslında', 'atmak', 'ay', 'ayak',
        
        # M harfi - Mantık kelimeleri
        'mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal', 'mantıkça',
        'mantıkçı', 'mantıksallık', 'mantıksızca', 'mantıklılık', 'mantık bilimi',
        'mantık hatası', 'mantık kuralları', 'mantık sınavı',
        
        # Diğer önemli kelimeler
        'merhaba', 'selam', 'teşekkür', 'yardım', 'destek', 'hizmet',
        'müşteri', 'sipariş', 'ürün', 'fiyat', 'kargo', 'teslimat',
        'nasıl', 'neden', 'ne', 'nerede', 'ne zaman',
        'iyi', 'kötü', 'güzel', 'büyük', 'küçük',
        'yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek',
        
        # ... binlerce kelime daha eklenebilir
    ]
    
    # Kelimeleri ekle
    importer.words = tdk_words
    for i, word in enumerate(tdk_words):
        importer.frequencies[word.lower()] = max(100 - i, 1)
    
    # Büyük sözlük oluştur
    output_file = importer.generate_large_dictionary("turkish_dictionary.json")
    
    print()
    print(f"[OK] Sozluk olusturuldu: {output_file}")
    print(f"   Toplam kelime: {len(importer.words)}")
    print()
    print("Elasticsearch'e index'lemek icin:")
    print("  python main.py")
    print("  Sonra: POST /index_words")

if __name__ == "__main__":
    main()
