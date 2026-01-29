@echo off
setlocal
title TextHelper Tum Ozellikler
color 0A

echo ==================================================
echo TEXTHELPER - TUM OZELLIKLER
echo BERT + GPT-2 + SymSpell
echo ==================================================
echo.

set USE_BERT=true
set USE_GPT=true
set USE_SYMSPELL=true
set OMP_NUM_THREADS=2
set MKL_NUM_THREADS=2
set USE_QUANTIZATION=true

docker info >nul 2>&1
if %errorlevel% equ 0 (call docker-compose up -d 2>nul)

echo [INFO] Port 8080 temizleniyor...
netstat -aon | findstr ":8080" | findstr "LISTENING" > port_check.tmp 2>nul || echo. > port_check.tmp
set /p PORT_CHECK=<port_check.tmp 2>nul
if not "%PORT_CHECK%"=="" (
    for /f "tokens=5" %%a in (port_check.tmp) do taskkill /F /PID %%a >nul 2>&1
)
if exist port_check.tmp del port_check.tmp

if not exist "python_backend" (
    echo [HATA] 'python_backend' bulunamadi.
    pause
    exit /b 1
)

cd python_backend
start "" "http://localhost:8080"
echo [BASLATILIYOR] http://localhost:8080
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

pause
