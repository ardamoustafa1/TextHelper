@echo off
echo TextHelper Ultimate Baslatiliyor...
echo Docker konteynerlari hazirlaniyor...

docker-compose down
docker-compose up --build -d

echo.
echo Sistem baslatildi!
echo Backend: http://localhost:8080/docs
echo Frontend: index_ultimate.html dosyasini acabilirsiniz.
echo.
pause
