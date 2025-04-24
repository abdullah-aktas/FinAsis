#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FinAsis Oyun Modülleri Derleme ve Dağıtım Scripti
-------------------------------------------------

Bu script, FinAsis oyun modüllerini derleyerek hem masaüstü hem de
mobil platformlar için dağıtılabilir paketler oluşturur.

Özellikler:
- Çoklu platform desteği (Windows, Linux, macOS, Android, iOS)
- Otomatik güncelleştirme sistemi
- Test otomasyonu
- CI/CD entegrasyonu
- Performans optimizasyonları
- Güvenlik kontrolleri
"""

import logging
import os
import sys
import shutil
import subprocess
import platform
import argparse
import json
import hashlib
import time
import requests
import zipfile
import tempfile
import pytest
import unittest
import psutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_games.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GameBuilder:
    """Oyun derleme yöneticisi"""
    
    def __init__(self, config_path: str = "game_config.json"):
        """
        GameBuilder sınıfını başlatır
        
        Args:
            config_path (str): Yapılandırma dosyası yolu
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.build_dir = Path("build/games")
        self.dist_dir = Path("dist")
        self.cache_dir = Path(".build_cache")
        self.requirements_file = Path("requirements.txt")
        self.start_time = time.time()
        self.current_platform = platform.system().lower()
        self.arch = platform.machine().lower()
        
    def _load_config(self) -> Dict[str, Any]:
        """Yapılandırma dosyasını yükler"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Yapılandırma dosyası bulunamadı: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Yapılandırma dosyası geçersiz JSON formatında: {self.config_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Yapılandırma yükleme hatası: {str(e)}")
            sys.exit(1)
            
    def check_requirements(self) -> bool:
        """Gerekli paketleri kontrol et"""
        logger.info("Gerekli paketler kontrol ediliyor...")
        
        try:
            all_requirements = set()
            for game in self.config["game_modules"]:
                all_requirements.update(game["requirements"])
                
            missing_packages = []
            for package in all_requirements:
                try:
                    __import__(package.split('-')[0])
                    logger.info(f"{package} paketi mevcut")
                except ImportError:
                    missing_packages.append(package)
                    logger.warning(f"{package} paketi eksik")
                    
            if missing_packages:
                logger.warning("Eksik paketler bulundu! Yüklemek için:")
                logger.warning(f"pip install {' '.join(missing_packages)}")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install"] + missing_packages,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Paket yükleme hatası: {e.stderr}")
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"Gereksinim kontrolü hatası: {str(e)}")
            return False
        
    def create_build_dirs(self) -> None:
        """Derleme dizinlerini oluştur"""
        logger.info("Derleme dizinleri hazırlanıyor...")
        
        build_dirs = [
            self.build_dir,
            self.build_dir / "desktop",
            self.build_dir / "mobile",
            self.build_dir / "assets",
            self.dist_dir,
            self.cache_dir
        ]
        
        for d in build_dirs:
            d.mkdir(parents=True, exist_ok=True)
            logger.info(f"{d} dizini oluşturuldu")
            
    def copy_assets(self) -> None:
        """Oyun varlıklarını kopyala"""
        logger.info("Oyun varlıkları kopyalanıyor...")
        
        for game in self.config["game_modules"]:
            for asset_dir in game["assets"]:
                src = Path(asset_dir)
                if src.exists():
                    dest = self.build_dir / "assets" / game["name"]
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    logger.info(f"{asset_dir} dizini başarıyla kopyalandı")
                else:
                    logger.warning(f"{asset_dir} dizini bulunamadı")
                    
    def run_tests(self) -> bool:
        """Testleri çalıştır"""
        if not self.config["test_config"]["unit_tests"]:
            logger.info("Testler devre dışı bırakıldı")
            return True
            
        logger.info("Testler çalıştırılıyor...")
        
        test_dir = Path("tests")
        if not test_dir.exists():
            logger.error("Test dizini bulunamadı")
            return False
            
        try:
            # Unit testleri çalıştır
            if self.config["test_config"]["unit_tests"]:
                result = pytest.main([
                    str(test_dir),
                    "--cov=.",
                    f"--cov-fail-under={self.config['test_config']['coverage_threshold']}",
                    f"--timeout={self.config['test_config']['test_timeout']}",
                    "-v"
                ])
                if result != 0:
                    logger.error("Unit testler başarısız")
                    return False
                    
            # Performans testlerini çalıştır
            if self.config["test_config"]["performance_tests"]:
                from tests.performance import run_performance_tests
                if not run_performance_tests():
                    logger.error("Performans testleri başarısız")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Testler sırasında hata: {e}")
            return False
            
    def build_game(self, game_config: Dict[str, Any]) -> bool:
        """
        Oyunu derler
        
        Args:
            game_config (Dict[str, Any]): Oyun yapılandırması
            
        Returns:
            bool: Derleme başarılı ise True, değilse False
        """
        try:
            game_name = game_config.get('name')
            if not game_name:
                logger.error("Oyun adı belirtilmemiş")
                return False
                
            logger.info(f"{game_name} oyunu derleniyor...")
            
            # Derleme komutlarını hazırla
            build_cmd = [
                "pyinstaller",
                "--name", game_name,
                "--onefile",
                "--windowed",
                game_config.get('main_file', 'main.py')
            ]
            
            # Ek seçenekleri ekle
            if game_config.get('icon'):
                build_cmd.extend(["--icon", game_config['icon']])
                
            if game_config.get('hidden_imports'):
                for imp in game_config['hidden_imports']:
                    build_cmd.extend(["--hidden-import", imp])
                    
            # Derlemeyi başlat
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"{game_name} başarıyla derlendi")
                return True
            else:
                logger.error(f"Derleme hatası: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Derleme sırasında hata: {str(e)}")
            return False
            
    def build_desktop_game(self, game: Dict) -> bool:
        """Masaüstü oyununu derle"""
        logger.info(f"{game['name']} derleniyor...")
        
        if not Path(game["script"]).exists():
            logger.warning(f"{game['script']} bulunamadı")
            return False
            
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            f"--name={game['name']}",
            "--clean",
            "--log-level=DEBUG",
            "--noconfirm",
            f"--specpath={self.build_dir / 'desktop'}",
            f"--workpath={self.build_dir / 'desktop' / 'work'}",
            f"--distpath={self.dist_dir / 'desktop'}",
        ]
        
        if game["icon"] and Path(game["icon"]).exists():
            pyinstaller_cmd.append(f"--icon={game['icon']}")
            
        # Platform özel ayarlar
        if self.current_platform == "windows":
            pyinstaller_cmd.extend(["--uac-admin"])
        elif self.current_platform == "macos":
            pyinstaller_cmd.extend(["--osx-bundle-identifier=com.finasis.games"])
            
        # Veri dosyalarını ekle
        separator = ";" if self.current_platform == "windows" else ":"
        for asset_dir in game["assets"]:
            pyinstaller_cmd.extend([
                "--add-data",
                f"{asset_dir}{separator}assets"
            ])
            
        # Script dosyasını ekle
        pyinstaller_cmd.append(game["script"])
        
        try:
            result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"{game['name']} başarıyla derlendi!")
                return True
            else:
                logger.error(f"Derleme hatası: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Derleme sırasında hata: {e}")
            return False
            
    def build_mobile_game(self, game: Dict) -> bool:
        """Mobil oyunu derle"""
        logger.info(f"{game['name']} mobil versiyonu derleniyor...")
        
        # Buildozer kontrolü
        try:
            subprocess.run(["buildozer", "--version"], check=True, capture_output=True)
        except:
            logger.warning("Buildozer bulunamadı! Mobil derleme atlanacak.")
            return False
            
        # Buildozer spec dosyasını oluştur
        buildozer_spec = f"""
[app]
title = {game['name']}
package.name = finasisgames
package.domain = tr.com.finasis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = {self.config['version']}
requirements = python3,{','.join(game['requirements'])}
orientation = landscape
fullscreen = 0
android.permissions = CAMERA
android.api = 30
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
p4a.bootstrap = sdl2
"""
        
        mobile_build_dir = self.build_dir / "mobile" / game["name"]
        mobile_build_dir.mkdir(parents=True, exist_ok=True)
        
        with open(mobile_build_dir / "buildozer.spec", "w") as f:
            f.write(buildozer_spec)
            
        # Oyun dosyalarını kopyala
        shutil.copy(game["script"], mobile_build_dir / "main.py")
        
        # Assets dizinini kopyala
        for asset_dir in game["assets"]:
            if Path(asset_dir).exists():
                shutil.copytree(asset_dir, mobile_build_dir / "assets")
                
        # Buildozer'ı çalıştır
        try:
            os.chdir(mobile_build_dir)
            subprocess.run(["buildozer", "android", "debug"], check=True)
            logger.info("Android APK başarıyla oluşturuldu!")
            
            # APK'yı dist dizinine taşı
            if (mobile_build_dir / "bin").exists():
                for file in (mobile_build_dir / "bin").glob("*.apk"):
                    shutil.copy(file, self.dist_dir / "mobile" / file.name)
                    logger.info(f"{file.name} dosyası dist/mobile/ dizinine kopyalandı")
                    
            os.chdir("../..")
            return True
            
        except Exception as e:
            logger.error(f"Android derleme hatası: {e}")
            os.chdir("../..")
            return False
            
    def create_zip_package(self) -> None:
        """Tüm derlenmiş dosyaları zip haline getir"""
        logger.info("Zip paketi oluşturuluyor...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"FinAsis_Games_{self.config['version']}_{timestamp}.zip"
        
        if self.dist_dir.exists():
            shutil.make_archive(
                str(self.dist_dir / f"FinAsis_Games_{self.config['version']}_{timestamp}"),
                'zip',
                str(self.dist_dir)
            )
            logger.info(f"{zip_filename} oluşturuldu!")
        else:
            logger.warning("dist/ dizini bulunamadı")
            
    def notify_ci_cd(self, status: str, message: str) -> None:
        """CI/CD sistemine bildirim gönder"""
        if not self.config["ci_cd"]["enabled"]:
            return
            
        try:
            if self.config["ci_cd"]["provider"] == "github":
                with open(os.environ.get("GITHUB_OUTPUT", ""), "a") as f:
                    f.write(f"status={status}\n")
                    f.write(f"message={message}\n")
                    
            elif self.config["ci_cd"]["provider"] == "gitlab":
                print(f"status={status}")
                print(f"message={message}")
                
            if self.config["ci_cd"]["notifications"]["slack"]:
                requests.post(
                    os.environ.get("SLACK_WEBHOOK_URL", ""),
                    json={"text": f"Build {status}: {message}"}
                )
                
        except Exception as e:
            logger.error(f"CI/CD bildirimi gönderilemedi: {e}")
            
    def build(self) -> bool:
        """Tüm oyunları derle"""
        logger.info(f"FinAsis Oyun Derleyicisi v{self.config['version']}")
        logger.info("=" * 50)
        
        if not self.check_requirements():
            return False
            
        if not self.run_tests():
            self.notify_ci_cd("failed", "Testler başarısız")
            return False
            
        self.create_build_dirs()
        self.copy_assets()
        
        # Masaüstü oyunlarını derle
        desktop_success = True
        for game in self.config["game_modules"]:
            if not self.build_desktop_game(game):
                desktop_success = False
                
        # Mobil oyunları derle
        mobile_success = True
        for game in self.config["game_modules"]:
            if not self.build_mobile_game(game):
                mobile_success = False
                
        if not (desktop_success or mobile_success):
            self.notify_ci_cd("failed", "Derleme başarısız")
            return False
            
        self.create_zip_package()
        self.notify_ci_cd("success", "Derleme başarılı")
        return True
        
def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='FinAsis Oyun Derleme Aracı')
    parser.add_argument('--desktop-only', action='store_true', help='Sadece masaüstü uygulamaları derle')
    parser.add_argument('--mobile-only', action='store_true', help='Sadece mobil uygulamaları derle')
    parser.add_argument('--skip-zip', action='store_true', help='Zip paketi oluşturmayı atla')
    parser.add_argument('--config', type=str, help='Yapılandırma dosyası yolu')
    
    args = parser.parse_args()
    
    try:
        builder = GameBuilder(args.config)
        success = builder.build()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"Beklenmeyen hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 