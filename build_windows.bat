@echo off
REM Build script for The Apex Executive - Windows
REM Run this on a Windows machine

echo ========================================
echo  Building The Apex Executive for Windows
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

REM Build executable
echo.
echo Building executable with PyInstaller...
pyinstaller setup_windows.spec

REM Check if build was successful
if exist "dist\TheApexExecutive\TheApexExecutive.exe" (
    echo.
    echo ========================================
    echo  Build Successful!
    echo ========================================
    echo.
    echo Executable location:
    echo   dist\TheApexExecutive\TheApexExecutive.exe
    echo.
    echo To test, run:
    echo   cd dist\TheApexExecutive
    echo   TheApexExecutive.exe
    echo.
) else (
    echo.
    echo ========================================
    echo  Build Failed!
    echo ========================================
    echo Check the output above for errors.
    echo.
)

pause
