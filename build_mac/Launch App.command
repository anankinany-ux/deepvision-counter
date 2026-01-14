#!/bin/bash
cd "$(dirname "$0")"

echo "Starting DeepVision Counter..."
echo ""

# Kill any existing instances
pkill -9 -f "DeepVision Counter" 2>/dev/null

# Wait a moment
sleep 1

# Launch the app with error capture
"../dist/DeepVision Counter.app/Contents/MacOS/DeepVision Counter" 2>&1

echo ""
echo "App closed or crashed."
echo "Press any key to close this window..."
read -n 1

