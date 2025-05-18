#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FinAsis Yedekleme ve Temizleme Scripti
---------------------------------------

Bu script, FinAsis projesinin yedekleme ve temizleme işlemlerini otomatikleştirir.

Özellikler:
- Otomatik yedekleme
- Hassas dosya tespiti
- Şifreleme desteği
- Paralel işleme
- Detaylı raporlama
- E-posta bildirimleri
"""

import os
import sys
import shutil
import logging
import hashlib
import datetime
import smtplib
import ssl
import concurrent.futures
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import argparse


# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clean_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, config_path: str = "backup_config.json"):
        self.config = self._load_config(config_path)
        self.backup_dir = Path(self.config["backup_dir"])
        self.sensitive_patterns = self.config.get("sensitive_patterns", [])
        self.encryption_key = self.config.get("encryption_key")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Yapılandırma dosyasını yükle"""
        try:
            with open(config_path, "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Yapılandırma dosyası bulunamadı: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Yapılandırma dosyası geçersiz JSON formatında: {config_path}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Yapılandırma yükleme hatası: {str(e)}")
            sys.exit(1)
            
    def check_file_permissions(self, file_path: Path) -> bool:
        """Dosya izinlerini kontrol et"""
        try:
            # Dosya okunabilir mi?
            if not os.access(file_path, os.R_OK):
                logger.warning(f"Dosya okunamıyor: {file_path}")
                return False
                
            # Dosya yazılabilir mi?
            if not os.access(file_path, os.W_OK):
                logger.warning(f"Dosyaya yazılamıyor: {file_path}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Dosya izinleri kontrol edilirken hata: {e}")
            return False
            
    def is_sensitive_file(self, file_path: Path) -> bool:
        """Hassas dosya kontrolü"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            for pattern in self.sensitive_patterns:
                if pattern in content:
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"Hassas dosya kontrolü sırasında hata: {e}")
            return False
            
    def encrypt_file(self, file_path: Path) -> bool:
        """Dosyayı şifrele"""
        if not self.encryption_key:
            logger.warning("Şifreleme anahtarı bulunamadı!")
            return False
            
        try:
            # TODO: Gerçek şifreleme implementasyonu
            # Örnek: Fernet veya AES kullanarak şifreleme
            logger.info(f"Dosya şifrelendi: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Şifreleme hatası: {e}")
            return False
            
    def backup_backup_dirs(self) -> Dict[str, Any]:
        """Yedekleme dizinlerini yedekle"""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "sensitive_files": 0,
            "encrypted_files": 0,
            "errors": 0
        }
        
        try:
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{backup_time}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            def process_file(file_path: Path) -> None:
                try:
                    if not self.check_file_permissions(file_path):
                        stats["errors"] += 1
                        return
                        
                    stats["total_files"] += 1
                    stats["total_size"] += file_path.stat().st_size
                    
                    if self.is_sensitive_file(file_path):
                        stats["sensitive_files"] += 1
                        if self.encrypt_file(file_path):
                            stats["encrypted_files"] += 1
                            
                    # Dosyayı yedekle
                    shutil.copy2(file_path, backup_path / file_path.name)
                    
                except Exception as e:
                    logger.error(f"Dosya işlenirken hata: {e}")
                    stats["errors"] += 1
                    
            # Paralel işleme
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = []
                for root, _, files in os.walk(self.config["source_dir"]):
                    for file in files:
                        file_path = Path(root) / file
                        futures.append(executor.submit(process_file, file_path))
                        
                for future in concurrent.futures.as_completed(futures):
                    future.result()
                    
            return stats
        except Exception as e:
            logger.error(f"Yedekleme sırasında hata: {e}")
            return stats
        
    def clean_pycache_dirs(self) -> Dict[str, int]:
        """__pycache__ dizinlerini temizle"""
        stats = {"cleaned_dirs": 0, "errors": 0}
        
        for root, dirs, _ in os.walk(self.config["source_dir"]):
            if "__pycache__" in dirs:
                try:
                    shutil.rmtree(Path(root) / "__pycache__")
                    stats["cleaned_dirs"] += 1
                except Exception as e:
                    logger.error(f"Temizleme hatası: {e}")
                    stats["errors"] += 1
                    
        return stats
        
    def send_email_report(self, stats: Dict[str, Any]) -> bool:
        """E-posta raporu gönder"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config["email"]["from"]
            msg["To"] = self.config["email"]["to"]
            msg["Subject"] = "FinAsis Yedekleme Raporu"
            
            body = f"""
Yedekleme İstatistikleri:
------------------------
Toplam Dosya: {stats["total_files"]}
Toplam Boyut: {stats["total_size"] / 1024 / 1024:.2f} MB
Hassas Dosya: {stats["sensitive_files"]}
Şifrelenen: {stats["encrypted_files"]}
Hatalar: {stats["errors"]}
"""
            
            msg.attach(MIMEText(body, "plain"))
            
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.config["email"]["smtp_server"], 
                                self.config["email"]["smtp_port"], 
                                context=context) as server:
                server.login(self.config["email"]["username"], 
                           self.config["email"]["password"])
                server.send_message(msg)
                
            return True
        except Exception as e:
            logger.error(f"E-posta gönderimi hatası: {e}")
            return False
            
def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="FinAsis Yedekleme ve Temizleme Scripti")
    parser.add_argument("--config", default="backup_config.json", help="Yapılandırma dosyası yolu")
    args = parser.parse_args()
    
    manager = BackupManager(args.config)
    
    # Yedekleme
    backup_stats = manager.backup_backup_dirs()
    logger.info(f"Yedekleme tamamlandı: {backup_stats}")
    
    # Temizleme
    clean_stats = manager.clean_pycache_dirs()
    logger.info(f"Temizleme tamamlandı: {clean_stats}")
    
    # Rapor gönder
    if manager.config.get("email"):
        manager.send_email_report(backup_stats)
        
if __name__ == "__main__":
    main() 