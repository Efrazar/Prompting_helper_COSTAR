# -*- mode: python ; coding: utf-8 -*-
# macOS build spec
# Requires: icon.icns (convert icon.png using iconutil or an online converter)

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/models', 'models'),
        ('src/utils', 'utils'),
        ('src/ui', 'ui'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sqlalchemy.ext.baked',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PromptingHelper',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.icns',  # Must be .icns format for macOS
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PromptingHelper',
)

app = BUNDLE(
    coll,
    name='PromptingHelper.app',
    icon='icon.icns',
    bundle_identifier='com.efrainzarazuaarvizu.promptinghelper',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'Prompting Helper',
        'CFBundleDisplayName': 'Prompting Helper',
    },
)
