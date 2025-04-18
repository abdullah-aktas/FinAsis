#!/usr/bin/env python
"""
İmport ifadelerini otomatik olarak güncelleyen script.
MVT dönüşümü sonrası eski import ifadelerini yeni yapıya uyarlayarak kodu düzeltir.
"""

import os
import re
import sys
from pathlib import Path

# İmport eşleştirme haritası - temel modüller
IMPORT_MAPPINGS = {
    # CRM ve Customers modül eşleştirmeleri
    'from apps.crm import': 'from apps.crm import',
    'from apps.crm import': 'from apps.crm import',
    'from apps.crm.models import': 'from apps.crm.models import',
    'from apps.crm.views import': 'from apps.crm.views import',
    'from apps.crm.serializers import': 'from apps.crm.serializers import',
    'from apps.crm.forms import': 'from apps.crm.forms import',
    
    # HR ve Users modül eşleştirmeleri
    'from apps.hr_management import': 'from apps.hr_management import',
    'from apps.hr_management.models import': 'from apps.hr_management.models import',
    'from apps.hr_management.views import': 'from apps.hr_management.views import',
    'from apps.hr_management.serializers import': 'from apps.hr_management.serializers import',
    'from apps.hr_management.forms import': 'from apps.hr_management.forms import',
    
    # Stok ve Varlık Yönetimi eşleştirmeleri
    'from apps.stock_management import': 'from apps.stock_management import',
    'from apps.stock_management.models import': 'from apps.stock_management.models import',
    'from apps.stock_management import': 'from apps.stock_management import',
    'from apps.stock_management.models import': 'from apps.stock_management.models import',
    
    # Entegrasyonlar
    'from apps.integrations.efatura import': 'from apps.integrations.efatura import',
    'from apps.integrations.efatura.models import': 'from apps.integrations.efatura.models import',
    'from apps.integrations.bank_integration import': 'from apps.integrations.bank_integration import',
    'from apps.integrations.bank_integration.models import': 'from apps.integrations.bank_integration.models import',
    'from apps.integrations.services import': 'from apps.integrations.services import',
    'from apps.integrations.services.models import': 'from apps.integrations.services.models import',
    'from apps.integrations.external import': 'from apps.integrations.external import',
    'from apps.integrations.external.models import': 'from apps.integrations.external.models import',
    
    # Diğer modüller
    'from apps.accounting import': 'from apps.accounting import',
    'from apps.accounting.models import': 'from apps.accounting.models import',
    'from apps.backup_manager import': 'from apps.backup_manager import',
    'from apps.permissions import': 'from apps.permissions import',
    'from apps.blockchain import': 'from apps.blockchain import',
    'from apps.ai_assistant import': 'from apps.ai_assistant import',
    'from apps.seo import': 'from apps.seo import',
    'from apps.virtual_company import': 'from apps.virtual_company import',
    'from apps.analytics import': 'from apps.analytics import',
    
    # Oyun modülleri 
    'from apps.games.game_app import': 'from apps.games.game_app import',
    'from apps.games.ursina_game import': 'from apps.games.ursina_game import',
    
    # Doğrudan import ifadeleri
    'import apps.crm': 'import apps.crm',
    'import apps.crm': 'import apps.crm',
    'import apps.hr_management': 'import apps.hr_management',
    'import apps.stock_management': 'import apps.stock_management',
    'import apps.stock_management': 'import apps.stock_management',
    'import apps.integrations.efatura': 'import apps.integrations.efatura',
    'import apps.integrations.bank_integration': 'import apps.integrations.bank_integration',
    'import apps.integrations.services': 'import apps.integrations.services',
    'import apps.integrations.external': 'import apps.integrations.external',
    'import apps.accounting': 'import apps.accounting',
    'import apps.backup_manager': 'import apps.backup_manager',
    'import apps.permissions': 'import apps.permissions',
    'import apps.blockchain': 'import apps.blockchain',
    'import apps.ai_assistant': 'import apps.ai_assistant',
    'import apps.seo': 'import apps.seo',
    'import apps.virtual_company': 'import apps.virtual_company',
    'import apps.analytics': 'import apps.analytics',
    'import apps.games.game_app': 'import apps.games.game_app',
    'import apps.games.ursina_game': 'import apps.games.ursina_game',
}

# ForeignKey referansları için model eşleştirme haritası
MODEL_MAPPINGS = {
    # String'li model referansları (ForeignKey, ManyToMany vs.)
    "'apps.crm.Customer'": "'apps.crm.Customer'",
    "'apps.hr_management.User'": "'apps.hr_management.User'",
    "'apps.hr_management.Profile'": "'apps.hr_management.Profile'",
    "'apps.stock_management.Asset'": "'apps.stock_management.Asset'",
    "'apps.stock_management.Product'": "'apps.stock_management.Product'",
    "'apps.stock_management.Stock'": "'apps.stock_management.Stock'",
    "'apps.integrations.efatura.EInvoice'": "'apps.integrations.efatura.EInvoice'",
    "'apps.integrations.bank_integration.BankAccount'": "'apps.integrations.bank_integration.BankAccount'",
    "'apps.integrations.services.Service'": "'apps.integrations.services.Service'",
    "'apps.integrations.external.Integration'": "'apps.integrations.external.Integration'",
    "'apps.accounting.Account'": "'apps.accounting.Account'",
    "'apps.accounting.Journal'": "'apps.accounting.Journal'",
    "'apps.backup_manager.Backup'": "'apps.backup_manager.Backup'",
    "'apps.permissions.Permission'": "'apps.permissions.Permission'",
    "'apps.blockchain.Contract'": "'apps.blockchain.Contract'",
    "'apps.ai_assistant.Assistant'": "'apps.ai_assistant.Assistant'",
    "'apps.seo.SeoSettings'": "'apps.seo.SeoSettings'",
    "'apps.virtual_company.VirtualCompany'": "'apps.virtual_company.VirtualCompany'",
    "'apps.analytics.Report'": "'apps.analytics.Report'",
    "'apps.games.game_app.Game'": "'apps.games.game_app.Game'",
    "'apps.games.ursina_game.Game'": "'apps.games.ursina_game.Game'",
    
    # Çift tırnaklı versiyonları
    '"apps.crm.Customer"': '"apps.crm.Customer"',
    '"apps.hr_management.User"': '"apps.hr_management.User"',
    '"apps.hr_management.Profile"': '"apps.hr_management.Profile"',
    '"apps.stock_management.Asset"': '"apps.stock_management.Asset"',
    '"apps.stock_management.Product"': '"apps.stock_management.Product"',
    '"apps.stock_management.Stock"': '"apps.stock_management.Stock"',
    '"apps.integrations.efatura.EInvoice"': '"apps.integrations.efatura.EInvoice"',
    '"apps.integrations.bank_integration.BankAccount"': '"apps.integrations.bank_integration.BankAccount"',
    '"apps.integrations.services.Service"': '"apps.integrations.services.Service"',
    '"apps.integrations.external.Integration"': '"apps.integrations.external.Integration"',
    '"apps.accounting.Account"': '"apps.accounting.Account"',
    '"apps.accounting.Journal"': '"apps.accounting.Journal"',
    '"apps.backup_manager.Backup"': '"apps.backup_manager.Backup"',
    '"apps.permissions.Permission"': '"apps.permissions.Permission"',
    '"apps.blockchain.Contract"': '"apps.blockchain.Contract"',
    '"apps.ai_assistant.Assistant"': '"apps.ai_assistant.Assistant"',
    '"apps.seo.SeoSettings"': '"apps.seo.SeoSettings"',
    '"apps.virtual_company.VirtualCompany"': '"apps.virtual_company.VirtualCompany"',
    '"apps.analytics.Report"': '"apps.analytics.Report"',
    '"apps.games.game_app.Game"': '"apps.games.game_app.Game"',
    '"apps.games.ursina_game.Game"': '"apps.games.ursina_game.Game"',
    
    # Noktasız alt paketler 
    "'apps.crm.Customer'": "'apps.crm.Customer'",
    "'apps.hr_management.User'": "'apps.hr_management.User'",
}

# URL eşleştirme haritası 
URL_MAPPINGS = {
    # URL include eşleştirmeleri
    "include('apps.crm.": "include('apps.crm.",
    "include('apps.hr_management.": "include('apps.hr_management.",
    "include('apps.stock_management.": "include('apps.stock_management.",
    "include('apps.stock_management.": "include('apps.stock_management.",
    "include('apps.integrations.efatura.": "include('apps.integrations.efatura.",
    "include('apps.integrations.bank_integration.": "include('apps.integrations.bank_integration.",
    "include('apps.integrations.services.": "include('apps.integrations.services.",
    "include('apps.integrations.external.": "include('apps.integrations.external.",
    "include('apps.accounting.": "include('apps.accounting.",
    "include('apps.backup_manager.": "include('apps.backup_manager.",
    "include('apps.permissions.": "include('apps.permissions.",
    "include('apps.blockchain.": "include('apps.blockchain.",
    "include('apps.ai_assistant.": "include('apps.ai_assistant.",
    "include('apps.seo.": "include('apps.seo.",
    "include('apps.virtual_company.": "include('apps.virtual_company.",
    "include('apps.analytics.": "include('apps.analytics.",
    "include('apps.games.game_app.": "include('apps.games.game_app.",
    "include('apps.games.ursina_game.": "include('apps.games.ursina_game.",
    
    # Path route eşleştirmeleri
    "path('customers/": "path('customers/",  # Bu değişmeyecek - URL yapısını koruyoruz
    "path('users/": "path('users/",  # Bu değişmeyecek - URL yapısını koruyoruz
    
    # Namespace eşleştirmeleri  
    "namespace='crm'": "namespace='crm'",
    "namespace='hr_management'": "namespace='hr_management'",
    "namespace='stock_management'": "namespace='stock_management'",
    "namespace='stock_management'": "namespace='stock_management'",
}

# Template eşleştirme haritası
TEMPLATE_MAPPINGS = {
    "{% extends 'crm/": "{% extends 'crm/",
    "{% include 'crm/": "{% include 'crm/",
    "{% extends 'hr_management/": "{% extends 'hr_management/",
    "{% include 'hr_management/": "{% include 'hr_management/",
    "{% extends 'stock_management/": "{% extends 'stock_management/",
    "{% include 'stock_management/": "{% include 'stock_management/",
    "{% extends 'stock_management/": "{% extends 'stock_management/",
    "{% include 'stock_management/": "{% include 'stock_management/",
}

def update_file(file_path):
    """Belirtilen dosyanın içeriğini update eder."""
    print(f"Dosya işleniyor: {file_path}")
    
    # Dosya içeriğini oku
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Orjinal içeriği yedekle
    original_content = content
    
    # İmportları güncelle
    for old_import, new_import in IMPORT_MAPPINGS.items():
        content = content.replace(old_import, new_import)
    
    # Model referanslarını güncelle
    for old_model, new_model in MODEL_MAPPINGS.items():
        content = content.replace(old_model, new_model)
    
    # URL referanslarını güncelle
    for old_url, new_url in URL_MAPPINGS.items():
        content = content.replace(old_url, new_url)
    
    # Template referanslarını güncelle
    if file_path.endswith('.html') or file_path.endswith('.py'):
        for old_template, new_template in TEMPLATE_MAPPINGS.items():
            content = content.replace(old_template, new_template)
    
    # Eğer değişiklik yapıldıysa dosyayı kaydet
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Güncellendi: {file_path}")
        return True
    else:
        print(f"⏩ Değişiklik yok: {file_path}")
        return False

def process_directory(directory_path, exclude_dirs=None):
    """Belirtilen dizindeki tüm Python dosyalarını işler."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    exclude_dirs = [os.path.normpath(os.path.join(directory_path, d)) for d in exclude_dirs]
    
    count = {
        'processed': 0,
        'updated': 0,
        'skipped': 0
    }
    
    for root, dirs, files in os.walk(directory_path):
        # Hariç tutulan dizinleri atla
        if any(os.path.normpath(root).startswith(excl) for excl in exclude_dirs):
            continue
        
        for file in files:
            # Python, HTML, JavaScript ve diğer template dosyalarını işle
            if file.endswith(('.py', '.html', '.js', '.jsx', '.ts', '.tsx')):
                file_path = os.path.join(root, file)
                count['processed'] += 1
                
                try:
                    if update_file(file_path):
                        count['updated'] += 1
                except Exception as e:
                    print(f"❌ Hata: {file_path} işlenirken bir sorun oluştu: {str(e)}")
                    count['skipped'] += 1
    
    return count

def main():
    """Ana program akışı."""
    # Komut satırı argümanlarını işle
    if len(sys.argv) < 2:
        print("Kullanım: python update_imports.py <dizin_yolu> [hariç_tutulan_dizinler...]")
        print("Örnek: python update_imports.py . venv node_modules")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    exclude_dirs = sys.argv[2:] if len(sys.argv) > 2 else ['venv', 'node_modules', '.git', '__pycache__', 'env', '.venv', 'migrations']
    
    print(f"İmport güncelleme işlemi başlatılıyor...")
    print(f"Dizin: {directory_path}")
    print(f"Hariç tutulan dizinler: {exclude_dirs}")
    
    confirmation = input("Devam etmek istiyor musunuz? (e/h): ")
    if confirmation.lower() != 'e':
        print("İşlem iptal edildi.")
        sys.exit(0)
    
    count = process_directory(directory_path, exclude_dirs)
    
    print("\nİşlem tamamlandı!")
    print(f"İşlenen dosyalar: {count['processed']}")
    print(f"Güncellenen dosyalar: {count['updated']}")
    print(f"Atlanılan dosyalar: {count['skipped']}")

if __name__ == "__main__":
    main() 