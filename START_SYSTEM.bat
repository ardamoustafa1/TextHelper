@echo off
chcp 65001 >nul
title TextHelper ULTIMATE - Sistem Baslatma
color 0A

echo.
echo ==========================================
echo   TextHelper ULTIMATE - Sistem Baslatiliyor
echo ==========================================
echo.

cd /d "%~dp0python_backend"

echo [1/3] Python kutuphaneleri kontrol ediliyor...
python -c "import fastapi, uvicorn, elasticsearch, redis; print('OK')" 2>nul
if errorlevel 1 (
    echo HATA: Kutuphaneler eksik!
    echo Kurulum: INSTALL_ALL.bat
    pause
    exit /b 1
)

echo.
echo [2/3] Sozluk dosyasi kontrol ediliyor...
if not exist "improvements\turkish_dictionary.json" (
    echo Sozluk olusturuluyor...
    python import_tdk_dictionary.py
)

echo.
echo [3/3] Backend baslatiliyor...
echo.
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    WebSocket: ws://localhost:8000/ws
echo.
echo    Durdurmak icin Ctrl+C basin
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8000/docs

python main.py

pause
