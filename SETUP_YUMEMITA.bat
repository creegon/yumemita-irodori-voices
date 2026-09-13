@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
if errorlevel 1 (
  echo.
  echo Setup failed. Keep the error message above and run this file again after fixing it.
  pause
  exit /b 1
)
echo.
echo Setup complete. Double-click START_YUMEMITA.bat to open the voice interface.
pause
endlocal
