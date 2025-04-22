#!/usr/bin/env python
"""
apps.py dosyalarındaki name özelliğini yeni MVT yapısına uygun olarak düzenleyen betik
"""
import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Uygulamalar ve yeni yolları
APP_PATHS = {
    'crm': 'apps.crm',
    'stock_management': 'apps.stock_management',
    'hr_management': 'apps.hr_management',
    'check_management': 'apps.checks',
    'customer_management': 'apps.customers',
    'permissions': 'apps.permissions',
    'blockchain': 'apps.blockchain',
    'ai_assistant': 'apps.ai_assistant',
    'seo_management': 'apps.seo',
    'virtual_company': 'apps.virtual_company',
    'asset_management': 'apps.assets',
    'accounting': 'apps.accounting',
    'users': 'apps.users',
    'backup_manager': 'apps.backup_manager',
    'game_app': 'games.game_app',
    'ursina_game': 'games.ursina_game',
    'efatura': 'integrations.efatura',
    'bank_integration': 'integrations.bank_integration',
    'external_integrations': 'integrations.external',
    'ext_services': 'integrations.services',
    'accounts': 'apps.accounts',
}

def fix_apps_py(app_path, new_app_name):
    """apps.py dosyasındaki name alanını güncelle"""
    app_file = os.path.join(BASE_DIR, app_path, 'apps.py')
    if not os.path.exists(app_file):
        print(f"Dosya bulunamadı: {app_file}")
        return False

    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # name değerini güncelle
        pattern = r"(name\s*=\s*['\"])([^'\"]+)(['\"])"
        
        # Eşleşmeyi bul ve 'name' satırını güncelle
        match = re.search(pattern, content)
        if match:
            current_name = match.group(2)
            print(f"İnceleniyor: {app_file} (mevcut ad: {current_name}, yeni ad: {new_app_name})")
            
            if current_name != new_app_name:
                updated_content = re.sub(pattern, f"\\1{new_app_name}\\3", content)
                
                # Signals importunu varsa güncelle
                import_pattern = r"(import\s+)([^\.]+)(\.signals)"
                updated_content = re.sub(import_pattern, f"\\1{new_app_name}\\3", updated_content)
                
                with open(app_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  ✅ Güncellendi: {app_file}")
                return True
            else:
                print(f"  ⏭️ Zaten güncel: {app_file}")
        else:
            print(f"  ❌ 'name' alanı bulunamadı: {app_file}")
        
        return False
    except Exception as e:
        print(f"  ❌ Hata: {app_file} işlenirken sorun oluştu: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("=== AppConfig İsim Güncellemesi ===")
    
    updated_files = []
    for old_app, new_app in APP_PATHS.items():
        app_path = old_app.replace('.', '/')
        new_app_path = f"apps/{app_path}"
        print(f"Kontrol ediliyor: {old_app} -> {new_app_path}")
        
        if os.path.exists(os.path.join(BASE_DIR, new_app_path)):
            if fix_apps_py(new_app_path, new_app):
                updated_files.append(new_app_path)
        else:
            print(f"Klasör bulunamadı: {new_app_path}")

    print(f"\nToplam {len(updated_files)} apps.py dosyası güncellendi.")
    
    if updated_files:
        print("\nGüncellenen dosyalar:")
        for file in updated_files:
            print(f" - {file}/apps.py")
    
    print("\nGüncelleme tamamlandı!")

if __name__ == "__main__":
    main() 