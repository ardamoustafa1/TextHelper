@echo off
chcp 65001 >nul
title TextHelper ULTIMATE - Docker ile Calistir
color 0A

echo.
echo ==========================================
echo   TextHelper ULTIMATE - DOCKER ILE
echo ==========================================
echo.

echo [1/5] Docker servisleri kontrol ediliyor...
call "%~dp0DOCKER_BASLAT.bat"
if errorlevel 1 (
    echo Docker servisleri baslatilamadi!
    pause
    exit /b 1
)

echo.
echo [2/5] Python kontrol ediliyor...
cd /d "%~dp0python_backend"
python --version
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)

echo.
echo [3/5] Kutuphaneler kontrol ediliyor...
python -c "import fastapi, uvicorn; print('OK')" 2>nul
if errorlevel 1 (
    echo HATA: Kutuphaneler eksik!
    echo Kurulum: INSTALL_ALL.bat
    pause
    exit /b 1
)

echo.
echo [4/5] Environment variables ayarlaniyor...
set USE_TRANSFORMER=true
set USE_ELASTICSEARCH=true
set ELASTICSEARCH_HOST=localhost:9200

echo.
echo [5/5] Backend baslatiliyor...
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
echo    - Transformer AI Modeli: AKTIF
echo    - Elasticsearch: AKTIF (Docker)
echo    - Redis Cache: AKTIF (Docker)
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
