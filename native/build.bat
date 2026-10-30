@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "MINGW=%LOCALAPPDATA%\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin"
set "PATH=%MINGW%;%PATH%"

if not exist "..\portable" mkdir "..\portable"

where gcc >nul 2>&1
if errorlevel 1 goto TCC

echo Kompilacja GCC...
windres -O coff app.rc -o app.res
if errorlevel 1 goto TCC
gcc -O2 -s -mwindows -o "..\portable\PrintQueueReset.exe" app.c spooler.c i18n.c app.res -ladvapi32 -lshell32 -lwinspool -lgdi32 -luser32 -lkernel32 -ldwmapi
if errorlevel 1 goto TCC
goto OK

:TCC
echo GCC blad — TCC...
set "TCC=%~dp0..\tools\tcc\tcc\tcc.exe"
if not exist "%TCC%" (
  echo Brak kompilatora.
  exit /b 1
)
"%TCC%" -mwindows -O2 -o "..\portable\PrintQueueReset.exe" app.c spooler.c i18n.c -Llib -ladvapi32 -lshell32 -lwinspool -luser32 -lgdi32 -lkernel32
if errorlevel 1 (
  echo Kompilacja nie powiodla sie.
  exit /b 1
)

:OK
for %%F in ("..\portable\PrintQueueReset.exe") do echo OK  %%~zF bajtow  %%~fF
copy /Y "..\CZYTAJ.txt" "..\portable\CZYTAJ.txt" >nul
copy /Y "..\LICENSE" "..\portable\LICENSE.txt" >nul
copy /Y "..\NOTICE" "..\portable\NOTICE.txt" >nul
exit /b 0
