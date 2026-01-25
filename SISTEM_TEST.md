# 🧪 Sistem Test Kılavuzu

## ✅ Sistem Çalışıyor mu Kontrol Et

### 1. Backend Başlat
```
BASLAT.bat → Çift tıklayın
```

### 2. API Test (Tarayıcı)
```
http://localhost:8000/docs
```

### 3. Test Senaryoları

#### Senaryo 1: Tek Harf
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "a", "max_suggestions": 10}'
```

**Beklenen:** 10+ öneri (a ile başlayan kelimeler)

#### Senaryo 2: Kelime
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "merhaba", "max_suggestions": 10}'
```

**Beklenen:** 10+ öneri (merhaba ile ilgili)

#### Senaryo 3: Cümle
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "merhaba nasıl", "max_suggestions": 10}'
```

**Beklenen:** 10+ öneri (nasıl ile devam eden)

---

## 🔍 Sorun Tespiti

### Öneri Yok mu?

1. **Backend loglarını kontrol et:**
   - Trie index hazır mı?
   - Large dictionary yüklendi mi?
   - Hata var mı?

2. **Health check:**
   ```
   http://localhost:8000/health
   ```

3. **Manuel test:**
   - API docs'tan test et
   - WebSocket ile test et

---

## 🚀 Hızlı Çözüm

Eğer öneri yoksa:
1. Backend'i yeniden başlat: `BASLAT.bat`
2. Health check yap: `http://localhost:8000/health`
3. API docs'tan test et: `http://localhost:8000/docs`

---

**Sistem artık düzgün çalışmalı!** ✅
