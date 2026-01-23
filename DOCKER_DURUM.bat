@echo off
chcp 65001 >nul
title Docker Durum Kontrolu
color 0E

echo.
echo ==========================================
echo   Docker Durum Kontrolu
echo ==========================================
echo.

echo [1/3] Docker Desktop kontrol ediliyor...
docker --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Docker bulunamadi!
    echo Docker Desktop'i kurun ve baslatin!
    pause
    exit /b 1
)
docker --version
echo.

echo [2/3] Docker servisleri kontrol ediliyor...
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo ==========================================
    echo   DOCKER API'YE BAGLANILAMIYOR!
    echo ==========================================
    echo.
    echo Cozumler:
    echo 1. Docker Desktop'i acin ve baslatin
    echo 2. Docker Desktop'in tamamen yuklendiginden emin olun
    echo 3. WSL2 kurulu olmali (Windows icin)
    echo 4. Docker Desktop'i yeniden baslatin
    echo.
    pause
    exit /b 1
)

echo Docker API'ye baglanildi!
echo.

echo [3/3] Container durumu:
echo.
docker ps --filter "name=texthelper" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo Elasticsearch kontrol ediliyor...
curl -s http://localhost:9200 >nul 2>&1
if errorlevel 1 (
    echo Elasticsearch calisiyor mu: HAYIR
    echo Elasticsearch'i baslatmak icin: DOCKER_BASLAT.bat
) else (
    echo Elasticsearch calisiyor mu: EVET
)

echo.
echo Redis kontrol ediliyor...
docker ps --filter "name=texthelper-redis" --format "{{.Names}}" | findstr /C:"texthelper-redis" >nul
if errorlevel 1 (
    echo Redis calisiyor mu: HAYIR
    echo Redis'i baslatmak icin: DOCKER_BASLAT.bat
) else (
    echo Redis calisiyor mu: EVET
)

echo.
pause
