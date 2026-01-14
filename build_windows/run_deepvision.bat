@echo off
REM DeepVision Counter - Windows Launch Script
REM ==========================================

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║       DeepVision Counter                  ║
echo  ║       AI-Powered People Counting          ║
echo  ╚═══════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version

REM Navigate to project directory
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist ".venv" (
    echo.
    echo [2/3] Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist ".venv\Lib\site-packages\ultralytics" (
    echo.
    echo [2/3] Installing dependencies (first time only)...
    pip install -r requirements.txt
) else (
    echo [2/3] Dependencies already installed
)

echo.
echo [3/3] Starting DeepVision Counter...
echo.

REM Run the application
python deepvision_counter.py

REM Keep window open if app crashes
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)
