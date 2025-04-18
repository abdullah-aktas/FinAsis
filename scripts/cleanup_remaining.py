#!/usr/bin/env python
"""
Ana dizinde kalan gereksiz klasör ve dosyaları temizleyen betik
"""
import os
import shutil
from pathlib import Path
import argparse

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Ana dizinde kaldırılacak dosya ve klasörler
ITEMS_TO_REMOVE = [
    'integrations',
    'permissions',
    'game_app',
    'hr_management',
    'stock_management',
    'inventory',
    'ursina_game',
    'users',
    'frontend',
    'seo_management',
    'virtual_company',
    'reporting',
    'game.py',
    'tatus',
    'FinasisDesktop',
    'nginx',
    'PostgreSQL',
    'POSTGRES_SETUP.md',
    'setup_postgres.ps1',
    'setup_postgres.sh',
]

def ensure_backup_dir():
    """Yedek klasörü oluştur"""
    backup_dir = os.path.join(BASE_DIR, 'backups', 'remaining_cleanup')
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
    parser = argparse.ArgumentParser(description='Ana dizindeki kalan gereksiz dosya ve klasörleri temizle.')
    parser.add_argument('--run', action='store_true', help='Gerçek silme işlemi yap (bu flag olmadan kuru çalışma yapar)')
    args = parser.parse_args()
    
    dry_run = not args.run
    
    print("=== FinAsis Ana Dizin Son Temizlik ===")
    if dry_run:
        print("NOT: Bu bir kuru çalışmadır. Gerçek silme işlemi yapılmayacak.")
        print("Gerçek silme için --run parametresi ekleyin.")
    
    # Mevcut olan öğeleri filtrele
    existing_items = []
    for item in ITEMS_TO_REMOVE:
        if os.path.exists(os.path.join(BASE_DIR, item)):
            existing_items.append(item)
    
    if not existing_items:
        print("Silinecek öğe yok. Ana dizin temiz.")
        return
    
    print(f"\nSilinecek {len(existing_items)} öğe:")
    for item in existing_items:
        print(f" - {item}")
    
    if dry_run:
        print("\nKuru çalışma bitiriliyor. Değişiklik yapılmadı.")
        return
    
    backup_dir = ensure_backup_dir()
    print(f"\nYedekleme dizini oluşturuldu: {backup_dir}")
    
    backup_and_remove(existing_items, backup_dir, dry_run=False)
    
    print("\nTemizlik işlemi tamamlandı!")
    print(f"Yedeklenen öğeler: {backup_dir}")

if __name__ == "__main__":
    main() 