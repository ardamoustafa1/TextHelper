@echo off
chcp 65001 >nul
title TextHelper ULTIMATE - Full System (Transformer + Elasticsearch)
color 0A

echo.
echo ==========================================
echo   TextHelper ULTIMATE - FULL SYSTEM
echo   Transformer + Elasticsearch Aktif
echo ==========================================
echo.

cd /d "%~dp0python_backend"

echo [1/5] Python kutuphaneleri kontrol ediliyor...
python -c "import fastapi, uvicorn, elasticsearch, redis, transformers; print('OK')" 2>nul
if errorlevel 1 (
    echo HATA: Kutuphaneler eksik!
    echo Kurulum: INSTALL_ALL.bat
    pause
    exit /b 1
)

echo.
echo [2/5] Elasticsearch kontrol ediliyor...
curl -s http://localhost:9200 >nul 2>&1
if errorlevel 1 (
    echo Elasticsearch bulunamadi!
    echo.
    echo Docker Desktop calisiyor mu kontrol edin!
    echo Elasticsearch olmadan da calisir (yerel sozluk kullanilir)
    echo.
    set USE_ELASTICSEARCH=false
) else (
    echo Elasticsearch calisiyor!
    set USE_ELASTICSEARCH=true
)

echo.
echo [3/5] Sozluk dosyasi kontrol ediliyor...
if not exist "improvements\turkish_dictionary.json" (
    echo Sozluk olusturuluyor...
    python import_tdk_dictionary.py
)

echo.
echo [4/5] Environment variables ayarlaniyor...
set USE_TRANSFORMER=true
set USE_ELASTICSEARCH=true
set ELASTICSEARCH_HOST=localhost:9200

echo.
echo [5/5] Backend baslatiliyor...
echo.
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    WebSocket: ws://localhost:8000/ws
echo.
echo    OZELLIKLER:
echo    - Transformer AI Modeli: AKTIF
echo    - Elasticsearch: AKTIF
echo    - Redis Cache: AKTIF
echo    - ML Ogrenme: AKTIF
echo.
echo    Durdurmak icin Ctrl+C basin
echo.

timeout /t 3 /nobreak >nul
start http://localhost:8000/docs
timeout /t 1 /nobreak >nul
start "" "%~dp0index_ultimate.html"

python main.py

pause
