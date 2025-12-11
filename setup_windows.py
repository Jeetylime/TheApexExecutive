"""
Setup configuration for The Apex Executive - Windows Build
Build using PyInstaller for Windows executable
"""
import sys
from pathlib import Path

# This script provides the configuration for PyInstaller
# Run on Windows with: pyinstaller setup_windows.spec

APP_NAME = "TheApexExecutive"
VERSION = "1.0.0"
MAIN_SCRIPT = "modern_ui.py"

# Data files to include
data_files = [
    ('config.py', '.'),
    ('game_core.py', '.'),
    ('event_system.py', '.'),
    ('companies.py', '.'),
    ('assets/app_icon.png', 'assets'),
    ('assets/README.txt', 'assets'),
]

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'tkinter',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'customtkinter',
    'darkdetect',
    'packaging',
]

print(f"Building {APP_NAME} v{VERSION} for Windows")
print("This configuration is for PyInstaller")
print("\nTo build on Windows, run:")
print("  pip install pyinstaller")
print("  pyinstaller setup_windows.spec")
