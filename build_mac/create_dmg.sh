#!/bin/bash
# Create DMG installer for macOS
# Customer Counter Pro - DMG Creation Script

APP_NAME="Customer Counter Pro"
VERSION="1.0.0"
DMG_NAME="CustomerCounterPro-${VERSION}-macOS"

echo "📦 Creating DMG installer for ${APP_NAME}..."
echo ""

# Check if app exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ App not found! Run ./build_mac.sh first."
    exit 1
fi

# Create temporary directory
TMP_DMG="tmp_dmg"
mkdir -p "${TMP_DMG}"

# Copy app to temp directory
echo "📋 Copying app..."
cp -R "dist/${APP_NAME}.app" "${TMP_DMG}/"

# Create Applications symlink
echo "🔗 Creating Applications symlink..."
ln -s /Applications "${TMP_DMG}/Applications"

# Create DMG
echo "🎨 Creating DMG..."
hdiutil create -volname "${APP_NAME}" \
    -srcfolder "${TMP_DMG}" \
    -ov -format UDZO \
    "${DMG_NAME}.dmg"

# Clean up
echo "🧹 Cleaning up..."
rm -rf "${TMP_DMG}"

if [ -f "${DMG_NAME}.dmg" ]; then
    echo "✅ DMG created successfully!"
    echo ""
    echo "📍 DMG location: ${DMG_NAME}.dmg"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the DMG: open ${DMG_NAME}.dmg"
    echo "2. Sign the DMG (optional): codesign --sign 'Developer ID' ${DMG_NAME}.dmg"
    echo "3. Notarize for distribution (required for macOS 10.15+)"
    echo ""
else
    echo "❌ DMG creation failed!"
    exit 1
fi

