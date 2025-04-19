#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FinAsis Oyun Modülleri Derleme ve Dağıtım Scripti
-------------------------------------------------

Bu script, FinAsis oyun modüllerini derleyerek hem masaüstü hem de
mobil platformlar için dağıtılabilir paketler oluşturur.
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from datetime import datetime

# Renkli konsol çıktısı için
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Başlık metni yazdır"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}\n")

def print_status(text):
    """Durum mesajı yazdır"""
    print(f"{Colors.OKBLUE}==> {text}{Colors.ENDC}")

def print_success(text):
    """Başarı mesajı yazdır"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Uyarı mesajı yazdır"""
    print(f"{Colors.WARNING}! {text}{Colors.ENDC}")

def print_error(text):
    """Hata mesajı yazdır"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def check_requirements():
    """Gerekli paketleri kontrol et"""
    print_header("Gerekli paketler kontrol ediliyor...")
    
    requirements = [
        "ursina", "pygame", "PyQt6", "opencv-python", 
        "numpy", "pyinstaller", "Pillow"
    ]
    
    missing_packages = []
    
    for package in requirements:
        try:
            __import__(package.split('-')[0])  # opencv-python için "opencv" şeklinde import et
            print_status(f"{package} paketi mevcut")
        except ImportError:
            missing_packages.append(package)
            print_warning(f"{package} paketi eksik")
    
    if missing_packages:
        print_warning("Eksik paketler bulundu! Yüklemek için:")
        print(f"pip install {' '.join(missing_packages)}")
        while True:
            response = input("Eksik paketleri şimdi yüklemek ister misiniz? (E/H): ").strip().lower()
            if response in ['e', 'evet', 'y', 'yes']:
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
                break
            elif response in ['h', 'hayır', 'n', 'no']:
                print_warning("Eksik paketler yüklenmedi. Derleme başarısız olabilir.")
                break
    else:
        print_success("Tüm gerekli paketler yüklü!")

def create_build_dirs():
    """Derleme dizinlerini oluştur"""
    print_header("Derleme dizinleri hazırlanıyor...")
    
    build_dirs = [
        "build",
        "build/desktop",
        "build/mobile",
        "build/assets",
        "dist"
    ]
    
    for d in build_dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print_status(f"{d} dizini oluşturuldu")
        else:
            print_status(f"{d} dizini zaten mevcut")

def copy_assets():
    """Oyun varlıklarını kopyala"""
    print_header("Oyun varlıkları kopyalanıyor...")
    
    asset_dirs = [
        "apps/games/ursina_game/assets",
        "apps/games/game_app/assets"
    ]
    
    for asset_dir in asset_dirs:
        if os.path.exists(asset_dir):
            dest_dir = "build/assets"
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(asset_dir, dest_dir)
            print_success(f"{asset_dir} dizini başarıyla kopyalandı")
        else:
            print_warning(f"{asset_dir} dizini bulunamadı, varsayılan varlıklar kullanılacak")
            # Varsayılan varlıkları oluştur
            if not os.path.exists("build/assets"):
                os.makedirs("build/assets")
            
            # Basit varsayılan varlıkları oluştur
            with open("build/assets/README.txt", "w", encoding="utf-8") as f:
                f.write("Bu dizin, oyun varlıklarını içerir.\n")
                f.write("Normalde ses dosyaları, görseller ve diğer medya dosyaları burada bulunur.\n")

def build_desktop_apps():
    """Masaüstü uygulamalarını derle"""
    print_header("Masaüstü uygulamaları derleniyor...")
    
    game_files = [
        {
            "script": "apps/games/ursina_game/finans_ogretici.py",
            "name": "FinansOgretici",
            "icon": "build/assets/icon.ico" if os.path.exists("build/assets/icon.ico") else None
        },
        {
            "script": "apps/games/game_app/game.py",
            "name": "TicaretinIzinde",
            "icon": "build/assets/icon.ico" if os.path.exists("build/assets/icon.ico") else None
        },
        {
            "script": "apps/games/game_app/ar_trade_trail.py",
            "name": "TicaretinIzindeAR",
            "icon": "build/assets/icon.ico" if os.path.exists("build/assets/icon.ico") else None
        },
        {
            "script": "apps/games/ursina_game/game.py",
            "name": "PiyasaSimulasyonu",
            "icon": "build/assets/icon.ico" if os.path.exists("build/assets/icon.ico") else None
        }
    ]
    
    for game in game_files:
        print_status(f"{game['name']} derleniyor...")
        
        if not os.path.exists(game["script"]):
            print_warning(f"{game['script']} bulunamadı, bu oyun derlenmeyecek")
            continue
        
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            f"--name={game['name']}",
            "--clean"
        ]
        
        if game["icon"] and os.path.exists(game["icon"]):
            pyinstaller_cmd.append(f"--icon={game['icon']}")
        
        # Ek veri dizinleri ekle
        pyinstaller_cmd.append("--add-data")
        if platform.system() == "Windows":
            pyinstaller_cmd.append(f"build/assets;assets")
        else:
            pyinstaller_cmd.append(f"build/assets:assets")
        
        # Script dosyasını ekle
        pyinstaller_cmd.append(game["script"])
        
        # PyInstaller'ı çalıştır
        try:
            result = subprocess.run(pyinstaller_cmd, check=True)
            if result.returncode == 0:
                print_success(f"{game['name']} başarıyla derlendi!")
            else:
                print_error(f"{game['name']} derlenirken bir hata oluştu!")
        except Exception as e:
            print_error(f"Derleme hatası: {str(e)}")

def build_mobile_apps():
    """Mobil uygulamaları derle"""
    print_header("Mobil uygulamalar derleniyor...")
    
    # Buildozer'ın yüklü olup olmadığını kontrol et
    try:
        subprocess.run(["buildozer", "--version"], check=True, capture_output=True)
    except:
        print_warning("Buildozer bulunamadı! Mobil uygulama derleme atlanacak.")
        print_warning("Buildozer'ı yüklemek için: 'pip install buildozer'")
        return
    
    # Android için buildozer.spec dosyasını oluştur
    buildozer_spec = """
[app]
title = FinAsis Oyunlar
package.name = finasisgames
package.domain = tr.com.finasis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,ursina,pygame,kivy,numpy,opencv-python,pillow
orientation = landscape
fullscreen = 0
android.permissions = CAMERA
android.api = 30
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
p4a.bootstrap = sdl2
"""
    
    # Buildozer spec dosyasını oluştur
    mobile_build_dir = "build/mobile"
    with open(f"{mobile_build_dir}/buildozer.spec", "w") as f:
        f.write(buildozer_spec)
    
    # Oyun dosyalarını kopyala
    shutil.copy("apps/games/game_app/game.py", f"{mobile_build_dir}/main.py")
    
    # assets dizinini kopyala
    if os.path.exists("build/assets"):
        shutil.copytree("build/assets", f"{mobile_build_dir}/assets")
    
    # Buildozer'ı çalıştır
    print_status("Android APK oluşturuluyor (bu işlem biraz zaman alabilir)...")
    try:
        os.chdir(mobile_build_dir)
        subprocess.run(["buildozer", "android", "debug"], check=True)
        print_success("Android APK başarıyla oluşturuldu!")
        # APK'yı ana dist klasörüne taşı
        if os.path.exists("bin"):
            for file in os.listdir("bin"):
                if file.endswith(".apk"):
                    shutil.copy(f"bin/{file}", f"../../dist/{file}")
                    print_success(f"{file} dosyası dist/ dizinine kopyalandı")
        os.chdir("../..")
    except Exception as e:
        print_error(f"Android derleme hatası: {str(e)}")
        os.chdir("../..")

def create_zip_package():
    """Tüm derlenmiş dosyaları zip haline getir"""
    print_header("Zip paketi oluşturuluyor...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"FinAsis_Oyunlar_{timestamp}.zip"
    
    if os.path.exists("dist"):
        shutil.make_archive(f"dist/FinAsis_Oyunlar_{timestamp}", 'zip', "dist")
        print_success(f"{zip_filename} oluşturuldu!")
    else:
        print_warning("dist/ dizini bulunamadı, zip paketi oluşturulamadı")

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='FinAsis Oyun Derleme Aracı')
    parser.add_argument('--desktop-only', action='store_true', help='Sadece masaüstü uygulamaları derle')
    parser.add_argument('--mobile-only', action='store_true', help='Sadece mobil uygulamaları derle')
    parser.add_argument('--skip-zip', action='store_true', help='Zip paketi oluşturmayı atla')
    
    args = parser.parse_args()
    
    print_header("FinAsis Oyun Derleme Aracı")
    print(f"Derleme başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Gereksinimleri kontrol et
    check_requirements()
    
    # Dizinleri oluştur
    create_build_dirs()
    
    # Varlıkları kopyala
    copy_assets()
    
    # Masaüstü uygulamaları derle
    if not args.mobile_only:
        build_desktop_apps()
    
    # Mobil uygulamaları derle
    if not args.desktop_only:
        build_mobile_apps()
    
    # Zip paketi oluştur
    if not args.skip_zip:
        create_zip_package()
    
    print_header("Derleme tamamlandı!")
    print(f"Tamamlanma zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Derlenen dosyalar 'dist/' dizininde bulunabilir.")

if __name__ == "__main__":
    main() 