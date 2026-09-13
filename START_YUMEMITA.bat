@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1
set GRADIO_ANALYTICS_ENABLED=False
set "VOICE_PY=%~dp0.runtime\Irodori-TTS\.venv\Scripts\python.exe"
if not exist "%VOICE_PY%" set "VOICE_PY=%~dp0app\python-runtime\python.exe"
if not exist "%VOICE_PY%" (
  echo Run setup.ps1 first, or copy this addon into the legacy Irodori-Voice-Pack root.
  pause
  exit /b 1
)
"%VOICE_PY%" -X utf8 "%~dp0app\webui_yumemita.py" %*
if errorlevel 1 pause
endlocal
