# 🔧 Docker Sorun Giderme

## ❌ Yaygın Sorunlar ve Çözümleri

### 1. Redis Port Çakışması (6379)

**Hata:**
```
Bind for 0.0.0.0:6379 failed: port is already allocated
```

**Çözüm:**

#### Seçenek 1: Mevcut Redis Container'ı Durdur
```bash
docker stop texthelper-redis
docker rm texthelper-redis
```

#### Seçenek 2: Port Kullanan Process'i Bul ve Durdur
```bash
# Port 6379'u kullanan process'i bul
netstat -ano | findstr ":6379"

# Process ID'yi bulduktan sonra durdur
taskkill /PID <process_id> /F
```

#### Seçenek 3: Redis Olmadan Devam Et
**Redis opsiyoneldir!** Sistem Redis olmadan da çalışır (memory cache kullanılacak).

---

### 2. Elasticsearch Hazır Olmama

**Hata:**
```
[UYARI] Elasticsearch 2 dakika icinde hazir olmadi!
```

**Çözüm:**

#### Seçenek 1: Biraz Daha Bekle
Elasticsearch ilk başlatmada 3-5 dakika sürebilir. Biraz daha bekleyin.

#### Seçenek 2: Container Durumunu Kontrol Et
```bash
docker ps
docker logs texthelper-elasticsearch
```

#### Seçenek 3: Elasticsearch Olmadan Devam Et
**Elasticsearch opsiyoneldir!** Sistem Elasticsearch olmadan da çalışır (yerel sözlük kullanılacak).

---

### 3. Docker Desktop Çalışmıyor

**Hata:**
```
Docker bulunamadi!
```

**Çözüm:**
1. Docker Desktop'ı başlatın
2. Docker Desktop'ın tamamen yüklendiğinden emin olun
3. `docker --version` komutu ile test edin

---

## ✅ Hızlı Çözüm

### Redis Sorunu İçin:
```bash
# Mevcut container'ı durdur ve sil
docker stop texthelper-redis
docker rm texthelper-redis

# Yeniden başlat
DOCKER_BASLAT.bat
```

### Elasticsearch Sorunu İçin:
```bash
# Container durumunu kontrol et
docker ps
docker logs texthelper-elasticsearch

# Gerekirse yeniden başlat
docker restart texthelper-elasticsearch
```

---

## 🎯 Önemli Not

**Docker servisleri OPSİYONELDİR!**

Sistem Docker olmadan da mükemmel çalışır:
- ✅ **Elasticsearch yoksa:** Yerel sözlük kullanılır
- ✅ **Redis yoksa:** Memory cache kullanılır
- ✅ **Her ikisi de yoksa:** Sistem normal çalışır

**Docker sadece performans artışı sağlar, zorunlu değildir!**

---

## 🚀 Sistem Çalıştırma (Docker Olmadan)

Docker sorunları varsa, direkt sistemi başlatabilirsiniz:

```
PRODUCTION_BASLAT.bat → Çift tıklayın
```

Sistem Docker olmadan da çalışır! ✅
