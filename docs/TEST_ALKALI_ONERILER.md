# 🧪 Alkalı Öneriler Test Rehberi

## ✅ Yapılan İyileştirmeler

### 1. **Alkalı Öneriler İçin:**
- ✅ **Relevance Filter:** Minimum score 0.1 → 0.3 (daha katı)
- ✅ **Son kelime prefix match:** 40% ağırlık (en önemli!)
- ✅ **Context bonus:** +2.0 skor (alkalı öneriler için)
- ✅ **Son kelime prefix match bonus:** +10.0 skor (context analysis'de)
- ✅ **Semantic similarity:** İyileştirildi (prefix match kontrolü)
- ✅ **Her zaman aktif:** Minimum 5 öneri ve 2 karakter varsa

### 2. **Kelime Sayısını Artırma:**
- ✅ **Morfoloji:** 50K → 100K base word (2x artış)
- ✅ **Suffix:** 30 → Tümü (daha fazla varyasyon)
- ✅ **Wikipedia:** 5K → 10K sayfa (2x artış)
- ✅ **Yaygın ifadeler:** Kombinasyonlar eklendi
- ✅ **Large Dictionary:** Tüm uzunluklar için aktif
- ✅ **Worker:** 6 → 8 (daha hızlı toplama)

---

## 🧪 Test Senaryoları

### Senaryo 1: "ürün al" yazınca

**BEKLENEN:**
- ✅ "al" ile başlayan öneriler öncelikli
- ✅ "alabilirsiniz", "alabilir misiniz", "alabilir miyim"
- ❌ "akıl", "akıllı" gibi alakasız öneriler filtrelenmeli

**TEST:**
```
1. "ürün al" yaz
2. Önerileri kontrol et
3. "al" ile başlayan öneriler önce gelmeli
4. Alakasız öneriler (akıl, akıllı) filtrelenmiş olmalı
```

---

### Senaryo 2: "merhaba nasıl" yazınca

**BEKLENEN:**
- ✅ "nasıl" ile başlayan öneriler öncelikli
- ✅ "nasıl yardımcı", "nasıl olabilirim", "nasıl yapabilirim"
- ❌ "nasıl" ile alakasız öneriler filtrelenmeli

**TEST:**
```
1. "merhaba nasıl" yaz
2. Önerileri kontrol et
3. "nasıl" ile başlayan öneriler önce gelmeli
4. Context-aware öneriler (yardımcı, olabilirim) öncelikli olmalı
```

---

### Senaryo 3: "sipariş durumu" yazınca

**BEKLENEN:**
- ✅ "durumu" ile başlayan öneriler öncelikli
- ✅ "durum", "durum sorgulama", "durum takibi"
- ❌ Alakasız öneriler filtrelenmeli

**TEST:**
```
1. "sipariş durumu" yaz
2. Önerileri kontrol et
3. "durumu" ile başlayan öneriler önce gelmeli
4. Context-aware öneriler (sorgulama, takibi) öncelikli olmalı
```

---

## 📊 Kelime Sayısı Testi

### Test:
```
1. KELIME_TOPLA.bat çalıştır
2. Kelime sayısını kontrol et
3. Hedef: 1M+ kelime
```

### Beklenen:
- ✅ **450K → 1M+ kelime**
- ✅ **Morfoloji:** 100K base → 1M+ variation
- ✅ **Wikipedia:** 10K sayfa
- ✅ **Yaygın ifadeler:** Kombinasyonlar eklendi

---

## ✅ Başarı Kontrolü

### Alkalı Öneriler:
1. **"ürün al"** → "al", "alabilirsiniz" (alkalı) ✅
2. **"merhaba nasıl"** → "nasıl", "nasıl yardımcı" (alkalı) ✅
3. **"sipariş durumu"** → "durumu", "durum" (alkalı) ✅

### Kelime Sayısı:
1. **"a" yaz** → 1000+ öneri (artırıldı) ✅
2. **"ak" yaz** → 500+ öneri (artırıldı) ✅
3. **"akı" yaz** → 200+ öneri (artırıldı) ✅

---

**Sistem artık hem alkalı hem kapsamlı!** ✅

**Alkalı öneriler + 1M+ kelime = En iyi sistem!** 🚀
