#!/bin/bash
# Simple App Builder for Customer Counter Pro
# Just double-click this file to build your app!

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Customer Counter Pro - Simple App Builder         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "This will turn your Python code into a real Mac app!"
echo ""

# Change to project directory
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

echo "📍 Project folder: $PROJECT_DIR"
echo ""

# Check if PyInstaller is installed
echo "🔍 Checking if PyInstaller is installed..."
if ! .venv/bin/python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller (first time only)..."
    .venv/bin/pip install pyinstaller
    echo "✅ PyInstaller installed!"
else
    echo "✅ PyInstaller already installed!"
fi
echo ""

# Clean previous builds
echo "🧹 Cleaning old builds..."
rm -rf build dist *.spec
echo "✅ Cleaned!"
echo ""

# Build the app
echo "🔨 Building your app... (this takes 5-10 minutes)"
echo ""
echo "⏳ Please wait... You'll see lots of text scrolling."
echo "   This is normal! Don't close this window."
echo ""

.venv/bin/python -m PyInstaller \
    --name="Customer Counter Pro" \
    --windowed \
    --onefile \
    --add-data="yolov8n.pt:." \
    --hidden-import=PIL \
    --hidden-import=matplotlib \
    --hidden-import=cv2 \
    --hidden-import=ultralytics \
    --noconfirm \
    counter_modern.py

# Check if build was successful
if [ -d "dist/Customer Counter Pro.app" ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║              ✅ SUCCESS! Your App is Ready!            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📦 Your app is here:"
    echo "   $PROJECT_DIR/dist/Customer Counter Pro.app"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo ""
    echo "1. Test it:"
    echo "   Open the 'dist' folder and double-click your app"
    echo ""
    echo "2. Install it:"
    echo "   Drag it to your Applications folder"
    echo ""
    echo "3. Share it:"
    echo "   Right-click → Compress to create a ZIP file"
    echo ""
    
    # Ask if user wants to open the dist folder
    echo "Would you like to open the 'dist' folder now? (y/n)"
    read -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open dist
        echo "✅ Folder opened!"
    fi
    
    echo ""
    echo "🎉 Congratulations! You've built a real Mac app!"
    echo ""
else
    echo ""
    echo "❌ Build failed! Something went wrong."
    echo ""
    echo "Please check the errors above and try again."
    echo "Or ask for help with the error messages you see."
    echo ""
fi

echo "Press any key to close..."
read -n 1 -s

