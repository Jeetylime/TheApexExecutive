# 🎮 Building The Apex Executive for Windows

## Prerequisites

You'll need to build this on a **Windows machine** or use a Windows VM/cloud service.

### Required Software:
- Python 3.8+ for Windows
- Git (optional, for cloning the project)

---

## Method 1: Build on Windows (Recommended)

### 1. Set up Python environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```cmd
pip install -r requirements.txt
pip install pyinstaller
```

### 3. Build the executable

```cmd
pyinstaller setup_windows.spec
```

This creates:
- `dist/TheApexExecutive/TheApexExecutive.exe` - Main executable
- `dist/TheApexExecutive/` - Folder with all dependencies

### 4. Test the build

```cmd
cd dist\TheApexExecutive
TheApexExecutive.exe
```

### 5. Create installer (Optional)

Use **Inno Setup** to create a professional installer:

1. Download [Inno Setup](https://jrsoftware.org/isdl.php)
2. Create an installer script (see below)
3. Compile to create `TheApexExecutive-Setup.exe`

---

## Method 2: Use GitHub Actions (Easiest from macOS) ⭐

**This is the recommended method if you're on macOS!** GitHub will build your Windows executable for you in the cloud - completely free.

### Why GitHub Actions?
- ✅ No Windows machine needed
- ✅ Completely free for public repos
- ✅ Automatic builds on every code update
- ✅ Professional CI/CD pipeline
- ✅ Can build for Windows, macOS, and Linux simultaneously

### Step-by-Step Guide

#### Step 1: Set Up GitHub Desktop

**If you don't have GitHub Desktop:**

1. Download from https://desktop.github.com
2. Install and open GitHub Desktop
3. Sign in with your GitHub account (or create one)

#### Step 2: Create a GitHub Repository

**Using GitHub Desktop:**

1. In GitHub Desktop, go to **File** → **Add Local Repository**
2. Click **"Choose..."** and select your project folder:
   `/Users/jettflynn/Desktop/ /TheApexExecutive`
3. Click **"create a repository"** link (since it's not a git repo yet)
4. Fill in:
   - **Name:** TheApexExecutive
   - **Description:** (optional) CEO business management game
   - **Local Path:** (already set)
   - ✅ Check **"Initialize this repository with a README"** if you want
5. Click **"Create Repository"**
6. Click **"Publish repository"** button at the top
7. Choose **Public** (unlimited free Actions) or **Private** (limited free minutes)
8. Uncheck **"Keep this code private"** if making it public
9. Click **"Publish Repository"**

#### Step 3: Commit and Push Your Code

**Using GitHub Desktop:**

1. You should see all your files listed in the left sidebar
2. In the bottom-left corner:
   - **Summary:** Type "Initial commit - Windows build files"
   - **Description:** (optional) Added PyInstaller config and GitHub Actions workflow
3. Click the blue **"Commit to main"** button
4. Click **"Push origin"** button at the top (or **"Publish branch"** if first time)

Your code is now on GitHub! 🎉

#### Step 4: Verify the Workflow File

The workflow file is already created at: `.github/workflows/build-windows.yml`

You can verify it exists:
```bash
ls -la .github/workflows/
```

This file tells GitHub Actions how to build your Windows executable.

#### Step 5: Trigger the Build

The build automatically starts when you push code. You can also trigger it manually:

1. Go to your GitHub repository (click **"View on GitHub"** in GitHub Desktop)
2. Click the **"Actions"** tab at the top
3. Click **"Build Windows Executable"** in the left sidebar
4. Click **"Run workflow"** button on the right
5. Click the green **"Run workflow"** button

#### Step 6: Monitor the Build

1. You'll see a workflow run appear (yellow dot = building)
2. Click on it to see real-time progress
3. Watch each step execute:
   - Checkout code ✓
   - Set up Python ✓
   - Install dependencies ✓
   - Build executable ✓
   - Create zip archive ✓
   - Upload artifact ✓
4. Takes about 3-5 minutes total

#### Step 7: Download Your Windows Executable

Once the build completes (green checkmark ✓):

1. Scroll down to the **"Artifacts"** section at the bottom
2. Click **"TheApexExecutive-Windows"** to download
3. You'll get a ZIP file containing your Windows build

The ZIP contains:
```
TheApexExecutive-Windows-x64.zip
  └── TheApexExecutive/
      ├── TheApexExecutive.exe  ← Your Windows executable!
      ├── All Python libraries
      └── All game files
```

#### Step 8: Test on Windows

1. Extract the ZIP on a Windows computer
2. Navigate to the `TheApexExecutive` folder
3. Double-click `TheApexExecutive.exe`
4. The game should launch!

### Understanding the Workflow File

Here's what each part does:

```yaml
on:
  push:              # Build when you push code
  workflow_dispatch: # Allow manual trigger
```

```yaml
runs-on: windows-latest  # Use GitHub's Windows server
```

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Install Python 3.11
```

```yaml
- name: Build executable
  run: pyinstaller setup_windows.spec  # Build using PyInstaller
```

### Automatic Builds on Updates

**Using GitHub Desktop:**

1. Make changes to your code in VS Code
2. Open GitHub Desktop - it will show your changes
3. Write a commit message (e.g., "Fixed bug in CEO actions")
4. Click **"Commit to main"**
5. Click **"Push origin"**

GitHub Actions will automatically:
1. Build a new Windows executable
2. Make it available for download
3. Email you if the build fails

### Creating Releases (Optional)

To create official releases with version tags:

**Using GitHub Desktop:**

1. Go to **Repository** → **Create Tag...**
2. Tag name: `v1.0.0`
3. Description: "Version 1.0.0 release"
4. Click **"Create Tag"**
5. Push the tag: **Repository** → **Push**

Or create directly on GitHub:

1. Go to your repository on GitHub
2. Click **"Releases"** on the right side
3. Click **"Create a new release"**
4. Tag: `v1.0.0`, Title: "Version 1.0.0"
5. Click **"Publish release"**

This creates a release with the Windows executable automatically attached!

### Troubleshooting GitHub Actions

**Build fails?**
- Click on the failed step to see error details
- Check that all files are committed and pushed
- Verify `requirements.txt` includes all dependencies

**Can't find the artifact?**
- Make sure the build succeeded (green checkmark)
- Artifacts are at the bottom of the workflow run page
- They expire after 30 days (configurable)

**Need more build minutes?**
- Public repos: Unlimited free minutes
- Private repos: 2,000 free minutes/month
- Check usage: Settings → Billing

### Advanced: Building for Multiple Platforms

You can modify the workflow to build for Windows, macOS, and Linux simultaneously:

```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
```

This creates executables for all three platforms in one go!

### Alternative: Cloud Build Services

If you can't use GitHub Actions, other options:
- **AppVeyor** (free for open source)
- **AWS EC2 Windows instance** (pay per hour)
- **Azure Pipelines** (free tier available)

---

## Creating a Professional Installer with Inno Setup

### 1. Install Inno Setup on Windows

Download from: https://jrsoftware.org/isdl.php

### 2. Create installer script (`installer.iss`)

```iss
[Setup]
AppName=The Apex Executive
AppVersion=1.0.0
DefaultDirName={autopf}\TheApexExecutive
DefaultGroupName=The Apex Executive
OutputBaseFilename=TheApexExecutive-Setup-v1.0.0
Compression=lzma2
SolidCompression=yes
OutputDir=installer_output
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\TheApexExecutive\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\The Apex Executive"; Filename: "{app}\TheApexExecutive.exe"
Name: "{autodesktop}\The Apex Executive"; Filename: "{app}\TheApexExecutive.exe"

[Run]
Filename: "{app}\TheApexExecutive.exe"; Description: "Launch The Apex Executive"; Flags: postinstall nowait skipifsilent
```

### 3. Compile the installer

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

This creates: `installer_output/TheApexExecutive-Setup-v1.0.0.exe`

---

## What Gets Packaged

✅ All game files (modern_ui.py, game_core.py, event_system.py, config.py, companies.py)
✅ Assets folder (app icon, etc.)
✅ All Python dependencies (customtkinter, darkdetect)
✅ Python runtime (no Python installation needed by users!)

---

## Distribution File Sizes

- **Executable folder**: ~50-80 MB
- **Installer (.exe)**: ~40-60 MB (compressed)

---

## Quick Build Script (Windows)

Create `build_windows.bat`:

```batch
@echo off
echo Building The Apex Executive for Windows...

REM Activate virtual environment
call venv\Scripts\activate

REM Install/update dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous builds
rmdir /s /q build dist

REM Build executable
pyinstaller setup_windows.spec

echo.
echo Build complete! Check dist\TheApexExecutive\
echo.
pause
```

Run with: `build_windows.bat`

---

## Testing Checklist

After building, test:
- ✅ App launches without errors
- ✅ All hotkeys work (1-9, Space, L)
- ✅ Save/Load functionality
- ✅ CEO actions execute properly
- ✅ Leaderboard displays
- ✅ Events system triggers
- ✅ Theme switching works

---

## Troubleshooting

### Missing DLL errors
- Ensure all dependencies are in requirements.txt
- Add missing modules to `hiddenimports` in setup_windows.spec

### Large file size
- Remove debug symbols: `upx=True` (already enabled)
- Use `--exclude-module` for unused packages

### Antivirus false positives
- Code sign the executable (requires certificate)
- Submit to antivirus vendors for whitelisting

### App icon not showing
- Convert PNG to ICO format first
- Use online converter or: `pip install pillow`

---

## 🎯 Quick Reference: GitHub Desktop Workflow

### One-Time Setup:
1. Download and install GitHub Desktop
2. **File** → **Add Local Repository** → Select your project folder
3. Click **"create a repository"** link
4. Click **"Publish repository"** → Choose Public/Private

### After Making Code Changes:
1. Open GitHub Desktop (it automatically detects changes)
2. Review changes in left sidebar
3. Enter commit message at bottom-left
4. Click **"Commit to main"**
5. Click **"Push origin"**
6. GitHub Actions builds your Windows .exe automatically!

### Download Built Executable:
1. Click **"View on GitHub"** in GitHub Desktop
2. Go to **Actions** tab
3. Click latest workflow run
4. Scroll to **Artifacts** → Download **TheApexExecutive-Windows**

### Create a Release:
1. **Repository** → **Create Tag...** → `v1.0.0`
2. Push the tag
3. Or create release directly on GitHub website

**No Windows machine required!** ✨

---

## Need Help?

- PyInstaller docs: https://pyinstaller.org/
- Inno Setup docs: https://jrsoftware.org/ishelp/
- GitHub Actions: https://docs.github.com/actions
