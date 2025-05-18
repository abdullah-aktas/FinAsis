# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Bu script, apps/ dizinindeki kalan modülleri ana dizine taşıdıktan sonra
apps/ dizinini tamamen kaldırır.
"""
import os
import shutil
from pathlib import Path
import time

# Ana dizin
BASE_DIR = Path(__file__).resolve().parent

def backup_apps_directory():
    """
    apps/ dizininin yedeğini alır
    """
    apps_dir = os.path.join(BASE_DIR, 'apps')
    if not os.path.exists(apps_dir):
        print("apps/ dizini bulunamadı.")
        return None
        
    # Yedek dizini adı
    backup_dir = f"apps_backup_{time.strftime('%Y%m%d_%H%M%S')}"
    backup_path = os.path.join(BASE_DIR, backup_dir)
    
    # Yedekleme işlemi
    try:
        shutil.copytree(apps_dir, backup_path)
        print(f"✅ apps/ dizini {backup_dir} olarak yedeklendi.")
        return backup_path
    except Exception as e:
        print(f"❌ Yedekleme sırasında hata: {e}")
        return None

def move_remaining_modules(backup_path):
    """
    apps/ dizinindeki kalan modülleri ana dizine taşır
    """
    apps_dir = os.path.join(BASE_DIR, 'apps')
    if not os.path.exists(apps_dir):
        print("apps/ dizini bulunamadı.")
        return False
        
    # apps/ içindeki modülleri bul
    modules = [d for d in os.listdir(apps_dir) 
              if os.path.isdir(os.path.join(apps_dir, d)) 
              and not d.startswith('__') 
              and not d.startswith('.')]
    
    if not modules:
        print("apps/ dizininde taşınacak modül kalmamış.")
        return True
        
    print(f"Taşınacak modüller: {', '.join(modules)}")
    
    # Her modülü taşı
    for module in modules:
        src_path = os.path.join(apps_dir, module)
        dst_path = os.path.join(BASE_DIR, module)
        
        # Hedef dizin zaten varsa, yedekle
        if os.path.exists(dst_path):
            backup_module_path = f"{dst_path}_apps_backup"
            print(f"⚠️ {module}/ dizini zaten mevcut, {os.path.basename(backup_module_path)} olarak yedekleniyor.")
            
            if os.path.exists(backup_module_path):
                shutil.rmtree(backup_module_path)
                
            shutil.move(dst_path, backup_module_path)
            
        # Modülü taşı
        try:
            shutil.copytree(src_path, dst_path)
            print(f"✅ {module}/ dizini ana dizine taşındı.")
            
            # apps.py dosyasını güncelle
            apps_py_path = os.path.join(dst_path, "apps.py")
            if os.path.exists(apps_py_path):
                try:
                    with open(apps_py_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content is None or len(content) < 2:
                            print(f"❗ {apps_py_path} dosyası boş veya çok kısa!")
                            # Gerekirse otomatik düzeltme eklenebilir
                        updated_content = content.replace(f"name = 'apps.{module}'", f"name = '{module}'")
                        updated_content = updated_content.replace(f"import apps.{module}", f"import {module}")
                        
                        with open(apps_py_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                            
                        print(f"✅ {module}/apps.py dosyası güncellendi.")
                except Exception as e:
                    print(f"❌ {module}/apps.py güncellenirken hata: {e}")
            
        except Exception as e:
            print(f"❌ {module}/ taşınırken hata: {e}")
            continue
    
    return True

def remove_apps_directory():
    """
    apps/ dizinini tamamen kaldırır
    """
    apps_dir = os.path.join(BASE_DIR, 'apps')
    if not os.path.exists(apps_dir):
        print("apps/ dizini zaten kaldırılmış.")
        return True
    
    try:
        shutil.rmtree(apps_dir)
        print("✅ apps/ dizini başarıyla kaldırıldı.")
        return True
    except Exception as e:
        print(f"❌ apps/ dizini kaldırılırken hata: {e}")
        return False

def main():
    """
    Ana işlevi gerçekleştirir
    """
    print("\n🔄 FinAsis - apps/ Dizini Kaldırma İşlemi")
    print("========================================\n")
    
    # 1. apps/ dizinini yedekle
    backup_path = backup_apps_directory()
    if not backup_path:
        print("❌ Yedekleme başarısız olduğu için işlem iptal edildi.")
        return
    
    # 2. Kalan modülleri taşı
    print("\n📦 Kalan modüller taşınıyor...")
    if not move_remaining_modules(backup_path):
        print("❌ Modüller taşınamadı, işlem iptal edildi.")
        return
    
    # 3. apps/ dizinini kaldır
    print("\n🗑️ apps/ dizini kaldırılıyor...")
    if remove_apps_directory():
        print("\n✅ İşlem başarıyla tamamlandı!")
        print(f"⚠️ Bir sorun olursa, {os.path.basename(backup_path)} dizinindeki yedek dosyaları kullanabilirsiniz.")
    else:
        print("\n❌ İşlem tamamlanamadı.")
        print(f"⚠️ Yedek dosyalar {os.path.basename(backup_path)} dizininde bulunabilir.")

if __name__ == "__main__":
    main() 