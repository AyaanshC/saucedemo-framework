@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run scripts\setup.ps1 once before opening the dashboard.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "scripts\dashboard_server.py"
if errorlevel 1 pause
