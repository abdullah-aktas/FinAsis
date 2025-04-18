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
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Modül birleştirmeleri - yeni değer, tam olarak yeni modül yolunu içermelidir
MODULE_MERGES = {
    # CRM ve Customers modülleri birleştirildi
    'customers': 'apps.crm',
    'customer_management': 'apps.crm',
    
    # User ve HR modülleri birleştirildi
    'users': 'apps.hr_management',
    
    # Inventory, Stock ve Assets modülleri birleştirildi
    'inventory': 'apps.stock_management',
    'assets': 'apps.stock_management',
    'asset_management': 'apps.stock_management',
    
    # Integrations modülü altında toplanan alt modüller
    'efatura': 'apps.integrations.efatura',
    'bank_integration': 'apps.integrations.bank_integration',
    'external_integrations': 'apps.integrations.external',
    'ext_services': 'apps.integrations.services',
    
    # Diğer modül eşleştirmeleri
    'backup_manager': 'apps.backup_manager',
    'permissions': 'apps.permissions',
    'blockchain': 'apps.blockchain',
    'ai_assistant': 'apps.ai_assistant',
    'seo_management': 'apps.seo',
    'virtual_company': 'apps.virtual_company',
    'analytics': 'apps.analytics',
    'game_app': 'apps.games.game_app',
    'ursina_game': 'apps.games.ursina_game',
    'accounting': 'apps.accounting',
    'finance': 'apps.finance',
    'finance.accounting': 'apps.finance.accounting',
    'finance.banking': 'apps.finance.banking',
    'finance.checks': 'apps.finance.checks',
    'finance.einvoice': 'apps.finance.einvoice',
    'checks': 'apps.checks',
}

# Migrasyonları yedekle
def backup_migrations():
    """Mevcut migrasyonları yedekle"""
    backup_dir = os.path.join(BASE_DIR, 'scripts', 'migration_backups', datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Migrasyonlar {backup_dir} dizinine yedekleniyor...")
    
    # Ana modülleri ve alt modülleri tara
    for old_module, new_module in MODULE_MERGES.items():
        module_path = os.path.join(BASE_DIR, old_module.replace('.', os.path.sep))
        migrations_path = os.path.join(module_path, 'migrations')
        
        if os.path.exists(migrations_path):
            module_backup_dir = os.path.join(backup_dir, old_module.replace('.', '_'))
            os.makedirs(module_backup_dir, exist_ok=True)
            
            # Migrasyonları kopyala
            for file in os.listdir(migrations_path):
                if file.endswith('.py'):
                    src = os.path.join(migrations_path, file)
                    dst = os.path.join(module_backup_dir, file)
                    shutil.copy2(src, dst)
                    print(f"  Yedeklendi: {src} -> {dst}")
    
    # apps altındaki modülleri de yedekle
    apps_dir = os.path.join(BASE_DIR, 'apps')
    if os.path.exists(apps_dir):
        for module in os.listdir(apps_dir):
            module_path = os.path.join(apps_dir, module)
            if os.path.isdir(module_path):
                migrations_path = os.path.join(module_path, 'migrations')
                if os.path.exists(migrations_path):
                    module_backup_dir = os.path.join(backup_dir, f"apps_{module}")
                    os.makedirs(module_backup_dir, exist_ok=True)
                    
                    # Migrasyonları kopyala
                    for file in os.listdir(migrations_path):
                        if file.endswith('.py'):
                            src = os.path.join(migrations_path, file)
                            dst = os.path.join(module_backup_dir, file)
                            shutil.copy2(src, dst)
                            print(f"  Yedeklendi: {src} -> {dst}")
                
                # Alt modüller varsa onları da yedekle
                for subdir in os.listdir(module_path):
                    submodule_path = os.path.join(module_path, subdir)
                    if os.path.isdir(submodule_path):
                        migrations_path = os.path.join(submodule_path, 'migrations')
                        if os.path.exists(migrations_path):
                            module_backup_dir = os.path.join(backup_dir, f"apps_{module}_{subdir}")
                            os.makedirs(module_backup_dir, exist_ok=True)
                            
                            # Migrasyonları kopyala
                            for file in os.listdir(migrations_path):
                                if file.endswith('.py'):
                                    src = os.path.join(migrations_path, file)
                                    dst = os.path.join(module_backup_dir, file)
                                    shutil.copy2(src, dst)
                                    print(f"  Yedeklendi: {src} -> {dst}")
    
    return backup_dir

# Migrasyon dosyalarını temizle
def clean_migrations():
    """Migrasyon dosyalarını temizle - eski modüllerin migrasyonlarını temizle"""
    for old_module, new_module in MODULE_MERGES.items():
        if '.' in old_module:  # Alt modüller için path doğru oluştur
            parts = old_module.split('.')
            old_module_path = os.path.join(BASE_DIR, *parts)
        else:
            old_module_path = os.path.join(BASE_DIR, old_module)
        
        old_migrations_path = os.path.join(old_module_path, 'migrations')
        
        if os.path.exists(old_migrations_path):
            # Sadece __init__.py'yi bırak, diğer migrasyonları sil
            for file in os.listdir(old_migrations_path):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(old_migrations_path, file)
                    try:
                        os.remove(file_path)
                        print(f"Silindi: {file_path}")
                    except Exception as e:
                        print(f"Hata: {file_path} silinemedi: {e}")

# Migrasyonları güncelle
def update_migrations():
    """Model referans yollarını ve import ifadelerini güncelle"""
    # Yeni modül yollarına göre migrasyonları güncelle
    for old_module, new_module in MODULE_MERGES.items():
        # Yeni modül yolu
        if '.' in new_module:  # Alt modül için
            parts = new_module.split('.')
            new_module_path = os.path.join(BASE_DIR, *parts)
        else:
            new_module_path = os.path.join(BASE_DIR, new_module)
        
        # Yeni modülün migrations klasörü
        new_migrations_path = os.path.join(new_module_path, 'migrations')
        
        if os.path.exists(new_migrations_path):
            for file in os.listdir(new_migrations_path):
                if file.endswith('.py') and file != '__init__.py':
                    migration_file = os.path.join(new_migrations_path, file)
                    update_migration_file(migration_file, old_module, new_module)

def update_migration_file(file_path, old_module, new_module):
    """Migrasyon dosyasındaki referansları güncelle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Model import yollarını güncelle
        old_module_dotted = old_module.replace('.', r'\.')
        pattern = rf"from\s+{old_module_dotted}\.models\s+import"
        replacement = f"from {new_module}.models import"
        content = re.sub(pattern, replacement, content)
        
        # ForeignKey ve model referanslarını güncelle
        pattern = rf"to\s*=\s*['\"]({old_module_dotted})\.(\w+)['\"]"
        replacement = f"to=\'{new_module}.\\2\'"
        content = re.sub(pattern, replacement, content)
        
        # Migrasyon bağımlılıklarını güncelle
        pattern = rf"dependencies\s*=\s*\[\s*\(?['\"]({old_module_dotted})['\"]"
        replacement = f"dependencies = [('{new_module}'"
        content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Güncellendi: {file_path}")
    except Exception as e:
        print(f"Hata: {file_path} dosyası güncellenirken bir sorun oluştu: {e}")

# Fake migrasyon komutu oluştur
def create_fake_migration_script():
    """Migrasyon sorunlarını çözmek için fake migrasyon betiği oluştur"""
    script_path = os.path.join(BASE_DIR, 'scripts', 'apply_migrations.py')
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python
"""
Migration uygulama programı.
Bu script, modül birleştirme işleminin ardından migrasyonları düzgün bir şekilde uygulamak için kullanılır.
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Django ayarlarını yükleme
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.conf import settings
from django.core.management import call_command

# Modül birleştirme haritası
MODULE_MERGES = {
    'customers': 'crm',
    'users': 'hr_management',
    'inventory': 'stock_management',
    'assets': 'stock_management',
    'efatura': 'integrations.efatura',
    'bank_integration': 'integrations.bank_integration',
    'ext_services': 'integrations.services',
    'external_integrations': 'integrations.external',
}

def log(message):
    """Log mesajını zaman damgası ile ekrana yazdır."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def apply_migrations_with_fake_initial():
    """Tüm modüller için --fake-initial kullanarak migrasyonları uygular."""
    log("Migrasyonlar uygulanıyor (fake-initial ile)...")
    
    apps_dir = os.path.join(settings.BASE_DIR, 'apps')
    
    # Önce Ana Uygulamalar
    primary_apps = ['accounting', 'crm', 'hr_management', 'stock_management', 'checks', 'permissions']
    for app in primary_apps:
        if os.path.exists(os.path.join(apps_dir, app, 'migrations')):
            try:
                log(f"'{app}' uygulaması için migrasyonlar uygulanıyor...")
                call_command('migrate', f'apps.{app}', '--fake-initial')
                log(f"'{app}' migrasyonları başarıyla uygulandı.")
            except Exception as e:
                log(f"HATA: '{app}' migrasyonlarını uygularken bir sorun oluştu: {str(e)}")
    
    # Sonra Entegrasyon Uygulamaları
    integration_apps = ['integrations.efatura', 'integrations.bank_integration', 
                        'integrations.services', 'integrations.external']
    for app in integration_apps:
        if os.path.exists(os.path.join(apps_dir, app.replace('.', '/'), 'migrations')):
            try:
                log(f"'{app}' uygulaması için migrasyonlar uygulanıyor...")
                call_command('migrate', f'apps.{app}', '--fake-initial')
                log(f"'{app}' migrasyonları başarıyla uygulandı.")
            except Exception as e:
                log(f"HATA: '{app}' migrasyonlarını uygularken bir sorun oluştu: {str(e)}")

    # Son olarak Django dahili uygulamaları
    log("Django dahili uygulamaları için migrasyonlar uygulanıyor...")
    call_command('migrate', 'admin')
    call_command('migrate', 'auth')
    call_command('migrate', 'contenttypes')
    call_command('migrate', 'sessions')
    log("Django dahili uygulama migrasyonları başarıyla uygulandı.")

def perform_full_migration():
    """Tüm sistemi migrate eder."""
    log("Tüm migrasyonlar uygulanıyor...")
    try:
        call_command('migrate')
        log("Tüm migrasyonlar başarıyla uygulandı.")
        return True
    except Exception as e:
        log(f"HATA: Migrasyonlar uygulanırken bir sorun oluştu: {str(e)}")
        return False

def check_for_issues():
    """Django check komutunu çalıştırarak olası sorunları kontrol eder."""
    log("Sistem sorunları kontrol ediliyor...")
    try:
        call_command('check')
        log("Sistem kontrolleri başarıyla tamamlandı.")
        return True
    except Exception as e:
        log(f"HATA: Sistem kontrolünde sorunlar tespit edildi: {str(e)}")
        return False

def main():
    """Ana program akışı."""
    log("MVT Dönüşümü sonrası migrasyon uygulama işlemi başlatılıyor...")
    
    # Sistem kontrolü
    if not check_for_issues():
        log("UYARI: Devam etmeden önce yukarıdaki sorunları çözün.")
        return

    # Kullanıcı onayı
    confirmation = input("Bu işlem migrasyon durumunu değiştirecektir. Devam etmek istiyor musunuz? (e/h): ")
    if confirmation.lower() != 'e':
        log("İşlem kullanıcı tarafından iptal edildi.")
        return

    # İlk olarak fake-initial ile migrasyon uygula
    apply_migrations_with_fake_initial()
    
    # Tüm sistemi migrate et
    perform_full_migration()
    
    log("İşlem tamamlandı. Veritabanı yapısını ve uygulama işlevselliğini kontrol edin.")

if __name__ == "__main__":
    main()
""")
    
    print(f"Migrasyon uygulama betiği oluşturuldu: {script_path}")
    
    # Windows için .bat, Unix için .sh dosyası oluştur
    if os.name == 'nt':
        batch_path = os.path.join(BASE_DIR, 'scripts', 'apply_migrations.bat')
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write('@echo off\ncd "%~dp0.."\npython scripts/apply_migrations.py\npause')
        print(f"Windows batch dosyası oluşturuldu: {batch_path}")
    else:
        shell_path = os.path.join(BASE_DIR, 'scripts', 'apply_migrations.sh')
        with open(shell_path, 'w', encoding='utf-8') as f:
            f.write('#!/bin/bash\ncd "$(dirname "$0")/.."\npython scripts/apply_migrations.py')
        os.chmod(shell_path, 0o755)
        print(f"Unix shell betiği oluşturuldu: {shell_path}")

def main():
    """Ana fonksiyon"""
    print("=== MVT Migrasyon Düzeltici ===")
    
    # Onay al
    response = input("Bu işlem mevcut migrasyon dosyalarını düzenleyecek ve yedekleyecektir. Devam etmek istiyor musunuz? (e/h): ")
    if response.lower() != 'e':
        print("İşlem iptal edildi.")
        return
    
    # Yedekle
    backup_dir = backup_migrations()
    
    # Temizle
    clean_migrations()
    
    # Güncelle
    update_migrations()
    
    # Fake migrasyon betiği oluştur
    create_fake_migration_script()
    
    print("\nMigrasyon düzeltme işlemi tamamlandı!")
    print(f"Migrasyonların yedeği: {backup_dir}")
    print("Sonraki adım olarak şu komutları çalıştırın:")
    print("  1. python manage.py makemigrations")
    print("  2. python scripts/apply_migrations.py")

if __name__ == "__main__":
    main()