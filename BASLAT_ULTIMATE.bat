@echo off
setlocal
title TextHelper Ultimate Server
color 0A

echo ==================================================
echo TEXTHELPER ULTIMATE
echo Enterprise NLP Engine + UI + Docker
echo ==================================================
echo.

REM --- DOCKER KONTROL ---
echo [INFO] Docker altyapisi kontrol ediliyor...
docker info >nul 2>&1
if %errorlevel% neq 0 goto DockerMissing

echo [OK] Docker tespit edildi. Servisler baslatiliyor...
call docker-compose up -d
if %errorlevel% neq 0 (
    echo [UYARI] docker-compose komutu hatali. Docker Desktop acik mi?
    echo Lite moduna geciliyor...
    goto DockerMissing
)
echo [INFO] Redis ve Elasticsearch containerlari aktif.
goto StartBackend

:DockerMissing
echo [UYARI] Docker aktif degil veya yuklu degil.
echo [INFO] Sistem "Hybrid Lite" modunda calisacak:
echo        - Arama Motoru: SymSpell (Dahili)
echo        - Onbellek: RAM (Dahili)
echo [INFO] Bu mod tek kullanici icin en hizli moddur.
echo.

:StartBackend
REM --- BACKEND BASLATMA ---
echo [INFO] Python altyapisi hazirlaniyor...

if not exist "python_backend" (
    echo [KRITIK HATA] 'python_backend' klasoru bulunamadi!
    echo Lutfen scripti 'TextHelper' ana klasorunde calistirdiginizdan emin olun.
    pause
    exit /b
)

cd python_backend

echo [INFO] Tarayici aciliyor...
start "" "http://localhost:8000"

echo.
echo [BASLATILIYOR] Sunucu devreye aliniyor...
echo --------------------------------------------------
echo Dashboard: http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo --------------------------------------------------
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Sunucu beklenmedik sekilde kapandi!
    echo.
    echo MUHTEMEL COZUMLER:
    echo 1. Python yuklu degilse yukleyin.
    echo 2. Kutuphaneler eksik olabilir. Su komutu calistirin:
    echo    pip install -r requirements.txt
    echo 3. Port 8000 dolu olabilir.
)

echo.
echo Kapatmak icin bir tusa basin...
pause
