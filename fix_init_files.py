#!/usr/bin/env python
"""
Bu script, taşıma işlemi sırasında sorun yaşanan __init__.py dosyalarını yeniden oluşturur.
"""
import os
from pathlib import Path
import sys

def find_init_files():
    """
    Proje içerisindeki tüm __init__.py dosyalarını bulur
    """
    base_dir = Path(__file__).resolve().parent
    init_files = []
    
    for root, dirs, files in os.walk(base_dir):
        # Virtual environment ve derleme klasörlerini atla
        if any(skip_dir in root for skip_dir in ['.git', 'venv', '.venv', 'node_modules', 'dist']):
            continue
            
        if '__init__.py' in files:
            init_files.append(os.path.join(root, '__init__.py'))
    
    return init_files

def fix_init_file(file_path):
    """
    Tek bir __init__.py dosyasını yeniden oluşturur
    """
    # Dosyanın içeriğini oku
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Dosya içeriği kontrolü
        if content is None or len(content) < 2:
            print(f"❗ {file_path} dosyası boş veya çok kısa, yenileniyor...")
            module_name = os.path.basename(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'# -*- coding: utf-8 -*-\n"""\n{module_name} modülü\n"""\n')
            print(f"✅ {file_path} dosyası yenilendi.")
            return True
        print(f"📋 {file_path} dosyası düzgün okunamadı, yenileniyor...")
        return False
    except UnicodeDecodeError:
        # Hatalı dosyayı yenisiyle değiştir
        module_name = os.path.basename(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f'# -*- coding: utf-8 -*-\n"""\n{module_name} modülü\n"""\n')
        print(f"✅ {file_path} dosyası yenilendi.")
        return True
    except Exception as e:
        print(f"❌ {file_path} dosyası onarılamadı: {e}")
        return False

def fix_all_init_files():
    """
    Tüm __init__.py dosyalarını kontrol eder ve gerekenleri yeniler
    """
    init_files = find_init_files()
    print(f"{len(init_files)} adet __init__.py dosyası bulundu.")
    
    fixed_count = 0
    error_count = 0
    
    for file_path in init_files:
        try:
            if fix_init_file(file_path):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Hata: {file_path} dosyası işlenirken sorun oluştu: {e}")
            error_count += 1
    
    print(f"\nİşlem tamamlandı.")
    print(f"✅ {fixed_count} adet dosya onarıldı.")
    print(f"❌ {error_count} adet dosyada hata oluştu.")

if __name__ == "__main__":
    fix_all_init_files() 