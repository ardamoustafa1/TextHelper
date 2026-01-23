@echo off
chcp 65001 >nul
title TextHelper ULTIMATE - Calistir
color 0A

echo.
echo ==========================================
echo   TextHelper ULTIMATE - BASLATILIYOR
echo ==========================================
echo.

cd /d "%~dp0python_backend"

echo [1/4] Python kontrol ediliyor...
python --version
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)

echo.
echo [2/4] Kutuphaneler kontrol ediliyor...
python -c "import fastapi, uvicorn; print('OK')" 2>nul
if errorlevel 1 (
    echo HATA: Kutuphaneler eksik!
    echo Kurulum: INSTALL_ALL.bat
    pause
    exit /b 1
)

echo.
echo [3/4] Environment variables ayarlaniyor...
set USE_TRANSFORMER=true
set USE_ELASTICSEARCH=false
set ELASTICSEARCH_HOST=localhost:9200

echo.
echo NOT: Docker OPSIYONEL!
echo - Elasticsearch icin: DOCKER_ELASTICSEARCH.bat calistirin
echo - Sistem Docker olmadan da calisir (yerel sozluk kullanir)
echo.

echo.
echo [4/4] Backend baslatiliyor...
echo.
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    WebSocket: ws://localhost:8000/ws
echo.
echo    Durdurmak icin Ctrl+C basin
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8000/docs
timeout /t 1 /nobreak >nul
if exist "%~dp0index_ultimate.html" (
    start "" "%~dp0index_ultimate.html"
)

python main.py

pause
