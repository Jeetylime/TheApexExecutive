"""
Setup configuration for The Apex Executive
"""
from setuptools import setup

APP = ['modern_ui.py']
DATA_FILES = [
    ('', ['config.py', 'game_core.py', 'event_system.py', 'companies.py']),
    ('assets', ['assets/app_icon.png', 'assets/README.txt']),
]

OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'darkdetect', 'tkinter'],
    'iconfile': 'assets/app_icon.png',
    'plist': {
        'CFBundleName': 'The Apex Executive',
        'CFBundleDisplayName': 'The Apex Executive',
        'CFBundleIdentifier': 'com.apexexecutive.game',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 The Apex Executive',
        'NSHighResolutionCapable': True,
    },
    'includes': ['tkinter', 'tkinter.messagebox', 'tkinter.simpledialog'],
}

setup(
    name='The Apex Executive',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
