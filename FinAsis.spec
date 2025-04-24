# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[('manage.py', '.'), ('config', 'config'), ('core', 'core'), ('static', 'static'), ('templates', 'templates'), ('db.sqlite3', '.')],
    hiddenimports=['django', 'django.core', 'django.contrib', 'django.conf', 'django.template', 'django.template.loader', 'django.template.context_processors', 'django.template.loaders', 'django.template.loaders.filesystem', 'django.template.loaders.app_directories', 'django.middleware', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FinAsis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
