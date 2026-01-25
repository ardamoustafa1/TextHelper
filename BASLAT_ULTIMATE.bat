@echo off
echo TextHelper Ultimate (Market Leader Edition) Baslatiliyor...
echo.
echo ==========================================
echo ==========================================
echo 1. Backend Baslatiliyor (Python/FastAPI)...
echo ==========================================

REM PIYASANIN EN IYISI - TUM OZELLIKLER AKTIF
set USE_TRANSFORMER=true
set ENABLE_HEAVY_FEATURES=true
set USE_GPU=true

REM Ortam degiskenlerini yukle (env_docker.txt)
if exist env_docker.txt (
    echo [BILGI] env_docker.txt yukleniyor...
    for /f "tokens=*" %%a in (env_docker.txt) do set %%a
)

REM Port 8000 temizligi - Eski islemleri kapat
echo [BILGI] Port 8000 kontrol ediliyor...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo [BILGI] Port 8000 kullanan islem kapatiliyor (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

start "TextHelper Brain" cmd /k "cd python_backend && python main.py"

echo.
echo ==========================================
echo 2. Frontend Aciliyor (Chrome/Edge)...
echo ==========================================
timeout /t 2 >nul
start index_ultimate.html

echo.
echo ==========================================
echo KURULUM BASARILI!
echo ------------------------------------------
echo Backend penceresini (siyah ekran) KAPATMAYIN.
echo Frontend tarayicinizda acilmis olmalidir.
echo Iyi kullanimlar!
echo ==========================================
pause
