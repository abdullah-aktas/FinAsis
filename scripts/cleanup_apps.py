#!/usr/bin/env python
"""
Apps dizinini temizleyen betik
"""
import os
import shutil
from pathlib import Path
import argparse

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Silinecek veya birleştirilecek gereksiz klasörler
APPS_TO_REMOVE = [
    'apps/inventory',
    'apps/game',
    'apps/integration',
    'apps/customers',
    'apps/company',
    'apps/docs',
]

def ensure_backup_dir():
    """Yedek klasörü oluştur"""
    backup_dir = os.path.join(BASE_DIR, 'backups', 'old_apps')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_and_remove(items, backup_dir, dry_run=True):
    """Öğeleri yedekle ve sil"""
    for item in items:
        item_path = os.path.join(BASE_DIR, item)
        backup_path = os.path.join(backup_dir, os.path.basename(item))
        
        if not os.path.exists(item_path):
            print(f"[UYARI] {item} bulunamadı, işlem yapılmadı.")
            continue
        
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
    parser = argparse.ArgumentParser(description='Apps dizinini temizle.')
    parser.add_argument('--run', action='store_true', help='Gerçek silme işlemi yap (bu flag olmadan kuru çalışma yapar)')
    args = parser.parse_args()
    
    dry_run = not args.run
    
    print("=== FinAsis Apps Dizini Temizlik İşlemi ===")
    if dry_run:
        print("NOT: Bu bir kuru çalışmadır. Gerçek silme işlemi yapılmayacak.")
        print("Gerçek silme için --run parametresi ekleyin.")
    
    print(f"\nSilinecek {len(APPS_TO_REMOVE)} öğe:")
    for item in APPS_TO_REMOVE:
        print(f" - {item}")
    
    if dry_run:
        print("\nKuru çalışma bitiriliyor. Değişiklik yapılmadı.")
        return
    
    backup_dir = ensure_backup_dir()
    print(f"\nYedekleme dizini oluşturuldu: {backup_dir}")
    
    backup_and_remove(APPS_TO_REMOVE, backup_dir, dry_run=False)
    
    print("\nTemizlik işlemi tamamlandı!")
    print(f"Yedeklenen öğeler: {backup_dir}")

if __name__ == "__main__":
    main() 