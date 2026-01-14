#!/bin/bash
# Build script for macOS standalone app
# Customer Counter Pro - Mac Build Script

echo "🚀 Building Customer Counter Pro for macOS..."
echo ""

# Check if pyinstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Create the standalone app
echo "🔨 Creating standalone app..."
pyinstaller --name="Customer Counter Pro" \
    --windowed \
    --onefile \
    --icon=assets/icon.icns \
    --add-data="yolov8n.pt:." \
    --add-data="config:config" \
    --hidden-import=PIL \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=matplotlib \
    --hidden-import=cv2 \
    --hidden-import=ultralytics \
    --hidden-import=lap \
    --noconfirm \
    counter_modern.py

# Check if build was successful
if [ -d "dist/Customer Counter Pro.app" ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📍 App location: dist/Customer Counter Pro.app"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the app: open 'dist/Customer Counter Pro.app'"
    echo "2. Create DMG installer: ./create_dmg.sh"
    echo "3. Sign the app (optional): codesign --deep --force --verify --verbose --sign 'Developer ID' 'dist/Customer Counter Pro.app'"
    echo ""
else
    echo "❌ Build failed! Check errors above."
    exit 1
fi

