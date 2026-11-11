@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\setup.ps1"
  if errorlevel 1 (
    echo Setup failed. See the message above.
    pause
    exit /b 1
  )
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\demo.ps1" -Suite case-study
set "DEMO_EXIT=%ERRORLEVEL%"
pause
exit /b %DEMO_EXIT%
