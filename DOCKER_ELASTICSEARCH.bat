@echo off
chcp 65001 >nul
title Elasticsearch Docker Baslatma
color 0B

echo.
echo ==========================================
echo   Elasticsearch Docker Baslatma
echo ==========================================
echo.

echo Docker Desktop calisiyor mu kontrol ediliyor...
docker --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Docker bulunamadi!
    echo Docker Desktop'i kurun ve baslatin!
    pause
    exit /b 1
)

echo Docker bulundu!
echo.

echo Mevcut container kontrol ediliyor...
docker ps -a --filter "name=texthelper-elasticsearch" --format "{{.Names}}" | findstr /C:"texthelper-elasticsearch" >nul
if not errorlevel 1 (
    echo Container zaten var, baslatiliyor...
    docker start texthelper-elasticsearch
    if errorlevel 1 (
        echo Container baslatilamadi, yeniden olusturuluyor...
        docker rm -f texthelper-elasticsearch
        goto :create
    )
    echo Container baslatildi!
) else (
    :create
    echo Yeni container olusturuluyor...
    docker run -d -p 9200:9200 -p 9300:9300 ^
      -e "discovery.type=single-node" ^
      -e "xpack.security.enabled=false" ^
      --name texthelper-elasticsearch ^
      elasticsearch:8.11.0
    
    if errorlevel 1 (
        echo HATA: Container olusturulamadi!
        echo Docker Desktop'in calistigindan emin olun!
        pause
        exit /b 1
    )
    
    echo Container olusturuldu ve baslatildi!
    echo Elasticsearch hazir olana kadar bekleniyor (10 saniye)...
    timeout /t 10 /nobreak >nul
)

echo.
echo ==========================================
echo   Elasticsearch Hazir!
echo ==========================================
echo.
echo   URL: http://localhost:9200
echo.
echo   Test etmek icin:
echo   curl http://localhost:9200
echo.
pause
