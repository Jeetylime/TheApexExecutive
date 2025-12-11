#!/bin/bash
# Build script for The Apex Executive DMG

set -e  # Exit on error

echo "🏗️  Building The Apex Executive for macOS..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Install py2app if needed
echo "📦 Installing py2app..."
.venv/bin/pip install py2app

# Build the app
echo "🔨 Building .app bundle..."
.venv/bin/python setup.py py2app

# Create DMG
echo "💾 Creating DMG installer..."
DMG_NAME="TheApexExecutive-v1.0.0.dmg"
APP_NAME="The Apex Executive.app"
VOLUME_NAME="The Apex Executive Installer"

# Remove old DMG if exists
rm -f "$DMG_NAME"

# Create temporary DMG
hdiutil create -volname "$VOLUME_NAME" -srcfolder "dist/$APP_NAME" -ov -format UDZO "$DMG_NAME"

echo "✅ DMG created successfully: $DMG_NAME"
echo ""
echo "📍 Location: $(pwd)/$DMG_NAME"
echo "📦 App size: $(du -sh "dist/$APP_NAME" | cut -f1)"
echo "💿 DMG size: $(du -sh "$DMG_NAME" | cut -f1)"
echo ""
echo "🎮 To test: Open $DMG_NAME and drag the app to Applications"
