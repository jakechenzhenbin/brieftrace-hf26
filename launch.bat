@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run the documented local setup first.
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8793"
".venv\Scripts\python.exe" -X utf8 server.py
pause
