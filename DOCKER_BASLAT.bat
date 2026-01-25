@echo off
chcp 65001 >nul
title Docker Servisleri Baslatma
color 0B
cd /d "%~dp0"

echo.
echo ==========================================
echo   Docker Servisleri Baslatiliyor
echo ==========================================
echo.

echo [0/4] Temiz baslat - eski container'lar kaldiriliyor...
docker rm -f texthelper-elasticsearch texthelper-redis
timeout /t 2 /nobreak >nul
echo [OK] Temizlendi.
echo.

echo [1/4] Docker kontrol ediliyor...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Docker bulunamadi! Docker Desktop kurun ve acin.
    pause
    exit /b 1
)
docker info >nul 2>&1
if errorlevel 1 (
    echo [UYARI] Docker engine yanit vermiyor. Docker Desktop acik mi?
    echo   Devam ediliyor...
) else (
    echo [OK] Docker calisiyor.
)
echo.

echo [2/4] Elasticsearch baslatiliyor...

:create_container
docker run -d --memory=512m --cpus=0.5 -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms256m -Xmx256m" --name texthelper-elasticsearch elasticsearch:8.11.0
if errorlevel 1 (
    echo [HATA] Elasticsearch container olusturulamadi!
    echo   Port 9200/9300 kullaniliyor olabilir. Eski container: docker rm -f texthelper-elasticsearch
    pause
    exit /b 1
)
echo [OK] Elasticsearch container olusturuldu.

echo.
echo Elasticsearch hazir olana kadar bekleniyor (30s-2dk, ilk kurulum uzun surebilir)...
set /a counter=0
:check_loop
timeout /t 5 /nobreak >nul
set /a counter+=1
curl -s -f -o nul http://localhost:9200
if not errorlevel 1 (
    echo [OK] Elasticsearch hazir!
    goto :elasticsearch_ready
)
if %counter% geq 24 (
    echo [UYARI] Elasticsearch 2 dakikada hazir olmadi!
    docker logs texthelper-elasticsearch --tail 15
    echo [BILGI] Yine de devam ediyoruz. Backend yerel sozluk kullanacak.
    goto :elasticsearch_ready
)
echo Bekleniyor... (%counter%/24)
goto :check_loop

:elasticsearch_ready
curl -s -f -o nul http://localhost:9200
if not errorlevel 1 (echo [OK] Elasticsearch calisiyor: http://localhost:9200) else (echo [UYARI] Elasticsearch yanit vermiyor.)

echo.
echo [3/4] Redis baslatiliyor...

set REDIS_PORT=6379
netstat -ano 2>nul | findstr ":6379" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo [BILGI] Port 6379 dolu, Redis 6380 portunda calisacak.
    set REDIS_PORT=6380
)

:create_redis_container
docker run -d --memory=128m --cpus=0.25 -p %REDIS_PORT%:6379 --name texthelper-redis redis:7-alpine
if errorlevel 1 (
    echo [HATA] Redis container olusturulamadi. Port %REDIS_PORT% kullaniliyor olabilir.
    goto :write_env
)
echo [OK] Redis container olusturuldu (port %REDIS_PORT%).

timeout /t 5 /nobreak >nul
docker exec texthelper-redis redis-cli ping >nul 2>&1
if not errorlevel 1 (echo [OK] Redis calisiyor: localhost:%REDIS_PORT%) else (echo [UYARI] Redis henuz yanit vermiyor.)

:write_env
echo ELASTICSEARCH_HOST=localhost:9200> env_docker.txt
echo REDIS_PORT=%REDIS_PORT%>> env_docker.txt
echo USE_ELASTICSEARCH=true>> env_docker.txt
echo [OK] env_docker.txt yazildi. PRODUCTION_BASLAT Redis + Elasticsearch kullanacak.

:show_status
echo.
echo ==========================================
echo   Docker Servisleri Durumu
echo ==========================================
echo.

REM Elasticsearch durumu
curl -s -f -o nul http://localhost:9200
if not errorlevel 1 (
    echo   [OK] Elasticsearch: http://localhost:9200 - CALISIYOR
) else (
    echo   [INFO] Elasticsearch: KULLANILAMIYOR (yerel sozluk kullanilacak)
)

REM Redis durumu
docker ps 2>nul | findstr /C:"texthelper-redis" >nul
if not errorlevel 1 (
    docker exec texthelper-redis redis-cli ping >nul 2>&1
    if not errorlevel 1 (
        echo   [OK] Redis: localhost:%REDIS_PORT% - CALISIYOR
    ) else (
        echo   [INFO] Redis: Container var, yanit yok
    )
) else (
    echo   [INFO] Redis: KULLANILAMIYOR
)

echo.
echo   Container durumu:
docker ps | findstr "texthelper"
if errorlevel 1 (
    echo   [BILGI] Container bulunamadi
)

echo.
echo ==========================================
echo   Sonraki adim: PRODUCTION_BASLAT.bat calistirin.
echo   env_docker.txt sayesinde Redis + Elasticsearch kullanilacak.
echo ==========================================
echo.
pause
