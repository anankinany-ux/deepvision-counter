@echo off
REM Build script for Windows standalone app
REM Customer Counter Pro - Windows Build Script

echo Building Customer Counter Pro for Windows...
echo.

REM Check if pyinstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM Create the standalone executable
echo Creating standalone executable...
pyinstaller --name="CustomerCounterPro" ^
    --windowed ^
    --onefile ^
    --icon=assets/icon.ico ^
    --add-data="yolov8n.pt;." ^
    --add-data="config;config" ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=matplotlib ^
    --hidden-import=cv2 ^
    --hidden-import=ultralytics ^
    --hidden-import=lap ^
    --noconfirm ^
    counter_modern.py

REM Check if build was successful
if exist "dist\CustomerCounterPro.exe" (
    echo Build successful!
    echo.
    echo App location: dist\CustomerCounterPro.exe
    echo.
    echo Next steps:
    echo 1. Test the app: dist\CustomerCounterPro.exe
    echo 2. Create installer: Run Inno Setup with installer_script.iss
    echo.
) else (
    echo Build failed! Check errors above.
    exit /b 1
)

