@echo off
chcp 65001 >nul
cd /d "%~dp0"

if exist "%~dp0portable\PrintQueueReset.exe" (
    start "" "%~dp0portable\PrintQueueReset.exe" %*
    exit /b 0
)
if exist "%~dp0dist\PrintQueueReset.exe" (
    start "" "%~dp0dist\PrintQueueReset.exe" %*
    exit /b 0
)

echo Brak portable\PrintQueueReset.exe
echo Zbuduj: native\build.bat  albo  build.bat
pause
exit /b 1
