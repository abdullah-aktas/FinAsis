import os
import sys
import json
import requests
import subprocess
import platform
import logging
from pathlib import Path
from packaging import version

class UpdateService:
    def __init__(self, current_version, update_url, app_name="FinAsis"):
        self.current_version = current_version
        self.update_url = update_url
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        
        # Güncelleme dosyalarının indirileceği dizin
        self.update_dir = Path.home() / ".finasis" / "updates"
        self.update_dir.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self):
        """Sunucudan güncelleme kontrolü yapar"""
        try:
            response = requests.get(f"{self.update_url}/version")
            if response.status_code == 200:
                update_info = response.json()
                latest_version = update_info.get("version")
                
                if latest_version and version.parse(latest_version) > version.parse(self.current_version):
                    return {
                        "available": True,
                        "version": latest_version,
                        "release_notes": update_info.get("release_notes", ""),
                        "download_url": update_info.get("download_url")
                    }
            
            return {"available": False}
        except Exception as e:
            self.logger.error(f"Güncelleme kontrolü sırasında hata: {str(e)}")
            return {"available": False, "error": str(e)}
    
    def download_update(self, download_url):
        """Güncelleme dosyasını indirir"""
        try:
            # İndirme URL'sinden dosya adını al
            file_name = download_url.split("/")[-1]
            file_path = self.update_dir / file_name
            
            # Dosyayı indir
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(file_path)
        except Exception as e:
            self.logger.error(f"Güncelleme indirme sırasında hata: {str(e)}")
            return None
    
    def install_update(self, update_file_path):
        """İndirilen güncellemeyi kurar"""
        try:
            # İşletim sistemine göre kurulum komutunu belirle
            if platform.system() == "Windows":
                # Windows için kurulum
                subprocess.Popen([update_file_path, "/SILENT", "/NORESTART"])
            elif platform.system() == "Darwin":  # macOS
                # macOS için kurulum
                subprocess.Popen(["open", update_file_path])
            elif platform.system() == "Linux":
                # Linux için kurulum (deb veya rpm paketleri için)
                if update_file_path.endswith(".deb"):
                    subprocess.Popen(["sudo", "dpkg", "-i", update_file_path])
                elif update_file_path.endswith(".rpm"):
                    subprocess.Popen(["sudo", "rpm", "-i", update_file_path])
            
            # Uygulamayı kapat
            self.logger.info("Güncelleme kuruluyor, uygulama kapatılıyor...")
            return True
        except Exception as e:
            self.logger.error(f"Güncelleme kurulumu sırasında hata: {str(e)}")
            return False
    
    def run_update_check(self):
        """Güncelleme kontrolü yapar ve gerekirse kurar"""
        update_info = self.check_for_updates()
        
        if update_info.get("available", False):
            self.logger.info(f"Yeni sürüm mevcut: {update_info['version']}")
            
            # Güncellemeyi indir
            update_file = self.download_update(update_info["download_url"])
            
            if update_file:
                # Güncellemeyi kur
                return self.install_update(update_file)
        
        return False 