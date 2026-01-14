#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "   Customer Counter Pro - Modern UI"
echo "=========================================="
echo ""

.venv/bin/python counter_modern.py

read -p "Press Enter to exit..."

