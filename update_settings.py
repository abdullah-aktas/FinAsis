#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FinAsis - Django Ayarları Güncelleme Betiği
-------------------------------------------
Bu script, Django settings.py dosyasındaki yapılandırmaları günceller ve doğrular.
"""

import os
import re
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_settings.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SettingsSection(Enum):
    """Ayarlar dosyasındaki bölümleri temsil eder."""
    INSTALLED_APPS = auto()
    MIDDLEWARE = auto()
    DATABASES = auto()
    CACHES = auto()
    AUTH_PASSWORD_VALIDATORS = auto()
    REST_FRAMEWORK = auto()
    CORS_ALLOWED_ORIGINS = auto()

@dataclass
class SettingsUpdate:
    """Ayarlar güncellemesi için veri yapısı."""
    section: SettingsSection
    pattern: str
    replacement: str
    validation: Optional[str] = None

class SettingsManager:
    """Django ayarlarını yöneten sınıf."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.settings_path = base_dir / 'config' / 'settings' / 'base.py'
        self.backup_path = self.settings_path.with_suffix('.py.bak')
        
        # Güncelleme kuralları
        self.update_rules: Dict[SettingsSection, SettingsUpdate] = {
            SettingsSection.INSTALLED_APPS: SettingsUpdate(
                section=SettingsSection.INSTALLED_APPS,
                pattern=r'INSTALLED_APPS\s*=\s*\[(.*?)\]',
                replacement=r"INSTALLED_APPS = [\n    'django.contrib.admin',\n    'django.contrib.auth',\n    'django.contrib.contenttypes',\n    'django.contrib.sessions',\n    'django.contrib.messages',\n    'django.contrib.staticfiles',\n    'rest_framework',\n    'corsheaders',\n    'drf_yasg',\n    'analytics',\n    'permissions',\n]",
                validation=r"INSTALLED_APPS\s*=\s*\[.*?\]"
            ),
            SettingsSection.MIDDLEWARE: SettingsUpdate(
                section=SettingsSection.MIDDLEWARE,
                pattern=r'MIDDLEWARE\s*=\s*\[(.*?)\]',
                replacement=r"MIDDLEWARE = [\n    'django.middleware.security.SecurityMiddleware',\n    'django.contrib.sessions.middleware.SessionMiddleware',\n    'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',\n    'django.middleware.csrf.CsrfViewMiddleware',\n    'django.contrib.auth.middleware.AuthenticationMiddleware',\n    'django.contrib.messages.middleware.MessageMiddleware',\n    'django.middleware.clickjacking.XFrameOptionsMiddleware',\n]",
                validation=r"MIDDLEWARE\s*=\s*\[.*?\]"
            )
        }
    
    def backup_settings(self) -> bool:
        """Ayarlar dosyasının yedeğini alır."""
        try:
            if self.settings_path.exists():
                import shutil
                shutil.copy2(self.settings_path, self.backup_path)
                logger.info(f"Ayarlar dosyası yedeklendi: {self.backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Yedekleme hatası: {e}")
            return False
    
    def restore_backup(self) -> bool:
        """Yedekten geri yükleme yapar."""
        try:
            if self.backup_path.exists():
                import shutil
                shutil.copy2(self.backup_path, self.settings_path)
                logger.info(f"Ayarlar dosyası yedekten geri yüklendi: {self.settings_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Geri yükleme hatası: {e}")
            return False
    
    def read_settings(self) -> Optional[str]:
        """Ayarlar dosyasını okur."""
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if content is None or len(content) < 2:
                    print(f"❗ {self.settings_path} dosyası boş veya çok kısa!")
                    # Gerekirse otomatik düzeltme eklenebilir
                return content
        except Exception as e:
            logger.error(f"Ayarlar dosyası okuma hatası: {e}")
            return None
    
    def write_settings(self, content: str) -> bool:
        """Ayarlar dosyasına yazar."""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info("Ayarlar dosyası güncellendi")
            return True
        except Exception as e:
            logger.error(f"Ayarlar dosyası yazma hatası: {e}")
            return False
    
    def validate_section(self, content: str, section: SettingsSection) -> bool:
        """Belirli bir bölümün doğruluğunu kontrol eder."""
        if section not in self.update_rules:
            return True
        
        rule = self.update_rules[section]
        if rule.validation:
            return bool(re.search(rule.validation, content, re.DOTALL))
        return True
    
    def update_section(self, content: str, section: SettingsSection) -> Tuple[str, bool]:
        """Belirli bir bölümü günceller."""
        if section not in self.update_rules:
            return content, False
        
        rule = self.update_rules[section]
        try:
            updated_content = re.sub(
                rule.pattern,
                rule.replacement,
                content,
                flags=re.DOTALL
            )
            if updated_content == content:
                logger.warning(f"{section.name} bölümü güncellenmedi")
                return content, False
            
            if not self.validate_section(updated_content, section):
                logger.error(f"{section.name} bölümü doğrulama hatası")
                return content, False
            
            logger.info(f"{section.name} bölümü başarıyla güncellendi")
            return updated_content, True
        except Exception as e:
            logger.error(f"{section.name} güncelleme hatası: {e}")
            return content, False
    
    def update_all(self) -> bool:
        """Tüm ayarları günceller."""
        if not self.settings_path.exists():
            logger.error(f"Ayarlar dosyası bulunamadı: {self.settings_path}")
            return False
        
        if not self.backup_settings():
            logger.error("Yedekleme başarısız oldu")
            return False
        
        content = self.read_settings()
        if not content:
            return False
        
        updated = False
        for section in SettingsSection:
            content, section_updated = self.update_section(content, section)
            updated = updated or section_updated
        
        if updated:
            return self.write_settings(content)
        return True

def parse_args() -> argparse.Namespace:
    """Komut satırı argümanlarını ayrıştırır."""
    parser = argparse.ArgumentParser(
        description='Django ayarlarını güncelleme betiği'
    )
    parser.add_argument(
        '--restore',
        action='store_true',
        help='Yedekten geri yükleme yapar'
    )
    parser.add_argument(
        '--section',
        choices=[s.name for s in SettingsSection],
        help='Güncellenecek bölümü belirtir'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Değişiklikleri simüle eder'
    )
    return parser.parse_args()

def main():
    """Ana program."""
    args = parse_args()
    base_dir = Path(__file__).resolve().parent.parent
    manager = SettingsManager(base_dir)
    
    if args.restore:
        if manager.restore_backup():
            logger.info("Yedekten geri yükleme başarılı")
        else:
            logger.error("Yedekten geri yükleme başarısız")
        return
    
    if args.dry_run:
        logger.info("Kuru çalıştırma modu aktif")
        return
    
    if args.section:
        section = SettingsSection[args.section]
        content = manager.read_settings()
        if content:
            updated_content, success = manager.update_section(content, section)
            if success:
                manager.write_settings(updated_content)
    else:
        if manager.update_all():
            logger.info("Tüm ayarlar başarıyla güncellendi")
        else:
            logger.error("Ayarlar güncellenirken hata oluştu")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program kullanıcı tarafından durduruldu")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        sys.exit(1) 