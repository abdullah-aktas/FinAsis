# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Proje yapısını MVT mimarisine dönüştüren script
"""
import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Taşınacak uygulamalar
APPS_TO_MOVE = {
    'crm': 'apps/crm',
    'stock_management': 'apps/stock_management',
    'hr_management': 'apps/hr_management',
    'check_management': 'apps/checks',
    'customer_management': 'apps/customers',
    'permissions': 'apps/permissions',
    'game_app': 'apps/games/game_app',
    'ursina_game': 'apps/games/ursina_game',
    'efatura': 'apps/integrations/efatura',
    'bank_integration': 'apps/integrations/bank_integration',
    'external_integrations': 'apps/integrations/external',
    'ext_services': 'apps/integrations/services',
    'asset_management': 'apps/assets',
    'blockchain': 'apps/blockchain',
    'ai_assistant': 'apps/ai_assistant',
    'seo_management': 'apps/seo',
    'virtual_company': 'apps/virtual_company',
}

def ensure_directory(path):
    """Klasörün var olduğundan emin ol"""
    os.makedirs(path, exist_ok=True)

def copy_app(source, destination):
    """Bir uygulamayı kaynak konumundan hedef konumuna kopyala"""
    source_path = os.path.join(BASE_DIR, source)
    destination_path = os.path.join(BASE_DIR, destination)
    
    if not os.path.exists(source_path):
        print(f"Kaynak bulunamadı: {source_path}")
        return False
        
    ensure_directory(destination_path)
    
    # Python dosyalarını ve klasörleri kopyala
    for item in os.listdir(source_path):
        source_item = os.path.join(source_path, item)
        dest_item = os.path.join(destination_path, item)
        
        if os.path.isdir(source_item):
            shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
        else:
            shutil.copy2(source_item, dest_item)
    
    print(f"{source} → {destination} taşındı")
    return True

def create_init_files():
    """Tüm gerekli klasörlerde __init__.py dosyaları oluştur"""
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'apps')):
        if '__init__.py' not in files:
            with open(os.path.join(root, '__init__.py'), 'w') as f:
                f.write('# MVT yapısı için oluşturuldu\n')

def update_imports():
    """Import ifadelerini güncelle (otomatik olarak çalışmayabilir, manuel kontrol gerektirebilir)"""
    print("ÖNEMLİ: Import ifadelerini güncellemek için kod editörünüzün arama ve değiştirme özelliğini kullanın")
    print("Örneğin, 'from apps.crm import' → 'from apps.crm import'")

def main():
    """Ana fonksiyon"""
    print("MVT Yapısına Dönüşüm Başlatılıyor...")
    
    # Uygulamaları taşı
    for source, destination in APPS_TO_MOVE.items():
        copy_app(source, destination)
    
    # İlgili __init__.py dosyalarını oluştur
    create_init_files()
    
    # İmport ifadeleri hakkında bilgi ver
    update_imports()
    
    print("MVT Yapısına Dönüşüm Tamamlandı! Lütfen import ifadelerini manuel olarak kontrol edin.")

if __name__ == "__main__":
    main() 