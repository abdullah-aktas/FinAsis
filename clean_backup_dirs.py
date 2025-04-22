#!/usr/bin/env python
"""
Bu script, taşıma işlemi sonrası oluşan yedek dizinlerini temizler.
"""
import os
import shutil
from pathlib import Path
import time

# Ana dizin
BASE_DIR = Path(__file__).resolve().parent

def backup_backup_dirs():
    """
    Yedek dizinlerinin bir yedeğini alır (güvenlik için)
    """
    # Tüm backup dizinlerini bul
    backup_dir_pattern = "_backup"
    backup_dirs = []
    
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and backup_dir_pattern in item:
            backup_dirs.append(item)
    
    if not backup_dirs:
        print("Temizlenecek yedek dizini bulunamadı.")
        return None
        
    # Ana yedek dizinini oluştur
    main_backup_dir = f"all_backups_{time.strftime('%Y%m%d_%H%M%S')}"
    main_backup_path = os.path.join(BASE_DIR, main_backup_dir)
    os.makedirs(main_backup_path, exist_ok=True)
    
    print(f"Bulunan yedek dizinleri: {len(backup_dirs)}")
    
    # Her bir yedek dizinini bu ana yedek dizinine taşı
    for backup_dir in backup_dirs:
        try:
            src_path = os.path.join(BASE_DIR, backup_dir)
            dst_path = os.path.join(main_backup_path, backup_dir)
            
            # Eğer dizin boşsa sadece bir not bırak
            if not os.listdir(src_path):
                with open(os.path.join(main_backup_path, f"{backup_dir}_was_empty.txt"), 'w') as f:
                    f.write(f"{backup_dir} dizini boştu. {time.strftime('%Y-%m-%d %H:%M:%S')}")
                continue
                
            # Dizini taşı
            shutil.move(src_path, dst_path)
            print(f"✅ {backup_dir}/ dizini {main_backup_dir}/ dizinine taşındı.")
        except Exception as e:
            print(f"❌ {backup_dir}/ dizini taşınamadı: {e}")
            
    print(f"\n✅ Tüm yedek dizinleri {main_backup_dir}/ dizinine taşındı.")
    return main_backup_path

def clean_pycache_dirs():
    """
    __pycache__ dizinlerini temizler
    """
    count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                try:
                    pycache_path = os.path.join(root, dir_name)
                    shutil.rmtree(pycache_path)
                    count += 1
                except Exception as e:
                    print(f"❌ {pycache_path} temizlenemedi: {e}")
    
    print(f"✅ {count} adet __pycache__ dizini temizlendi.")

def main():
    """
    Ana işlevi gerçekleştirir
    """
    print("\n🧹 FinAsis - Yedek Dizinleri Temizleme İşlemi")
    print("===========================================\n")
    
    # Yedek dizinlerini taşı
    backup_path = backup_backup_dirs()
    if not backup_path:
        print("❌ Temizlenecek yedek dizini bulunamadı.")
    else:
        # __pycache__ dizinlerini temizle
        print("\n🧹 __pycache__ dizinleri temizleniyor...")
        clean_pycache_dirs()
        
        # Projeyi test etmek için öneriler
        print("\n📋 Sonraki Adımlar:")
        print("1. Django sunucusunu başlatarak projeyi test edin:")
        print("   python manage.py runserver")
        print("2. Veritabanı migrasyonlarını kontrol edin:")
        print("   python manage.py migrate --check")
        print("3. Admin paneline erişebildiğinizden emin olun:")
        print("   http://localhost:8000/admin/")
        print("4. Temel işlevleri test edin:")
        print("   - Giriş yapabilme")
        print("   - Ana sayfayı görüntüleme")
        print("   - Modüllere erişebilme")
        
        print(f"\n⚠️ Bir sorun olursa, {os.path.basename(backup_path)} dizinindeki yedekleri kullanabilirsiniz.")
        print("\n✅ Temizleme işlemi başarıyla tamamlandı!")

if __name__ == "__main__":
    main() 