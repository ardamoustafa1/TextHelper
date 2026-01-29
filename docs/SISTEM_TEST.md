# 🧪 Sistem Test Kılavuzu

## ✅ Sistem Çalışıyor mu Kontrol Et

### 1. Backend Başlat
```
BASLAT.bat → Çift tıklayın
```

### 2. API Test (Tarayıcı)
```
http://localhost:8080/docs
```

### 3. Test Senaryoları

#### Senaryo 1: Tek Harf
```bash
curl -X POST "http://localhost:8080/api/v1/process" -H "Content-Type: application/json" -d "{\"text\": \"a\"}"
```

**Beklenen:** Öneri listesi (a ile başlayan kelimeler)

#### Senaryo 2: Kelime
```bash
curl -X POST "http://localhost:8080/api/v1/process" -H "Content-Type: application/json" -d "{\"text\": \"merhaba\"}"
```

**Beklenen:** Öneri listesi (merhaba ile ilgili)

#### Senaryo 3: Cümle
```bash
curl -X POST "http://localhost:8080/api/v1/process" -H "Content-Type: application/json" -d "{\"text\": \"merhaba nasıl\"}"
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
   http://localhost:8080/api/v1/health
   ```

3. **Manuel test:**
   - API docs'tan test et
   - WebSocket ile test et

---

## 🚀 Hızlı Çözüm

Eğer öneri yoksa:
1. Backend'i yeniden başlat: `BASLAT.bat`
2. Health check yap: `http://localhost:8080/api/v1/health`
3. API docs'tan test et: `http://localhost:8080/docs`

---

**Sistem artık düzgün çalışmalı!** ✅
