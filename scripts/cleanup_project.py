# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Ana dizini temizleyen betik
"""
import os
import shutil
from pathlib import Path
import argparse

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Ana dizinde kalması gereken dosyalar ve klasörler
KEEP_FILES = [
    'manage.py',
    'Dockerfile',
    'docker-compose.yml',
    'requirements.txt',
    'README.md',
    '.env',
    '.env.example',
    '.gitignore',
    'apps',
    'config',
    'core',
    'templates',
    'static',
    'tests',
    'scripts',
    'media',
    '.git',
    'venv',
    '.venv',
    'node_modules',
    'locale',
    'staticfiles',
    'package.json',
    'package-lock.json',
    'pyrightconfig.json',
    'pytest.ini',
]

def list_removable_items():
    """Ana dizinde silinebilir öğeleri listele"""
    all_items = os.listdir(BASE_DIR)
    removable_items = [item for item in all_items if item not in KEEP_FILES]
    return removable_items

def create_backup_dir():
    """Yedek klasörü oluştur"""
    backup_dir = os.path.join(BASE_DIR, 'backups', 'old_structure')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_and_remove(items, backup_dir, dry_run=True):
    """Öğeleri yedekle ve sil"""
    for item in items:
        item_path = os.path.join(BASE_DIR, item)
        backup_path = os.path.join(backup_dir, item)
        
        if dry_run:
            print(f"[DRY RUN] {item} → {backup_path} taşınacak")
        else:
            try:
                if os.path.isdir(item_path):
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                    shutil.copytree(item_path, backup_path)
                    shutil.rmtree(item_path)
                else:
                    shutil.copy2(item_path, backup_path)
                    os.remove(item_path)
                print(f"[OK] {item} → {backup_path} taşındı")
            except Exception as e:
                print(f"[HATA] {item} öğesi taşınırken hata: {e}")

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Proje kök dizinini temizle.')
    parser.add_argument('--run', action='store_true', help='Gerçek silme işlemi yap (bu flag olmadan kuru çalışma yapar)')
    parser.add_argument('--auto', action='store_true', help='Otomatik olarak çalıştır, onay isteme')
    args = parser.parse_args()
    
    dry_run = not args.run
    
    print("=== FinAsis MVT Yapısı Temizlik İşlemi ===")
    if dry_run:
        print("NOT: Bu bir kuru çalışmadır. Gerçek silme işlemi yapılmayacak.")
        print("Gerçek silme için --run parametresi ekleyin.")
    
    removable_items = list_removable_items()
    
    if not removable_items:
        print("Silinecek öğe yok. Kök dizin temiz.")
        return
    
    print(f"\nSilinebilir {len(removable_items)} öğe bulundu:")
    for item in removable_items:
        print(f" - {item}")
    
    if dry_run:
        print("\nKuru çalışma bitiriliyor. Değişiklik yapılmadı.")
        return
    
    if not args.auto:
        confirm = input("\nBu öğeler yedeklenecek ve kök dizinden kaldırılacak. Devam etmek istiyor musunuz? (e/h): ")
        if confirm.lower() != 'e':
            print("İşlem iptal edildi.")
            return
    
    backup_dir = create_backup_dir()
    print(f"\nYedekleme dizini oluşturuldu: {backup_dir}")
    
    backup_and_remove(removable_items, backup_dir, dry_run=False)
    
    print("\nTemizlik işlemi tamamlandı!")
    print(f"Yedeklenen öğeler: {backup_dir}")

if __name__ == "__main__":
    main() 