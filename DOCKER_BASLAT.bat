@echo off
chcp 65001 >nul
title Docker Servisleri Baslatma
color 0B

echo.
echo ==========================================
echo   Docker Servisleri Baslatiliyor
echo ==========================================
echo.

echo [1/3] Docker kontrol ediliyor...
docker --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Docker bulunamadi!
    echo Docker Desktop'i baslatin!
    pause
    exit /b 1
)
echo Docker bulundu!
echo.

echo [2/3] Elasticsearch baslatiliyor...
docker ps -a --filter "name=texthelper-elasticsearch" --format "{{.Names}}" | findstr /C:"texthelper-elasticsearch" >nul
if not errorlevel 1 (
    echo Container bulundu, baslatiliyor...
    docker start texthelper-elasticsearch
    if errorlevel 1 (
        echo Container baslatilamadi, yeniden olusturuluyor...
        docker rm -f texthelper-elasticsearch
        docker run -d -p 9200:9200 -p 9300:9300 ^
          -e "discovery.type=single-node" ^
          -e "xpack.security.enabled=false" ^
          -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" ^
          --name texthelper-elasticsearch ^
          elasticsearch:8.11.0
    )
) else (
    echo Yeni container olusturuluyor...
    docker run -d -p 9200:9200 -p 9300:9300 ^
      -e "discovery.type=single-node" ^
      -e "xpack.security.enabled=false" ^
      -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" ^
      --name texthelper-elasticsearch ^
      elasticsearch:8.11.0
)

echo Elasticsearch hazir olana kadar bekleniyor (15 saniye)...
timeout /t 15 /nobreak >nul

curl -s http://localhost:9200 >nul 2>&1
if errorlevel 1 (
    echo UYARI: Elasticsearch henuz hazir degil, biraz daha bekleyin...
) else (
    echo Elasticsearch hazir!
)

echo.
echo [3/3] Redis baslatiliyor...
docker ps -a --filter "name=texthelper-redis" --format "{{.Names}}" | findstr /C:"texthelper-redis" >nul
if not errorlevel 1 (
    echo Container bulundu, baslatiliyor...
    docker start texthelper-redis
    if errorlevel 1 (
        echo Container baslatilamadi, yeniden olusturuluyor...
        docker rm -f texthelper-redis
        docker run -d -p 6379:6379 --name texthelper-redis redis:7-alpine
    )
) else (
    echo Yeni container olusturuluyor...
    docker run -d -p 6379:6379 --name texthelper-redis redis:7-alpine
)

echo.
echo ==========================================
echo   Docker Servisleri Hazir!
echo ==========================================
echo.
echo   Elasticsearch: http://localhost:9200
echo   Redis: localhost:6379
echo.
echo   Container durumu:
docker ps --filter "name=texthelper" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
pause
