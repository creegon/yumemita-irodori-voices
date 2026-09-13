@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1
set GRADIO_ANALYTICS_ENABLED=False
set "VOICE_PY=%~dp0.runtime\Irodori-TTS\.venv\Scripts\python.exe"
if not exist "%VOICE_PY%" (
  echo First run SETUP_YUMEMITA.bat to install Python, dependencies and models.
  pause
  exit /b 1
)
"%VOICE_PY%" -X utf8 "%~dp0app\webui_yumemita.py" %*
if errorlevel 1 pause
endlocal
