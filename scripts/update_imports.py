#!/usr/bin/env python
"""
İmport ifadelerini otomatik olarak güncelleyen script.
MVT dönüşümü sonrası eski import ifadelerini yeni yapıya uyarlayarak kodu düzeltir.
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/update_imports.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ImportMapping:
    old: str
    new: str
    pattern: Optional[str] = None

# İmport eşleştirme haritası - temel modüller
IMPORT_MAPPINGS: Dict[str, ImportMapping] = {
    # CRM ve Customers modül eşleştirmeleri
    'from apps.crm import': ImportMapping('from apps.crm import', 'from apps.crm import'),
    'from crm.models import': ImportMapping('from crm.models import', 'from crm.models import'),
    'from crm.views import': ImportMapping('from crm.views import', 'from crm.views import'),
    'from crm.serializers import': ImportMapping('from crm.serializers import', 'from crm.serializers import'),
    'from crm.forms import': ImportMapping('from crm.forms import', 'from crm.forms import'),
    
    # HR ve Users modül eşleştirmeleri
    'from apps.hr_management import': ImportMapping('from apps.hr_management import', 'from apps.hr_management import'),
    'from hr_management.models import': ImportMapping('from hr_management.models import', 'from hr_management.models import'),
    'from hr_management.views import': ImportMapping('from hr_management.views import', 'from hr_management.views import'),
    'from hr_management.serializers import': ImportMapping('from hr_management.serializers import', 'from hr_management.serializers import'),
    'from hr_management.forms import': ImportMapping('from hr_management.forms import', 'from hr_management.forms import'),
    
    # Stok ve Varlık Yönetimi eşleştirmeleri
    'from apps.stock_management import': ImportMapping('from apps.stock_management import', 'from apps.stock_management import'),
    'from stock_management.models import': ImportMapping('from stock_management.models import', 'from stock_management.models import'),
    
    # Entegrasyonlar
    'from integrations.efatura import': ImportMapping('from integrations.efatura import', 'from integrations.efatura import'),
    'from integrations.efatura.models import': ImportMapping('from integrations.efatura.models import', 'from integrations.efatura.models import'),
    'from integrations.bank_integration import': ImportMapping('from integrations.bank_integration import', 'from integrations.bank_integration import'),
    'from integrations.bank_integration.models import': ImportMapping('from integrations.bank_integration.models import', 'from integrations.bank_integration.models import'),
    'from integrations.services import': ImportMapping('from integrations.services import', 'from integrations.services import'),
    'from integrations.services.models import': ImportMapping('from integrations.services.models import', 'from integrations.services.models import'),
    'from integrations.external import': ImportMapping('from integrations.external import', 'from integrations.external import'),
    'from integrations.external.models import': ImportMapping('from integrations.external.models import', 'from integrations.external.models import'),
    
    # Diğer modüller
    'from apps.accounting import': ImportMapping('from apps.accounting import', 'from apps.accounting import'),
    'from accounting.models import': ImportMapping('from accounting.models import', 'from accounting.models import'),
    'from apps.backup_manager import': ImportMapping('from apps.backup_manager import', 'from apps.backup_manager import'),
    'from apps.permissions import': ImportMapping('from apps.permissions import', 'from apps.permissions import'),
    'from apps.blockchain import': ImportMapping('from apps.blockchain import', 'from apps.blockchain import'),
    'from apps.ai_assistant import': ImportMapping('from apps.ai_assistant import', 'from apps.ai_assistant import'),
    'from apps.seo import': ImportMapping('from apps.seo import', 'from apps.seo import'),
    'from apps.virtual_company import': ImportMapping('from apps.virtual_company import', 'from apps.virtual_company import'),
    'from apps.analytics import': ImportMapping('from apps.analytics import', 'from apps.analytics import'),
    
    # Oyun modülleri 
    'from games.game_app import': ImportMapping('from games.game_app import', 'from games.game_app import'),
    'from games.ursina_game import': ImportMapping('from games.ursina_game import', 'from games.ursina_game import'),
}

# ForeignKey referansları için model eşleştirme haritası
MODEL_MAPPINGS: Dict[str, ImportMapping] = {
    # String'li model referansları (ForeignKey, ManyToMany vs.)
    "'crm.Customer'": ImportMapping("'crm.Customer'", "'crm.Customer'"),
    "'hr_management.User'": ImportMapping("'hr_management.User'", "'hr_management.User'"),
    "'hr_management.Profile'": ImportMapping("'hr_management.Profile'", "'hr_management.Profile'"),
    "'stock_management.Asset'": ImportMapping("'stock_management.Asset'", "'stock_management.Asset'"),
    "'stock_management.Product'": ImportMapping("'stock_management.Product'", "'stock_management.Product'"),
    "'stock_management.Stock'": ImportMapping("'stock_management.Stock'", "'stock_management.Stock'"),
    "'integrations.efatura.EInvoice'": ImportMapping("'integrations.efatura.EInvoice'", "'integrations.efatura.EInvoice'"),
    "'integrations.bank_integration.BankAccount'": ImportMapping("'integrations.bank_integration.BankAccount'", "'integrations.bank_integration.BankAccount'"),
    "'integrations.services.Service'": ImportMapping("'integrations.services.Service'", "'integrations.services.Service'"),
    "'integrations.external.Integration'": ImportMapping("'integrations.external.Integration'", "'integrations.external.Integration'"),
    "'accounting.Account'": ImportMapping("'accounting.Account'", "'accounting.Account'"),
    "'accounting.Journal'": ImportMapping("'accounting.Journal'", "'accounting.Journal'"),
    "'apps.backup_manager.Backup'": ImportMapping("'apps.backup_manager.Backup'", "'apps.backup_manager.Backup'"),
    "'permissions.Permission'": ImportMapping("'permissions.Permission'", "'permissions.Permission'"),
    "'blockchain.Contract'": ImportMapping("'blockchain.Contract'", "'blockchain.Contract'"),
    "'ai_assistant.Assistant'": ImportMapping("'ai_assistant.Assistant'", "'ai_assistant.Assistant'"),
    "'seo.SeoSettings'": ImportMapping("'seo.SeoSettings'", "'seo.SeoSettings'"),
    "'virtual_company.VirtualCompany'": ImportMapping("'virtual_company.VirtualCompany'", "'virtual_company.VirtualCompany'"),
    "'analytics.Report'": ImportMapping("'analytics.Report'", "'analytics.Report'"),
    "'games.game_app.Game'": ImportMapping("'games.game_app.Game'", "'games.game_app.Game'"),
    "'games.ursina_game.Game'": ImportMapping("'games.ursina_game.Game'", "'games.ursina_game.Game'"),
}

def update_file(file_path: Path) -> bool:
    """Belirtilen dosyanın içeriğini update eder."""
    logger.info(f"Dosya işleniyor: {file_path}")
    
    try:
        # Dosya içeriğini oku
        content = file_path.read_text(encoding='utf-8')
        
        # Orjinal içeriği yedekle
        original_content = content
        
        # İmportları güncelle
        for mapping in IMPORT_MAPPINGS.values():
            content = content.replace(mapping.old, mapping.new)
        
        # Model referanslarını güncelle
        for mapping in MODEL_MAPPINGS.values():
            content = content.replace(mapping.old, mapping.new)
        
        # Eğer değişiklik yapıldıysa dosyayı kaydet
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Güncellendi: {file_path}")
            return True
        else:
            logger.info(f"⏩ Değişiklik yok: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Hata: {file_path} işlenirken bir sorun oluştu: {str(e)}")
        return False

def process_directory(directory_path: Path, exclude_dirs: Optional[List[str]] = None) -> Dict[str, int]:
    """Belirtilen dizindeki tüm Python dosyalarını işler."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    exclude_dirs = [directory_path / d for d in exclude_dirs]
    
    count = {
        'processed': 0,
        'updated': 0,
        'skipped': 0
    }
    
    def process_file(file_path: Path) -> None:
        """Tek bir dosyayı işle"""
        if file_path.suffix in ('.py', '.html', '.js', '.jsx', '.ts', '.tsx'):
            count['processed'] += 1
            if update_file(file_path):
                count['updated'] += 1
    
    # Dizini tara
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(directory_path):
            # Hariç tutulan dizinleri atla
            if any(Path(root).is_relative_to(excl) for excl in exclude_dirs):
                continue
            
            # Dosyaları işle
            for file in files:
                file_path = Path(root) / file
                executor.submit(process_file, file_path)
    
    return count

def main() -> None:
    """Ana fonksiyon"""
    try:
        # Base directory
        base_dir = Path(__file__).resolve().parent.parent
        
        # Hariç tutulacak dizinler
        exclude_dirs = [
            'venv',
            '.git',
            '__pycache__',
            'migrations',
            'static',
            'media',
            'logs'
        ]
        
        # Dizini işle
        count = process_directory(base_dir, exclude_dirs)
        
        # Sonuçları göster
        logger.info(f"\nİşlem tamamlandı:")
        logger.info(f"  Toplam işlenen dosya: {count['processed']}")
        logger.info(f"  Güncellenen dosya: {count['updated']}")
        logger.info(f"  Atlanan dosya: {count['skipped']}")
        
    except Exception as e:
        logger.error(f"İşlem sırasında bir hata oluştu: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 