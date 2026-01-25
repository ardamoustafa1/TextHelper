"""
Sözlük Temizleme Scripti
- Anlamsız test kelimelerini temizler
- Sadece gerçek Türkçe kelimeleri tutar
"""

import json
import os
import re
from typing import List, Set

def is_valid_turkish_word(word: str) -> bool:
    """Kelime geçerli Türkçe kelime mi kontrol et"""
    if not word or len(word.strip()) == 0:
        return False
    
    word_lower = word.lower().strip()
    
    # 1. Anlamsız pattern'leri filtrele
    invalid_patterns = [
        r'abcdefg',  # Test kelimeleri
        r'abcdefgh',
        r'abcdefghi',
        r'qwerty',  # Klavye pattern'leri
        r'asdfgh',
        r'^[a-z]{1,2}$',  # Çok kısa anlamsız kombinasyonlar (a, ab, ac gibi - ama "ü" gibi tek harfli gerçek kelimeleri tut)
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, word_lower):
            return False
    
    # 2. Sadece Türkçe karakterler içermeli
    if not re.match(r'^[a-zçğıöşüA-ZÇĞIİÖŞÜ\s\-]+$', word):
        return False
    
    # 3. Çok uzun kelimeler (muhtemelen hata)
    if len(word) > 30:
        return False
    
    # 4. Tekrarlayan karakterler (aaa, bbb gibi)
    if re.match(r'^(.)\1{3,}$', word_lower):  # 4+ aynı karakter
        return False
    
    # 5. Sadece rakam veya özel karakter
    if re.match(r'^[0-9\W]+$', word):
        return False
    
    return True

def clean_dictionary(input_file: str = "turkish_dictionary.json", output_file: str = "turkish_dictionary.json"):
    """Sözlüğü temizle"""
    dict_file = os.path.join(os.path.dirname(__file__), input_file)
    
    if not os.path.exists(dict_file):
        print(f"[HATA] Dosya bulunamadi: {dict_file}")
        return
    
    print("=" * 60)
    print("SOZLUK TEMIZLENIYOR...")
    print("=" * 60)
    print()
    
    # Mevcut sözlüğü yükle
    try:
        with open(dict_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            words = data.get('words', [])
            frequencies = data.get('frequencies', {})
            categories = data.get('categories', {})
        
        print(f"[INFO] Mevcut kelime sayisi: {len(words):,}")
    except Exception as e:
        print(f"[HATA] Sözlük yüklenemedi: {e}")
        return
    
    # Kelimeleri temizle
    cleaned_words = []
    removed_words = []
    
    for word in words:
        if is_valid_turkish_word(word):
            cleaned_words.append(word)
        else:
            removed_words.append(word)
            # Frekans ve kategori'den de sil
            word_lower = word.lower()
            frequencies.pop(word_lower, None)
            categories.pop(word_lower, None)
    
    print(f"[OK] Temizlenen kelime sayisi: {len(cleaned_words):,}")
    print(f"[OK] Silinen kelime sayisi: {len(removed_words):,}")
    
    if removed_words:
        print()
        print("[INFO] Silinen örnek kelimeler:")
        for word in removed_words[:20]:  # İlk 20 örnek
            print(f"  - {word}")
        if len(removed_words) > 20:
            print(f"  ... ve {len(removed_words) - 20} kelime daha")
    
    # Frekansları güncelle (sadece temiz kelimeler için)
    cleaned_frequencies = {}
    cleaned_categories = {}
    
    for word in cleaned_words:
        word_lower = word.lower()
        if word_lower in frequencies:
            cleaned_frequencies[word_lower] = frequencies[word_lower]
        if word_lower in categories:
            cleaned_categories[word_lower] = categories[word_lower]
    
    # Kaydet
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    data = {
        'words': cleaned_words,
        'frequencies': cleaned_frequencies,
        'categories': cleaned_categories,
        'total_count': len(cleaned_words),
        'version': '4.1',
        'generated_at': '2026-01-23',
        'cleaned': True,
        'removed_count': len(removed_words)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print("TAMAMLANDI!")
    print("=" * 60)
    print(f"[OK] Temiz sözlük kaydedildi: {len(cleaned_words):,} kelime")
    print(f"[OK] Dosya: {output_path}")
    print()
    print("Şimdi gerçek kelimeleri eklemek için:")
    print("KELIME_OTOMATIK_INDIR.bat → Çift tıklayın")
    print("=" * 60)

if __name__ == "__main__":
    clean_dictionary()
