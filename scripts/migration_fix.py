# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
MVT dönüşümünde modül birleştirmeleri sonrası migrasyon sorunlarını düzeltme betiği
"""
import os
import shutil
from pathlib import Path
import json
import sys
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_fix.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass
class ModuleMerge:
    old_module: str
    new_module: str
    is_submodule: bool = False
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

# Modül birleştirmeleri - yeni değer, tam olarak yeni modül yolunu içermelidir
MODULE_MERGES: Dict[str, ModuleMerge] = {
    # CRM ve Customers modülleri birleştirildi
    'customers': ModuleMerge('customers', 'apps.crm', False, ['apps.crm']),
    'customer_management': ModuleMerge('customer_management', 'apps.crm', False, ['apps.crm']),
    
    # User ve HR modülleri birleştirildi
    'users': ModuleMerge('users', 'apps.hr_management', False, ['apps.hr_management']),
    
    # Inventory, Stock ve Assets modülleri birleştirildi
    'inventory': ModuleMerge('inventory', 'apps.stock_management', False, ['apps.stock_management']),
    'assets': ModuleMerge('assets', 'apps.stock_management', False, ['apps.stock_management']),
    'asset_management': ModuleMerge('asset_management', 'apps.stock_management', False, ['apps.stock_management']),
    
    # Integrations modülü altında toplanan alt modüller
    'efatura': ModuleMerge('efatura', 'integrations.efatura', False, ['integrations.efatura']),
    'bank_integration': ModuleMerge('bank_integration', 'integrations.bank_integration', False, ['integrations.bank_integration']),
    'external_integrations': ModuleMerge('external_integrations', 'integrations.external', False, ['integrations.external']),
    'ext_services': ModuleMerge('ext_services', 'integrations.services', False, ['integrations.services']),
    
    # Diğer modül eşleştirmeleri
    'backup_manager': ModuleMerge('backup_manager', 'apps.backup_manager', False, ['apps.backup_manager']),
    'permissions': ModuleMerge('permissions', 'apps.permissions', False, ['apps.permissions']),
    'blockchain': ModuleMerge('blockchain', 'apps.blockchain', False, ['apps.blockchain']),
    'ai_assistant': ModuleMerge('ai_assistant', 'apps.ai_assistant', False, ['apps.ai_assistant']),
    'seo_management': ModuleMerge('seo_management', 'apps.seo', False, ['apps.seo']),
    'virtual_company': ModuleMerge('virtual_company', 'apps.virtual_company', False, ['apps.virtual_company']),
    'analytics': ModuleMerge('analytics', 'apps.analytics', False, ['apps.analytics']),
    'game_app': ModuleMerge('game_app', 'games.game_app', False, ['games.game_app']),
    'ursina_game': ModuleMerge('ursina_game', 'games.ursina_game', False, ['games.ursina_game']),
    'accounting': ModuleMerge('accounting', 'apps.accounting', False, ['apps.accounting']),
    'finance': ModuleMerge('finance', 'apps.finance', False, ['apps.finance']),
    'finance.accounting': ModuleMerge('finance.accounting', 'finance.accounting', True, ['finance.accounting']),
    'finance.banking': ModuleMerge('finance.banking', 'finance.banking', True, ['finance.banking']),
    'finance.checks': ModuleMerge('finance.checks', 'finance.checks', True, ['finance.checks']),
    'finance.einvoice': ModuleMerge('finance.einvoice', 'finance.einvoice', True, ['finance.einvoice']),
    'checks': ModuleMerge('checks', 'apps.checks', False, ['apps.checks']),
}

def calculate_file_hash(file_path: Path) -> str:
    """Dosyanın SHA-256 hash değerini hesapla"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def backup_migrations() -> str:
    """Mevcut migrasyonları yedekle"""
    backup_dir = BASE_DIR / 'scripts' / 'migration_backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Migrasyonlar {backup_dir} dizinine yedekleniyor...")
    
    def backup_module_migrations(module_path: Path, backup_path: Path) -> None:
        """Tek bir modülün migrasyonlarını yedekle"""
        migrations_path = module_path / 'migrations'
        if migrations_path.exists():
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Migrasyon dosyalarını hash ile birlikte yedekle
            for file in migrations_path.glob('*.py'):
                dst = backup_path / file.name
                shutil.copy2(file, dst)
                file_hash = calculate_file_hash(file)
                hash_file = backup_path / f"{file.name}.sha256"
                hash_file.write_text(file_hash)
                logger.info(f"  Yedeklendi: {file} -> {dst} (Hash: {file_hash})")
    
    # Ana modülleri ve alt modülleri tara
    with ThreadPoolExecutor() as executor:
        for old_module, merge_info in MODULE_MERGES.items():
            module_path = BASE_DIR / old_module.replace('.', os.path.sep)
            module_backup_dir = backup_dir / old_module.replace('.', '_')
            executor.submit(backup_module_migrations, module_path, module_backup_dir)
    
    # apps altındaki modülleri de yedekle
    apps_dir = BASE_DIR / 'apps'
    if apps_dir.exists():
        with ThreadPoolExecutor() as executor:
            for module in apps_dir.iterdir():
                if module.is_dir():
                    module_backup_dir = backup_dir / f"apps_{module.name}"
                    executor.submit(backup_module_migrations, module, module_backup_dir)
                    
                    # Alt modüller varsa onları da yedekle
                    for subdir in module.iterdir():
                        if subdir.is_dir():
                            submodule_backup_dir = backup_dir / f"apps_{module.name}_{subdir.name}"
                            executor.submit(backup_module_migrations, subdir, submodule_backup_dir)
    
    return str(backup_dir)

def clean_migrations() -> None:
    """Migrasyon dosyalarını temizle - eski modüllerin migrasyonlarını temizle"""
    for old_module, merge_info in MODULE_MERGES.items():
        old_module_path = BASE_DIR / old_module.replace('.', os.path.sep)
        old_migrations_path = old_module_path / 'migrations'
        
        if old_migrations_path.exists():
            # Sadece __init__.py'yi bırak, diğer migrasyonları sil
            for file in old_migrations_path.glob('*.py'):
                if file.name != '__init__.py':
                    try:
                        file.unlink()
                        logger.info(f"Silindi: {file}")
                    except Exception as e:
                        logger.error(f"Hata: {file} silinemedi: {e}")

def update_migrations() -> None:
    """Model referans yollarını ve import ifadelerini güncelle"""
    def update_migration_file(file_path: Path, old_module: str, new_module: str) -> None:
        """Migrasyon dosyasındaki referansları güncelle"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Model import yollarını güncelle
            old_module_dotted = old_module.replace('.', r'\.')
            patterns = [
                (rf"from\s+{old_module_dotted}\.models\s+import", f"from {new_module}.models import"),
                (rf"to\s*=\s*['\"]({old_module_dotted})\.(\w+)['\"]", f"to=\'{new_module}.\\2\'"),
                (rf"dependencies\s*=\s*\[\s*\(?['\"]({old_module_dotted})['\"]", f"dependencies = [('{new_module}'")
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Güncellendi: {file_path}")
            
        except Exception as e:
            logger.error(f"Hata: {file_path} dosyası güncellenirken bir sorun oluştu: {e}")
    
    # Yeni modül yollarına göre migrasyonları güncelle
    with ThreadPoolExecutor() as executor:
        for old_module, merge_info in MODULE_MERGES.items():
            new_module_path = BASE_DIR / merge_info.new_module.replace('.', os.path.sep)
            new_migrations_path = new_module_path / 'migrations'
            
            if new_migrations_path.exists():
                for file in new_migrations_path.glob('*.py'):
                    if file.name != '__init__.py':
                        executor.submit(update_migration_file, file, old_module, merge_info.new_module)

def create_fake_migration_script() -> None:
    """Migrasyon sorunlarını çözmek için fake migrasyon betiği oluştur"""
    script_path = BASE_DIR / 'scripts' / 'apply_migrations.py'
    
    script_content = """#!/usr/bin/env python
\"\"\"
Migration uygulama programı.
Bu script, modül birleştirme işleminin ardından migrasyonları düzgün bir şekilde uygulamak için kullanılır.
\"\"\"

import os
import sys
import django
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set
from concurrent.futures import ThreadPoolExecutor

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_apply.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Django ayarlarını yükleme
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder

def get_applied_migrations() -> Set[str]:
    \"\"\"Uygulanmış migrasyonları al\"\"\"
    recorder = MigrationRecorder(connection)
    return {m.app + '.' + m.name for m in recorder.applied_migrations()}

def apply_migrations(apps: List[str]) -> None:
    \"\"\"Belirtilen uygulamalar için migrasyonları uygula\"\"\"
    executor = MigrationExecutor(connection)
    applied = get_applied_migrations()
    
    for app in apps:
        try:
            logger.info(f"{app} uygulaması için migrasyonlar uygulanıyor...")
            executor.migrate([app])
            logger.info(f"{app} uygulaması için migrasyonlar başarıyla uygulandı.")
        except Exception as e:
            logger.error(f"{app} uygulaması için migrasyon uygulanırken hata oluştu: {e}")

def main() -> None:
    \"\"\"Ana fonksiyon\"\"\"
    try:
        # Önce temel uygulamalar
        base_apps = [
            'apps.crm',
            'apps.hr_management',
            'apps.stock_management',
            'apps.accounting',
            'apps.finance'
        ]
        apply_migrations(base_apps)
        
        # Sonra entegrasyonlar
        integration_apps = [
            'integrations.efatura',
            'integrations.bank_integration',
            'integrations.external',
            'integrations.services'
        ]
        apply_migrations(integration_apps)
        
        # Son olarak diğer uygulamalar
        other_apps = [
            'apps.backup_manager',
            'apps.permissions',
            'apps.blockchain',
            'apps.ai_assistant',
            'apps.seo',
            'apps.virtual_company',
            'apps.analytics',
            'apps.checks',
            'games.game_app',
            'games.ursina_game'
        ]
        apply_migrations(other_apps)
        
    except Exception as e:
        logger.error(f"Migrasyon uygulama sırasında hata oluştu: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
    
    script_path.write_text(script_content, encoding='utf-8')
    script_path.chmod(0o755)  # Çalıştırılabilir yap
    logger.info(f"Fake migrasyon betiği oluşturuldu: {script_path}")

def main() -> None:
    """Ana fonksiyon"""
    try:
        # Migrasyonları yedekle
        backup_dir = backup_migrations()
        logger.info(f"Migrasyonlar başarıyla yedeklendi: {backup_dir}")
        
        # Eski migrasyonları temizle
        clean_migrations()
        logger.info("Eski migrasyonlar temizlendi")
        
        # Migrasyonları güncelle
        update_migrations()
        logger.info("Migrasyonlar güncellendi")
        
        # Fake migrasyon betiği oluştur
        create_fake_migration_script()
        logger.info("Fake migrasyon betiği oluşturuldu")
        
    except Exception as e:
        logger.error(f"İşlem sırasında bir hata oluştu: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()