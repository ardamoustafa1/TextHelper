@echo off
setlocal
title TextHelper Docker - Redis + Elasticsearch
color 0B

echo ==================================================
echo TEXTHELPER DOCKER
echo Redis (6379) + Elasticsearch (9200)
echo ==================================================
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Docker yok veya calismiyor. Docker Desktop acik mi?
    pause
    exit /b 1
)

echo [INFO] docker-compose up -d...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [HATA] docker-compose basarisiz.
    pause
    exit /b 1
)

echo.
echo [OK] Redis ve Elasticsearch containerlari calisiyor.
echo      Sonra PRODUCTION_BASLAT.bat veya BASLAT_ULTIMATE.bat calistirin.
echo.
pause
