# 🎮 Building The Apex Executive DMG for macOS

## Quick Start

Run this single command to build the DMG:

```bash
./build_dmg.sh
```

This will create `TheApexExecutive-v1.0.0.dmg` ready for distribution!

---

## Manual Build Steps

If you prefer to build manually:

### 1. Install py2app
```bash
.venv/bin/pip install py2app
```

### 2. Build the .app bundle
```bash
.venv/bin/python setup.py py2app
```

### 3. Create the DMG
```bash
hdiutil create -volname "The Apex Executive Installer" \
  -srcfolder "dist/The Apex Executive.app" \
  -ov -format UDZO TheApexExecutive-v1.0.0.dmg
```

---

## What Gets Packaged

✅ All game files (modern_ui.py, game_core.py, event_system.py, config.py, companies.py)
✅ Assets folder (app icon, etc.)
✅ All Python dependencies (customtkinter, darkdetect)
✅ Python interpreter (no Python installation needed by users!)

---

## Distribution

The final DMG file:
- **Name**: `TheApexExecutive-v1.0.0.dmg`
- **Location**: Project root directory
- **Size**: ~50-80 MB (includes Python + all dependencies)
- **Compatible**: macOS 10.13+ (High Sierra and newer)

Users simply:
1. Download the DMG
2. Open it
3. Drag "The Apex Executive.app" to Applications folder
4. Launch and play!

---

## Testing the Build

After building:

1. Open `TheApexExecutive-v1.0.0.dmg`
2. Drag the app to Applications
3. Launch from Applications folder
4. Verify all features work:
   - Hotkeys (1-9, Space, L)
   - Save/Load games
   - All CEO actions
   - Leaderboard
   - Events system

---

## Troubleshooting

### If the app won't open (security warning):
```bash
xattr -cr "dist/The Apex Executive.app"
```

### To clean and rebuild:
```bash
rm -rf build dist *.dmg
./build_dmg.sh
```

### Check what's included:
```bash
ls -la "dist/The Apex Executive.app/Contents/Resources/"
```

---

## File Sizes (Approximate)

- `.app bundle`: 60-90 MB
- `.dmg file`: 50-80 MB (compressed)

The size includes:
- Python 3.x runtime
- customtkinter framework
- All game assets
- Your game code

No Python installation required on user's machine! 🎉
