# Docker ile Elasticsearch + Redis Kullanımı

## Adımlar

### 1. DOCKER_BASLAT.bat
- Docker Desktop **açık** olmalı.
- Çift tıklayın. Script:
  - Eski container'ları siler (temiz başlangıç).
  - **Elasticsearch** (9200) ve **Redis** (6379 veya 6380) container'larını oluşturur.
  - Port 6379 doluysa Redis **6380** portunda çalışır.
  - `env_docker.txt` dosyasını yazar (ELASTICSEARCH_HOST, REDIS_PORT, USE_ELASTICSEARCH).

### 2. PRODUCTION_BASLAT.bat
- `env_docker.txt` varsa bu dosyadaki değişkenleri yükler.
- Backend Redis ve Elasticsearch’e bağlanır.

## Sıra Önemli
1. **Önce** `DOCKER_BASLAT.bat` çalıştırın.
2. **Sonra** `PRODUCTION_BASLAT.bat` çalıştırın.

## Sorun Giderme
- **"Elasticsearch KULLANILAMIYOR"**: Container 2 dakika içinde ayağa kalkmamış olabilir. `docker logs texthelper-elasticsearch` ile kontrol edin. Bazen ilk açılış 2–3 dakika sürer.
- **"Redis atlandi"**: Artık atlamıyoruz; 6379 doluysa Redis 6380’de çalışır.
- **Redis 6380’deyse**: `env_docker.txt` içinde `REDIS_PORT=6380` yazar. PRODUCTION_BASLAT bunu okur, ekstra bir şey yapmanız gerekmez.
