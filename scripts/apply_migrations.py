#!/usr/bin/env python
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