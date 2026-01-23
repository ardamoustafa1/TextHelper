# 🚀 Kurulum ve Çalıştırma Adımları

## ⚡ Hızlı Kurulum (Otomatik)

### Windows:
```bash
KUR_VE_CALISTIR.bat
```

Bu script:
1. ✅ Transformers ve Torch kurar
2. ✅ Elasticsearch Docker'ı başlatır (varsa)
3. ✅ Sözlük dosyasını oluşturur
4. ✅ Backend'i başlatır

---

## 📋 Manuel Kurulum Adımları

### 1. Transformers ve Torch Kurulumu

```bash
cd python_backend
pip install transformers torch
```

**Not:** Bu büyük dosyalar (2-3 GB) indirebilir, biraz zaman alabilir.

---

### 2. Elasticsearch Docker Kurulumu

#### Docker Desktop'ı Başlatın
- Docker Desktop uygulamasını açın
- Çalıştığından emin olun

#### Container'ı Başlatın

**Yöntem 1: Batch Dosyası (Kolay)**
```bash
DOCKER_ELASTICSEARCH.bat
```

**Yöntem 2: Manuel**
```bash
docker run -d -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  --name texthelper-elasticsearch \
  elasticsearch:8.11.0
```

**Kontrol:**
```bash
curl http://localhost:9200
```

---

### 3. Environment Variables Ayarlama

**Windows (CMD):**
```cmd
set USE_TRANSFORMER=true
set USE_ELASTICSEARCH=true
set ELASTICSEARCH_HOST=localhost:9200
```

**Windows (PowerShell):**
```powershell
$env:USE_TRANSFORMER="true"
$env:USE_ELASTICSEARCH="true"
$env:ELASTICSEARCH_HOST="localhost:9200"
```

**Linux/Mac:**
```bash
export USE_TRANSFORMER=true
export USE_ELASTICSEARCH=true
export ELASTICSEARCH_HOST=localhost:9200
```

---

### 4. Backend'i Başlatma

```bash
cd python_backend
python main.py
```

---

## ✅ Kontrol

### Health Check:
```bash
curl http://localhost:8000/health
```

**Beklenen Yanıt:**
```json
{
  "status": "healthy",
  "transformer_loaded": true,
  "elasticsearch_available": true,
  "dictionary_size": 50
}
```

### API Test:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "man", "max_suggestions": 5}'
```

---

## 🐛 Sorun Giderme

### Docker Hatası:
- Docker Desktop çalışıyor mu kontrol edin
- `DOCKER_ELASTICSEARCH.bat` dosyasını çalıştırın

### Transformers Hatası:
- İnternet bağlantınızı kontrol edin
- Disk alanı yeterli mi kontrol edin (3+ GB gerekli)

### Elasticsearch Bağlantı Hatası:
- Container çalışıyor mu: `docker ps`
- Port 9200 kullanımda mı kontrol edin
- Elasticsearch olmadan da çalışır (yerel sözlük kullanır)

---

## 🎯 Sonuç

Sistem başarıyla kuruldu ve çalışıyor! 🎉

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws
