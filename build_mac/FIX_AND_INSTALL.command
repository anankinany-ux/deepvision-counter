#!/bin/bash
# Professional App Installer - Fixes all macOS security issues

clear
echo "==========================================================="
echo "  DeepVision Counter - Professional Installer"
echo "==========================================================="
echo ""

cd "$(dirname "$0")"

APP_PATH="../dist/DeepVision Counter.app"
INSTALL_PATH="/Applications/DeepVision Counter.app"

# Step 1: Verify app exists
if [ ! -d "$APP_PATH" ]; then
    echo "[X] ERROR: App not found at: $APP_PATH"
    echo "Please run the build script first!"
    exit 1
fi

echo "[OK] App found"
echo ""

# Step 2: Remove all macOS quarantine attributes
echo "[>] Removing macOS security blocks..."
xattr -cr "$APP_PATH"
echo "[OK] Security attributes cleared"
echo ""

# Step 3: Remove old installation
if [ -d "$INSTALL_PATH" ]; then
    echo "[>] Removing old installation..."
    rm -rf "$INSTALL_PATH"
    echo "[OK] Old version removed"
    echo ""
fi

# Step 4: Copy to Applications
echo "[>] Installing to Applications folder..."
cp -R "$APP_PATH" "$INSTALL_PATH"
echo "[OK] Installed successfully"
echo ""

# Step 5: Clear attributes again
echo "[>] Final security cleanup..."
xattr -cr "$INSTALL_PATH"
echo "[OK] Ready to use"
echo ""

# Step 6: Test launch
echo "[>] Testing app launch..."
open "$INSTALL_PATH"

echo ""
echo "==========================================================="
echo "  [OK] INSTALLATION COMPLETE!"
echo "==========================================================="
echo ""
echo "The app is opening now..."
echo ""
echo "TO OPEN IN FUTURE:"
echo "  * Press Command+Space"
echo "  * Type: DeepVision"
echo "  * Press Enter"
echo ""
echo "Or find it in your Applications folder"
echo ""
echo "==========================================================="
echo ""

# Keep terminal open
echo "Press any key to close this window..."
read -n 1

