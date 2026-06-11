# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get site-packages folder path dynamically
site_packages = next(p for p in sys.path if 'site-packages' in p)

datas = [
    # Streamlit static files and assets
    (os.path.join(site_packages, 'streamlit', 'static'), 'streamlit/static'),
    # Streamlit runtime
    (os.path.join(site_packages, 'streamlit', 'runtime'), 'streamlit/runtime'),
    # Our app.py and downloader.py scripts
    ('app.py', '.'),
    ('downloader.py', '.'),
]

# Collect static-ffmpeg binaries
datas += collect_data_files('static_ffmpeg')

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'yt_dlp',
        'static_ffmpeg',
    ] + collect_submodules('streamlit'),
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StreamYTDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StreamYTDownloader',
)
