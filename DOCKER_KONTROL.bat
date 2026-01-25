@echo off
chcp 65001 >nul
title Docker Kontrol
cd /d "%~dp0"

echo.
echo === Docker / DOCKER_BASLAT Hizli Kontrol ===
echo.

echo [1] Docker yolu ve versiyon:
where docker 2>nul
if errorlevel 1 (echo    HATA: docker bulunamadi! Docker Desktop kurun.) else (docker --version 2>nul)

echo.
echo [2] Docker calisiyor mu? (docker info):
docker info 2>nul
if errorlevel 1 (
    echo    HATA: Docker calismiyor! Docker Desktop i acin, engine baslasin.
) else (
    echo    OK: Docker calisiyor.
)

echo.
echo [3] curl var mi? (Elasticsearch kontrolu icin):
where curl 2>nul
if errorlevel 1 (echo    UYARI: curl yok. Windows 10+ genelde var.) else (echo    OK: curl var.)

echo.
echo [4] Port 9200 (Elasticsearch) kullaniliyor mu?
netstat -ano 2>nul | findstr ":9200" | findstr "LISTENING"
if errorlevel 1 (echo    Hayir, port bos.) else (echo    Evet, biri kullaniyor.)

echo.
echo [5] Port 6379 (Redis) kullaniliyor mu?
netstat -ano 2>nul | findstr ":6379" | findstr "LISTENING"
if errorlevel 1 (echo    Hayir, port bos.) else (echo    Evet, biri kullaniyor.)

echo.
echo [6] texthelper container'lari:
docker ps -a 2>nul | findstr "texthelper"
if errorlevel 1 (echo    Yok.)

echo.
echo === Sonuc ===
echo - Docker yok / calismiyorsa: Docker Desktop acin, CMD yi yeniden acin.
echo - Port 9200/6379 doluyorsa: Ilgili programi kapatin veya DOCKER_BASLAT Redis i atlar.
echo - DOCKER_BASLAT yine de calismiyorsa: CMD ile acip "DOCKER_BASLAT.bat" yazin, hata mesajini okuyun.
echo.
pause
