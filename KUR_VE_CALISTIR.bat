@echo off
chcp 65001 >nul
title TextHelper ULTIMATE - Kurulum ve Baslatma
color 0A

echo.
echo ==========================================
echo   TextHelper ULTIMATE - FULL SYSTEM
echo   Transformer + Elasticsearch
echo ==========================================
echo.

cd /d "%~dp0python_backend"

echo [1/6] Python kontrol ediliyor...
python --version
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)

echo.
echo [2/6] Transformers ve Torch kuruluyor...
python -m pip install transformers torch --quiet --disable-pip-version-check
if errorlevel 1 (
    echo UYARI: Transformers kurulamadi, devam ediliyor...
)

echo.
echo [3/6] Elasticsearch kontrol ediliyor...
curl -s http://localhost:9200 >nul 2>&1
if errorlevel 1 (
    echo.
    echo ==========================================
    echo   ELASTICSEARCH BULUNAMADI
    echo ==========================================
    echo.
    echo Docker Desktop calisiyor mu kontrol edin!
    echo.
    echo Manuel olarak baslatmak icin:
    echo   docker run -d -p 9200:9200 -p 9300:9300 ^
    echo     -e "discovery.type=single-node" ^
    echo     -e "xpack.security.enabled=false" ^
    echo     --name texthelper-elasticsearch ^
    echo     elasticsearch:8.11.0
    echo.
    echo Docker Desktop'i baslatip tekrar deneyin!
    echo.
    set /p continue="Elasticsearch olmadan devam etmek ister misiniz? (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
    set USE_ELASTICSEARCH=false
) else (
    echo Elasticsearch calisiyor!
    set USE_ELASTICSEARCH=true
)

echo.
echo [4/6] Sozluk dosyasi kontrol ediliyor...
if not exist "improvements\turkish_dictionary.json" (
    echo Sozluk olusturuluyor...
    python import_tdk_dictionary.py
)

echo.
echo [5/6] Environment variables ayarlaniyor...
set USE_TRANSFORMER=true
set USE_ELASTICSEARCH=%USE_ELASTICSEARCH%
set ELASTICSEARCH_HOST=localhost:9200

echo.
echo [6/6] Backend baslatiliyor...
echo.
echo ==========================================
echo   SISTEM DURUMU
echo ==========================================
echo.
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    WebSocket: ws://localhost:8000/ws
echo.
echo    OZELLIKLER:
if "%USE_TRANSFORMER%"=="true" (
    echo    - Transformer AI Modeli: AKTIF
) else (
    echo    - Transformer AI Modeli: PASIF
)
if "%USE_ELASTICSEARCH%"=="true" (
    echo    - Elasticsearch: AKTIF
) else (
    echo    - Elasticsearch: PASIF (Yerel sozluk kullaniliyor)
)
echo    - Redis Cache: AKTIF
echo    - ML Ogrenme: AKTIF
echo.
echo    Durdurmak icin Ctrl+C basin
echo.

timeout /t 3 /nobreak >nul
start http://localhost:8000/docs
timeout /t 1 /nobreak >nul
if exist "%~dp0index_ultimate.html" (
    start "" "%~dp0index_ultimate.html"
)

python main.py

pause
