#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bu betik FinAsis oyunlarını masaüstü (.exe) veya mobil (.apk) platformlar için derler.
"""

import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path

# Proje dizinini belirle
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.absolute()
URSINA_GAME_DIR = PROJECT_ROOT / "apps" / "games" / "ursina_game"
DIST_DIR = PROJECT_ROOT / "dist"

# Masaüstü yapılandırması
DESKTOP_SPEC = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [os.path.join(SPECPATH, '{main_script}')],
    pathex=['{ursina_game_dir}', '{project_root}'],
    binaries=[],
    datas=[
        ('{ursina_game_dir}/assets', 'assets'),
        ('{ursina_game_dir}/models', 'models'),
        ('{ursina_game_dir}/textures', 'textures'),
        ('{ursina_game_dir}/sounds', 'sounds'),
    ],
    hiddenimports=['ursina', 'ursina.prefabs', 'ursina.models', 'ursina.textures'],
    hookspath=[],
    hooksconfig={{}},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{game_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console},
    icon='{icon_path}',
)
"""

# Mobil buildozer.spec şablonu
BUILDOZER_SPEC = """
[app]
title = {game_name}
package.name = finasis.{package_name}
package.domain = com.finasis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,wav,mp3,glb,obj,mtl
source.include_patterns = assets/*,models/*,textures/*,sounds/*
version = 1.0.0
requirements = python3,kivy,ursina,setuptools,pillow,numpy
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.minapi = 27
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a
p4a.source_dir = .
p4a.bootstrap = sdl2
icon.filename = {icon_path}

[buildozer]
log_level = 2
"""

# Oyunlar listesi
GAMES = {
    "ticaretin_izinde_3d": {
        "display_name": "Ticaretin İzinde 3D",
        "main_script": "main.py",
        "icon": "assets/icons/game_icon.ico",
        "package_name": "ticaretin_izinde_3d",
        "console": False
    }
}

def build_desktop(game_key):
    """Masaüstü versiyonunu PyInstaller ile derler"""
    game = GAMES.get(game_key)
    if not game:
        print(f"Hata: '{game_key}' oyunu bulunamadı.")
        return False
    
    print(f"[INFO] '{game['display_name']}' masaüstü (.exe) sürümü derleniyor...")
    
    # PyInstaller spec dosyası oluştur
    spec_content = DESKTOP_SPEC.format(
        main_script=game['main_script'],
        ursina_game_dir=str(URSINA_GAME_DIR).replace('\\', '/'),
        project_root=str(PROJECT_ROOT).replace('\\', '/'),
        game_name=game['display_name'],
        console=str(game['console']),
        icon_path=str(URSINA_GAME_DIR / game['icon']).replace('\\', '/')
    )
    
    spec_file = URSINA_GAME_DIR / f"{game_key}.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # PyInstaller ile derle
    os.chdir(URSINA_GAME_DIR)
    result = subprocess.run([
        'pyinstaller', 
        '--clean',
        '--distpath', str(DIST_DIR / 'desktop'),
        '--workpath', str(DIST_DIR / 'build'),
        str(spec_file)
    ], capture_output=True)
    
    if result.returncode == 0:
        print(f"[SUCCESS] '{game['display_name']}' başarıyla derlendi! Dosya konumu: {DIST_DIR / 'desktop' / game['display_name']}.exe")
        return True
    else:
        print(f"[ERROR] Derleme hatası: {result.stderr.decode('utf-8', errors='ignore')}")
        return False

def build_mobile(game_key):
    """Mobil versiyonunu Buildozer ile derler"""
    game = GAMES.get(game_key)
    if not game:
        print(f"Hata: '{game_key}' oyunu bulunamadı.")
        return False
    
    print(f"[INFO] '{game['display_name']}' mobil (.apk) sürümü derleniyor...")
    
    # Buildozer dizini oluştur
    mobile_build_dir = DIST_DIR / 'mobile' / game_key
    os.makedirs(mobile_build_dir, exist_ok=True)
    
    # Gerekli dosyaları kopyala
    shutil.copytree(URSINA_GAME_DIR / 'assets', mobile_build_dir / 'assets', dirs_exist_ok=True)
    shutil.copytree(URSINA_GAME_DIR / 'models', mobile_build_dir / 'models', dirs_exist_ok=True)
    shutil.copytree(URSINA_GAME_DIR / 'textures', mobile_build_dir / 'textures', dirs_exist_ok=True)
    shutil.copytree(URSINA_GAME_DIR / 'sounds', mobile_build_dir / 'sounds', dirs_exist_ok=True)
    
    # Python dosyalarını kopyala
    for py_file in URSINA_GAME_DIR.glob('*.py'):
        shutil.copy2(py_file, mobile_build_dir)
    
    # Buildozer.spec oluştur
    buildozer_spec = BUILDOZER_SPEC.format(
        game_name=game['display_name'],
        package_name=game['package_name'],
        icon_path=f"assets/icons/game_icon.png"
    )
    
    with open(mobile_build_dir / 'buildozer.spec', 'w', encoding='utf-8') as f:
        f.write(buildozer_spec)
    
    # Buildozer ile derle
    os.chdir(mobile_build_dir)
    result = subprocess.run(['buildozer', 'android', 'debug'], capture_output=True)
    
    if result.returncode == 0:
        print(f"[SUCCESS] '{game['display_name']}' başarıyla derlendi! APK konumu: {mobile_build_dir}/bin/")
        # APK'yı ana dist klasörüne kopyala
        for apk in (mobile_build_dir / 'bin').glob('*.apk'):
            dest_path = DIST_DIR / 'mobile' / f"{game['display_name']}.apk" 
            shutil.copy2(apk, dest_path)
            print(f"[INFO] APK kopyalandı: {dest_path}")
        return True
    else:
        print(f"[ERROR] Derleme hatası: {result.stderr.decode('utf-8', errors='ignore')}")
        return False

def main():
    parser = argparse.ArgumentParser(description='FinAsis oyunlarını derleyin.')
    parser.add_argument('--game', choices=list(GAMES.keys()), default='ticaretin_izinde_3d',
                        help='Derlenecek oyun (varsayılan: ticaretin_izinde_3d)')
    parser.add_argument('--desktop-only', action='store_true', help='Sadece masaüstü (.exe) sürümünü derle')
    parser.add_argument('--mobile-only', action='store_true', help='Sadece mobil (.apk) sürümünü derle')
    
    args = parser.parse_args()
    game_key = args.game
    
    # Dist dizinlerini oluştur
    os.makedirs(DIST_DIR / 'desktop', exist_ok=True)
    os.makedirs(DIST_DIR / 'mobile', exist_ok=True)
    os.makedirs(DIST_DIR / 'build', exist_ok=True)
    
    if args.desktop_only:
        build_desktop(game_key)
    elif args.mobile_only:
        build_mobile(game_key)
    else:
        # Hem masaüstü hem de mobil platformlar için derle
        desktop_success = build_desktop(game_key)
        mobile_success = build_mobile(game_key)
        
        if desktop_success and mobile_success:
            print(f"[SUCCESS] '{GAMES[game_key]['display_name']}' tüm platformlar için başarıyla derlendi!")
        else:
            print(f"[WARN] Bazı derleme işlemleri başarısız oldu.")

if __name__ == "__main__":
    main() 