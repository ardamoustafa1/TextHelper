@echo off
chcp 65001 >nul
title TextHelper - Kelime Topla
color 0E

echo.
echo ==========================================
echo   TEXTHELPER - KELIME TOPLAMA
echo ==========================================
echo.
echo [UYARI] Bu islem 5-15 dakika surebilir
echo [INFO] 1M+ kelime toplanacak
echo.
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/2] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    pause
    exit /b 1
)
echo [OK] Python bulundu!

echo.
echo [2/2] Kelime toplama baslatiliyor...
echo.

cd python_backend\improvements
python mega_word_collector.py

echo.
echo [TAMAMLANDI] Kelime toplama bitti!
echo.
echo [ONEMLI] Yeni kelimelerin yuklenmesi icin backend'i YENIDEN BASLATIN:
echo          PRODUCTION_BASLAT.bat veya python main.py
echo.
pause
