@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Budowanie portable EXE (bez zaleznosci od Pythona)...
python -m PyInstaller --noconfirm --clean PrintQueueReset.spec
if errorlevel 1 (
    echo Blad budowania.
    pause
    exit /b 1
)

if not exist "portable" mkdir portable
copy /Y "dist\PrintQueueReset.exe" "portable\PrintQueueReset.exe" >nul
copy /Y "CZYTAJ.txt" "portable\CZYTAJ.txt" >nul
copy /Y "LICENSE" "portable\LICENSE.txt" >nul
copy /Y "NOTICE" "portable\NOTICE.txt" >nul
echo.
echo Gotowe: portable\PrintQueueReset.exe
pause
