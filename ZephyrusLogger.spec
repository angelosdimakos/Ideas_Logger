# ZephyrusLogger.spec
# Replaces your broken one with a clean structure

# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

import pathlib
project_root = str(pathlib.Path(".").resolve())


block_cipher = None

a = Analysis(
    ['scripts/main.py'],             # entry script
    pathex=[project_root],           # treat 'zip/' as the root
    binaries=[],
    datas=[
        ('config/*.json', 'config'),             # include config files
        ('logs/*.json', 'logs'),                 # include logs
        ('logs/*.txt', 'logs'),
        ('exports/*.md', 'exports'),             # markdown exports
        ('vector_store/*', 'vector_store'),      # vector store assets
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZephyrusLogger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True  # Set to False for GUI mode only
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZephyrusLogger'
)
