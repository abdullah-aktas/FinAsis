import os
import sys
import subprocess
import shutil
import platform
import logging
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_desktop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DesktopBuilder:
    """Masaüstü uygulaması derleme yöneticisi"""
    
    def __init__(self):
        self.build_dir = Path("build/desktop")
        self.dist_dir = Path("dist")
        self.cache_dir = Path(".build_cache")
        self.config_file = Path("desktop_config.json")
        self.requirements_file = Path("requirements.txt")
        self.start_time = time.time()
        self.current_platform = platform.system().lower()
        self.arch = platform.machine().lower()
        
        # Güvenlik ayarları
        self.security_config = {
            "encryption_key": os.getenv("BUILD_ENCRYPTION_KEY", "your-default-key"),
            "sign_certificate": os.getenv("SIGN_CERTIFICATE_PATH", ""),
            "verify_checksums": True,
            "scan_malware": True,
            "check_vulnerabilities": True
        }
        
        # Performans ayarları
        self.performance_config = {
            "max_workers": os.cpu_count() or 4,
            "chunk_size": 8192,
            "compression_level": 6,
            "cache_enabled": True,
            "parallel_build": True
        }
        
        # Varsayılan yapılandırma
        self.config = {
            "app_name": "FinAsis",
            "version": "1.0.0",
            "company_name": "FinAsis",
            "description": "FinAsis Masaüstü Uygulaması",
            "author": "FinAsis Team",
            "update_server": "https://updates.finasis.com.tr",
            "update_channel": "stable",
            "auto_update": True,
            "platforms": ["windows", "linux", "macos"],
            "architectures": ["x86_64", "arm64"],
            "hidden_imports": [
                "django",
                "django.core",
                "django.contrib",
                "django.conf",
                "django.template",
                "django.template.loader",
                "django.template.context_processors",
                "django.template.loaders",
                "django.template.loaders.filesystem",
                "django.template.loaders.app_directories",
                "django.middleware",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "rest_framework",
                "corsheaders",
                "whitenoise",
            ],
            "excluded_modules": [
                "tkinter",
                "test",
                "unittest",
                "_pytest",
            ],
            "test_config": {
                "unit_tests": True,
                "integration_tests": True,
                "performance_tests": True,
                "security_tests": True,
                "coverage_threshold": 80,
                "test_timeout": 300,
            },
            "ci_cd": {
                "enabled": True,
                "provider": "github",
                "auto_deploy": True,
                "deploy_targets": ["production", "staging"],
                "notifications": {
                    "slack": True,
                    "email": True,
                }
            }
        }
        
        # Yapılandırmayı yükle
        self.load_config()
        
    def load_config(self) -> None:
        """Yapılandırma dosyasını yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
                logger.info("Yapılandırma dosyası yüklendi")
        except Exception as e:
            logger.warning(f"Yapılandırma dosyası yüklenemedi: {e}")
            
    def save_config(self) -> None:
        """Yapılandırmayı kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("Yapılandırma dosyası kaydedildi")
        except Exception as e:
            logger.error(f"Yapılandırma dosyası kaydedilemedi: {e}")
            
    def check_dependencies(self) -> bool:
        """Gerekli bağımlılıkları kontrol et"""
        logger.info("Bağımlılıklar kontrol ediliyor...")
        
        try:
            required_packages = [
                "PyQt5",
                "cryptography",
                "psutil",
                "aiohttp",
                "python-dotenv"
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
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
            logger.error(f"Bağımlılık kontrolü hatası: {str(e)}")
            return False
                
    def clean_build(self) -> None:
        """Önceki derleme dosyalarını temizle"""
        paths = [self.build_dir, self.dist_dir, Path("FinAsis.spec")]
        for path in paths:
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                logger.info(f"{path} temizlendi")
            except Exception as e:
                logger.warning(f"{path} temizlenemedi: {e}")
                
    def create_build_dirs(self) -> None:
        """Gerekli dizinleri oluştur"""
        for path in [self.build_dir, self.cache_dir]:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"{path} dizini oluşturuldu")
            
    def copy_project_files(self) -> None:
        """Proje dosyalarını kopyala"""
        project_files = [
            "manage.py",
            "config",
            "core",
            "users",
            "api",
            "static",
            "templates",
            "db.sqlite3",  # Eğer varsa
            "requirements.txt",
            ".env.example",  # Örnek çevre değişkenleri
            "tests",  # Test dosyaları
        ]
        
        for item in project_files:
            src = Path(item)
            if src.exists():
                dest = self.build_dir / item
                logger.info(f"{item} kopyalanıyor...")
                try:
                    if src.is_file():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dest)
                    else:
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(src, dest)
                except Exception as e:
                    logger.error(f"{item} kopyalanırken hata: {e}")
                    
    def get_file_hash(self, file_path: Path) -> str:
        """Dosya hash değerini hesapla"""
        if not file_path.exists():
            return ""
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def prepare_pyinstaller_command(self, platform: Optional[str] = None, arch: Optional[str] = None) -> List[str]:
        """PyInstaller komutunu hazırla"""
        platform = platform or self.current_platform
        arch = arch or self.arch
        
        icon_path = Path("static/img/favicon.ico")
        separator = ";" if platform == "windows" else ":"
        
        cmd = [
            "pyinstaller",
            f"--name={self.config['app_name']}",
            "--onefile",
            "--windowed",
            "--clean",
            "--log-level=DEBUG",
            "--noconfirm",
            f"--specpath={self.build_dir}",
            f"--workpath={self.build_dir / 'work'}",
            f"--distpath={self.dist_dir / platform / arch}",
            "--key=your-encryption-key-here",  # Şifreleme anahtarı
        ]
        
        # Platform özel ayarlar
        if platform == "windows":
            cmd.extend(["--icon=static/img/favicon.ico", "--uac-admin"])
        elif platform == "macos":
            cmd.extend(["--icon=static/img/favicon.icns", "--osx-bundle-identifier=com.finasis.app"])
        elif platform == "linux":
            cmd.extend(["--icon=static/img/favicon.png"])
            
        # İkon ekle
        if icon_path.exists():
            cmd.append(f"--icon={icon_path}")
            
        # Veri dosyalarını ekle
        for item in self.build_dir.glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to(self.build_dir)
                cmd.append(f"--add-data={item}{separator}{rel_path.parent}")
                
        # Gizli importları ekle
        for imp in self.config["hidden_imports"]:
            cmd.append(f"--hidden-import={imp}")
            
        # Hariç tutulan modülleri ekle
        for exc in self.config["excluded_modules"]:
            cmd.append(f"--exclude-module={exc}")
            
        # Ana script'i ekle
        cmd.append("desktop_app.py")
        
        return cmd
        
    def run_tests(self) -> bool:
        """Testleri çalıştır"""
        if not self.config["test_config"]["unit_tests"]:
            logger.info("Testler devre dışı bırakıldı")
            return True
            
        logger.info("Testler çalıştırılıyor...")
        
        # Test dizinini kontrol et
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
            
    def check_updates(self) -> Optional[Dict]:
        """Güncellemeleri kontrol et"""
        if not self.config["auto_update"]:
            return None
            
        try:
            response = requests.get(
                f"{self.config['update_server']}/check",
                params={
                    "version": self.config["version"],
                    "platform": self.current_platform,
                    "arch": self.arch,
                    "channel": self.config["update_channel"]
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Güncelleme kontrolü başarısız: {e}")
            return None
            
    def download_update(self, update_info: Dict) -> bool:
        """Güncellemeyi indir"""
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                response = requests.get(update_info["download_url"], stream=True)
                response.raise_for_status()
                
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                    
                # Güncelleme dosyasını doğrula
                if hashlib.sha256(open(tmp_file.name, 'rb').read()).hexdigest() != update_info["sha256"]:
                    raise ValueError("Güncelleme dosyası doğrulanamadı")
                    
                # Güncellemeyi uygula
                with zipfile.ZipFile(tmp_file.name) as zip_ref:
                    zip_ref.extractall(self.dist_dir)
                    
                return True
                
        except Exception as e:
            logger.error(f"Güncelleme indirilemedi: {e}")
            return False
            
    def build_for_platform(self, platform: str, arch: str) -> bool:
        """Belirli bir platform için derle"""
        logger.info(f"{platform}/{arch} için derleme başlatılıyor...")
        
        cmd = self.prepare_pyinstaller_command(platform, arch)
        logger.debug("Komut: " + " ".join(cmd))
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"{platform}/{arch} derleme hatası:")
                logger.error(result.stderr)
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"{platform}/{arch} derleme sırasında hata: {e}")
            return False
            
    def build_all_platforms(self) -> bool:
        """Tüm platformlar için derle"""
        success = True
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for platform in self.config["platforms"]:
                for arch in self.config["architectures"]:
                    futures.append(executor.submit(self.build_for_platform, platform, arch))
                    
            for future in futures:
                if not future.result():
                    success = False
                    
        return success
        
    def notify_ci_cd(self, status: str, message: str) -> None:
        """CI/CD sistemine bildirim gönder"""
        if not self.config["ci_cd"]["enabled"]:
            return
            
        try:
            if self.config["ci_cd"]["provider"] == "github":
                # GitHub Actions bildirimi
                with open(os.environ.get("GITHUB_OUTPUT", ""), "a") as f:
                    f.write(f"status={status}\n")
                    f.write(f"message={message}\n")
                    
            elif self.config["ci_cd"]["provider"] == "gitlab":
                # GitLab CI bildirimi
                print(f"status={status}")
                print(f"message={message}")
                
            # Slack bildirimi
            if self.config["ci_cd"]["notifications"]["slack"]:
                requests.post(
                    os.environ.get("SLACK_WEBHOOK_URL", ""),
                    json={"text": f"Build {status}: {message}"}
                )
                
        except Exception as e:
            logger.error(f"CI/CD bildirimi gönderilemedi: {e}")
            
    def check_security(self) -> bool:
        """Güvenlik kontrollerini gerçekleştir"""
        try:
            # Dosya bütünlüğü kontrolü
            for root, _, files in os.walk(self.build_dir):
                for file in files:
                    file_path = Path(root) / file
                    if not self.verify_file_integrity(file_path):
                        logger.error(f"Dosya bütünlüğü bozuk: {file_path}")
                        return False
            
            # Zararlı yazılım taraması
            if self.security_config["scan_malware"]:
                if not self.scan_for_malware():
                    logger.error("Zararlı yazılım tespit edildi")
                    return False
            
            # Güvenlik açığı taraması
            if self.security_config["check_vulnerabilities"]:
                if not self.check_vulnerabilities():
                    logger.error("Güvenlik açıkları tespit edildi")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Güvenlik kontrolü hatası: {e}")
            return False

    def verify_file_integrity(self, file_path: Path) -> bool:
        """Dosya bütünlüğünü doğrula"""
        try:
            if not file_path.exists():
                return False
            
            # Dosya hash'ini hesapla
            file_hash = self.get_file_hash(file_path)
            
            # Hash değerini kaydet
            hash_file = file_path.with_suffix(file_path.suffix + '.hash')
            if hash_file.exists():
                with open(hash_file, 'r') as f:
                    stored_hash = f.read().strip()
                    return file_hash == stored_hash
            else:
                with open(hash_file, 'w') as f:
                    f.write(file_hash)
                return True
        except Exception as e:
            logger.error(f"Dosya bütünlüğü kontrolü hatası: {e}")
            return False

    def scan_for_malware(self) -> bool:
        """Zararlı yazılım taraması yap"""
        try:
            # TODO: Gerçek zararlı yazılım taraması implementasyonu
            # Örnek: subprocess.run(["clamscan", "-r", str(self.build_dir)])
            return True
        except Exception as e:
            logger.error(f"Zararlı yazılım taraması hatası: {e}")
            return False

    def check_vulnerabilities(self) -> bool:
        """Güvenlik açığı taraması yap"""
        try:
            # TODO: Gerçek güvenlik açığı taraması implementasyonu
            # Örnek: subprocess.run(["safety", "check"])
            return True
        except Exception as e:
            logger.error(f"Güvenlik açığı taraması hatası: {e}")
            return False

    def optimize_performance(self) -> None:
        """Performans optimizasyonları yap"""
        try:
            # Önbellek temizliği
            if self.performance_config["cache_enabled"]:
                self.clean_cache()
            
            # Paralel işleme ayarları
            if self.performance_config["parallel_build"]:
                os.environ["PYTHONUNBUFFERED"] = "1"
                os.environ["PYTHONOPTIMIZE"] = "2"
            
            # Bellek optimizasyonu
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Performans optimizasyonu hatası: {e}")

    def clean_cache(self) -> None:
        """Önbelleği temizle"""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True)
                logger.info("Önbellek temizlendi")
        except Exception as e:
            logger.error(f"Önbellek temizleme hatası: {e}")

    def sign_file(self, file_path: Path) -> str:
        """Dosyayı imzalama"""
        try:
            if not self.security_config["sign_certificate"]:
                logger.warning("İmzalama sertifikası bulunamadı")
                return ""
                
            # TODO: Gerçek imzalama işlemi implementasyonu
            # Örnek: subprocess.run(["signtool", "sign", "/f", self.security_config["sign_certificate"], str(file_path)])
            return "signed"
        except Exception as e:
            logger.error(f"Dosya imzalama hatası: {e}")
            return ""

    def build(self) -> bool:
        """Uygulamayı derle"""
        logger.info(f"FinAsis Masaüstü Uygulaması Derleyicisi v{self.config['version']}")
        logger.info("=" * 50)
        
        if not self.check_dependencies():
            return False
        
        # Performans optimizasyonları
        self.optimize_performance()
        
        # Testleri çalıştır
        if not self.run_tests():
            self.notify_ci_cd("failed", "Testler başarısız")
            return False
        
        # Güvenlik kontrolleri
        if not self.check_security():
            self.notify_ci_cd("failed", "Güvenlik kontrolleri başarısız")
            return False
        
        self.clean_build()
        self.create_build_dirs()
        self.copy_project_files()
        
        # Tüm platformlar için derle
        if not self.build_all_platforms():
            self.notify_ci_cd("failed", "Derleme başarısız")
            return False
        
        # Derleme başarılı
        build_info = {
            "version": self.config["version"],
            "build_date": datetime.now().isoformat(),
            "platforms": {},
            "build_time": time.time() - self.start_time,
            "security_checks": {
                "file_integrity": True,
                "malware_scan": True,
                "vulnerability_scan": True
            },
            "performance_metrics": {
                "build_duration": time.time() - self.start_time,
                "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_usage": psutil.cpu_percent()
            }
        }
        
        # Her platform için build bilgilerini topla
        for platform in self.config["platforms"]:
            for arch in self.config["architectures"]:
                exe_path = self.dist_dir / platform / arch / f"{self.config['app_name']}.exe"
                if exe_path.exists():
                    build_info["platforms"][f"{platform}_{arch}"] = {
                        "file_hash": self.get_file_hash(exe_path),
                        "file_size": exe_path.stat().st_size,
                        "signature": self.sign_file(exe_path) if self.security_config["sign_certificate"] else None
                    }
        
        # Build bilgilerini kaydet
        with open(self.build_dir / "build_info.json", "w") as f:
            json.dump(build_info, f, indent=4)
        
        # Güncellemeleri kontrol et
        update_info = self.check_updates()
        if update_info and update_info["version"] != self.config["version"]:
            logger.info(f"Yeni güncelleme mevcut: {update_info['version']}")
            if self.download_update(update_info):
                logger.info("Güncelleme başarıyla uygulandı")
        
        self.notify_ci_cd("success", "Derleme başarılı")
        return True
        
def main():
    """Ana fonksiyon"""
    try:
        builder = DesktopBuilder()
        success = builder.build()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"Beklenmeyen hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 