@echo off
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "VENV=%SCRIPT_DIR%.venv"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LAUNCHER=%STARTUP%\inputtracker.vbs"
set "DATA_DIR=%USERPROFILE%\.inputtracker"

echo ^> Creating Python virtual environment...
python -m venv "%VENV%"
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ^> Installing dependencies...
"%VENV%\Scripts\pip" install --quiet --upgrade pip
"%VENV%\Scripts\pip" install --quiet -r "%SCRIPT_DIR%requirements.txt"

echo ^> Creating data directory...
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

echo ^> Installing startup launcher...
(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.Run Chr^(34^) ^& "%VENV%\Scripts\pythonw.exe" ^& Chr^(34^) ^& " " ^& Chr^(34^) ^& "%SCRIPT_DIR%app.py" ^& Chr^(34^), 0, False
) > "%LAUNCHER%"

echo ^> Starting InputTracker...
start "" "%VENV%\Scripts\pythonw.exe" "%SCRIPT_DIR%app.py"

echo.
echo Done. InputTracker is starting in your system tray.
echo.
echo   IMPORTANT - if Windows Security prompts for input monitoring access,
echo   click Allow.
echo.
echo   To stop:    taskkill /f /im pythonw.exe
echo   To uninstall auto-start: del "%LAUNCHER%"
echo   Data lives: %DATA_DIR%\
echo.
pause
