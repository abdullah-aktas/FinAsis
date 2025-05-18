#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FinAsis - URL Yapılandırma Güncelleme Betiği
--------------------------------------------
Bu script, Django URL yapılandırmalarını günceller ve doğrular.
"""

import os
import re
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum, auto

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_urls.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class URLPatternType(Enum):
    """URL desen tiplerini temsil eder."""
    PATH = auto()
    RE_PATH = auto()
    INCLUDE = auto()
    VIEW = auto()
    NAMESPACE = auto()

@dataclass
class URLPattern:
    """URL deseni için veri yapısı."""
    pattern_type: URLPatternType
    pattern: str
    replacement: str
    validation: Optional[str] = None

class URLManager:
    """URL yapılandırmalarını yöneten sınıf."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.backup_dir = base_dir / 'backups' / 'urls'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # URL desen kuralları
        self.pattern_rules: Dict[URLPatternType, URLPattern] = {
            URLPatternType.PATH: URLPattern(
                pattern_type=URLPatternType.PATH,
                pattern=r'path\([\'"]apps\.(\w+)',
                replacement=r'path([\'\1',
                validation=r'path\(.*?\)'
            ),
            URLPatternType.RE_PATH: URLPattern(
                pattern_type=URLPatternType.RE_PATH,
                pattern=r're_path\([\'"]apps\.(\w+)',
                replacement=r're_path([\'\1',
                validation=r're_path\(.*?\)'
            ),
            URLPatternType.INCLUDE: URLPattern(
                pattern_type=URLPatternType.INCLUDE,
                pattern=r'include\([\'"]apps\.(\w+)',
                replacement=r'include([\'\1',
                validation=r'include\(.*?\)'
            ),
            URLPatternType.VIEW: URLPattern(
                pattern_type=URLPatternType.VIEW,
                pattern=r'from apps\.(\w+)',
                replacement=r'from \1',
                validation=r'from \w+'
            ),
            URLPatternType.NAMESPACE: URLPattern(
                pattern_type=URLPatternType.NAMESPACE,
                pattern=r'namespace=[\'"]apps\.(\w+)',
                replacement=r'namespace=[\'\1',
                validation=r'namespace=[\'"].*?[\'"]'
            )
        }
    
    def backup_file(self, file_path: Path) -> bool:
        """Dosyanın yedeğini alır."""
        try:
            if file_path.exists():
                backup_path = self.backup_dir / f"{file_path.name}.bak"
                import shutil
                shutil.copy2(file_path, backup_path)
                logger.info(f"Dosya yedeklendi: {backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Yedekleme hatası: {e}")
            return False
    
    def restore_backup(self, file_path: Path) -> bool:
        """Yedekten geri yükleme yapar."""
        try:
            backup_path = self.backup_dir / f"{file_path.name}.bak"
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, file_path)
                logger.info(f"Dosya yedekten geri yüklendi: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Geri yükleme hatası: {e}")
            return False
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """Dosyayı okur."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if content is None or len(content) < 2:
                    print(f"❗ {file_path} dosyası boş veya çok kısa!")
                    # Gerekirse otomatik düzeltme eklenebilir
                return content
        except Exception as e:
            logger.error(f"Dosya okuma hatası: {e}")
            return None
    
    def write_file(self, file_path: Path, content: str) -> bool:
        """Dosyaya yazar."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"Dosya güncellendi: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Dosya yazma hatası: {e}")
            return False
    
    def validate_content(self, content: str, pattern_type: URLPatternType) -> bool:
        """İçeriğin doğruluğunu kontrol eder."""
        if pattern_type not in self.pattern_rules:
            return True
        
        rule = self.pattern_rules[pattern_type]
        if rule.validation:
            return bool(re.search(rule.validation, content, re.DOTALL))
        return True
    
    def update_content(self, content: str, pattern_type: URLPatternType) -> Tuple[str, bool]:
        """İçeriği günceller."""
        if pattern_type not in self.pattern_rules:
            return content, False
        
        rule = self.pattern_rules[pattern_type]
        try:
            updated_content = re.sub(
                rule.pattern,
                rule.replacement,
                content,
                flags=re.DOTALL
            )
            if updated_content == content:
                logger.warning(f"{pattern_type.name} deseni güncellenmedi")
                return content, False
            
            if not self.validate_content(updated_content, pattern_type):
                logger.error(f"{pattern_type.name} doğrulama hatası")
                return content, False
            
            logger.info(f"{pattern_type.name} deseni başarıyla güncellendi")
            return updated_content, True
        except Exception as e:
            logger.error(f"{pattern_type.name} güncelleme hatası: {e}")
            return content, False
    
    def find_urls_files(self) -> Set[Path]:
        """Tüm urls.py dosyalarını bulur."""
        urls_files: Set[Path] = set()
        
        # Ana urls.py dosyasını ekle
        main_urls = self.base_dir / 'config' / 'urls.py'
        if main_urls.exists():
            urls_files.add(main_urls)
        
        # Alt dizinlerdeki urls.py dosyalarını bul
        for root, _, files in os.walk(self.base_dir):
            if 'venv' in root or '.git' in root:
                continue
            
            for file in files:
                if file == 'urls.py':
                    urls_files.add(Path(root) / file)
        
        return urls_files
    
    def update_file(self, file_path: Path) -> bool:
        """Bir dosyayı günceller."""
        if not file_path.exists():
            logger.error(f"Dosya bulunamadı: {file_path}")
            return False
        
        if not self.backup_file(file_path):
            logger.error("Yedekleme başarısız oldu")
            return False
        
        content = self.read_file(file_path)
        if not content:
            return False
        
        updated = False
        for pattern_type in URLPatternType:
            content, pattern_updated = self.update_content(content, pattern_type)
            updated = updated or pattern_updated
        
        if updated:
            return self.write_file(file_path, content)
        return True
    
    def update_all(self) -> bool:
        """Tüm URL dosyalarını günceller."""
        urls_files = self.find_urls_files()
        if not urls_files:
            logger.error("URL dosyası bulunamadı")
            return False
        
        success = True
        for file_path in urls_files:
            if not self.update_file(file_path):
                success = False
        
        return success

def parse_args() -> argparse.Namespace:
    """Komut satırı argümanlarını ayrıştırır."""
    parser = argparse.ArgumentParser(
        description='Django URL yapılandırmalarını güncelleme betiği'
    )
    parser.add_argument(
        '--restore',
        action='store_true',
        help='Yedekten geri yükleme yapar'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Güncellenecek dosyayı belirtir'
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
    manager = URLManager(base_dir)
    
    if args.restore:
        if args.file:
            file_path = Path(args.file)
            if manager.restore_backup(file_path):
                logger.info("Yedekten geri yükleme başarılı")
            else:
                logger.error("Yedekten geri yükleme başarısız")
        else:
            logger.error("Geri yükleme için dosya belirtilmedi")
        return
    
    if args.dry_run:
        logger.info("Kuru çalıştırma modu aktif")
        return
    
    if args.file:
        file_path = Path(args.file)
        if manager.update_file(file_path):
            logger.info("Dosya başarıyla güncellendi")
        else:
            logger.error("Dosya güncellenirken hata oluştu")
    else:
        if manager.update_all():
            logger.info("Tüm URL dosyaları başarıyla güncellendi")
        else:
            logger.error("URL dosyaları güncellenirken hata oluştu")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program kullanıcı tarafından durduruldu")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        sys.exit(1) 