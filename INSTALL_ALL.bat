@echo off
chcp 65001 >nul
title TextHelper ULTIMATE - Eksiksiz Kurulum
color 0A

echo.
echo ==========================================
echo   TextHelper ULTIMATE - EKSIKSIZ KURULUM
echo   Tüm iyileştirmeler kuruluyor...
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
echo [2/6] Pip guncelleniyor...
python -m pip install --upgrade pip --quiet

echo.
echo [3/6] Temel kutuphaneler kuruluyor...
python -m pip install fastapi uvicorn[standard] websockets --quiet
if errorlevel 1 (
    echo HATA: Temel kutuphaneler kurulamadi!
    pause
    exit /b 1
)

echo.
echo [4/6] NLP ve yazim duzeltme kutuphaneleri...
python -m pip install autocorrect textdistance fuzzywuzzy python-Levenshtein --quiet

echo.
echo [5/6] Cache ve veritabani...
python -m pip install redis hiredis elasticsearch --quiet

echo.
echo [6/6] Diger kutuphaneler...
python -m pip install pydantic python-multipart numpy --quiet

echo.
echo ==========================================
echo   TDK Sozluk Import
echo ==========================================
echo.
python import_tdk_dictionary.py

echo.
echo ==========================================
echo   KURULUM TAMAMLANDI!
echo ==========================================
echo.
echo Olusturulan dosyalar:
echo   - turkish_dictionary.json
echo   - improvements/ klasoru
echo.
echo Baslatmak icin:
echo   cd python_backend
echo   python main.py
echo.
echo Opsiyonel: Transformer modeli (buyuk dosyalar)
echo   python -m pip install transformers torch
echo   set USE_TRANSFORMER=true
echo.
echo Opsiyonel: Elasticsearch Docker
echo   docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0
echo   set USE_ELASTICSEARCH=true
echo.
pause
