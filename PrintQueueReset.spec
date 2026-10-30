# -*- mode: python ; coding: utf-8 -*-
"""Standalone Print Queue Reset (one-file, no Python install).

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=[("assets", "assets"), ("LICENSE", ".")],
    hiddenimports=["app", "spooler", "i18n"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["numpy", "PIL", "pip", "setuptools"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PrintQueueReset",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets\\icon.ico",
    uac_admin=False,
    version="file_version_info.txt",
)
