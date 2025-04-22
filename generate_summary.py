#!/usr/bin/env python
"""
Modül taşıma işlemi sonrası bir özet rapor oluşturur
"""
import os
from pathlib import Path
import sys
import time

def get_directory_structure(root_dir, excluded_dirs=None):
    """
    Belirtilen dizinin içeriğini ağaç yapısı olarak döndürür
    """
    if excluded_dirs is None:
        excluded_dirs = ['.git', 'venv', '.venv', '__pycache__', 'node_modules', 'dist']
    
    struct = {'name': os.path.basename(root_dir)}
    
    if os.path.isdir(root_dir):
        struct['type'] = 'directory'
        struct['children'] = []
        
        try:
            for item in os.listdir(root_dir):
                item_path = os.path.join(root_dir, item)
                
                # Dışlanacak dizinleri atla
                if os.path.isdir(item_path) and item in excluded_dirs:
                    continue
                    
                # Eğer dizin boş değilse veya dosya ise ekle
                if os.path.isfile(item_path) or os.path.isdir(item_path) and os.listdir(item_path):
                    struct['children'].append(get_directory_structure(item_path, excluded_dirs))
        except PermissionError:
            pass
    else:
        struct['type'] = 'file'
        
    return struct

def print_directory_structure(structure, indent=0, is_last=True):
    """
    Ağaç yapısını formatlanmış şekilde yazdırır
    """
    prefix = '    ' * indent
    connector = '└── ' if is_last else '├── '
    
    # Mevcut öğeyi yazdır
    print(f"{prefix}{connector}{structure['name']}")
    
    # Alt öğeleri işle
    if structure['type'] == 'directory' and 'children' in structure:
        children = structure['children']
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            print_directory_structure(child, indent + 1, is_last_child)

def count_modules():
    """
    Taşınan modüllerin sayısını hesaplar
    """
    # Ana dizin
    base_dir = Path(__file__).resolve().parent
    
    # Modülleri say
    modules = [d for d in os.listdir(base_dir) 
              if os.path.isdir(os.path.join(base_dir, d)) 
              and not d.startswith('.') 
              and not d.startswith('__')
              and d not in ['venv', '.venv', 'node_modules', 'dist', 'static', 'media', 'staticfiles']]
    
    # Apps dizini içindeki modülleri kontrol et
    apps_dir = os.path.join(base_dir, 'apps')
    if os.path.exists(apps_dir) and os.path.isdir(apps_dir):
        apps_modules = [d for d in os.listdir(apps_dir) 
                       if os.path.isdir(os.path.join(apps_dir, d)) 
                       and not d.startswith('.') 
                       and not d.startswith('__')]
        return len(modules), len(apps_modules)
    
    return len(modules), 0

def generate_summary():
    """
    Taşıma işlemi sonrası bir özet rapor oluşturur
    """
    # Ana dizin
    base_dir = Path(__file__).resolve().parent
    
    print("\n" + "="*50)
    print(" FinAsis Modül Taşıma İşlemi - Özet Rapor")
    print("="*50 + "\n")
    
    # Tarih ve saat
    print(f"Rapor Tarihi: {time.strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Modül sayıları
    ana_dizin_modul_sayisi, apps_modul_sayisi = count_modules()
    print(f"\nAna dizindeki modül sayısı: {ana_dizin_modul_sayisi}")
    print(f"Apps dizinindeki modül sayısı: {apps_modul_sayisi}")
    
    # Taşıma durumu
    if apps_modul_sayisi == 0:
        print("\nTüm modüller başarıyla ana dizine taşınmış.")
    else:
        print(f"\nDİKKAT: {apps_modul_sayisi} modül hala apps/ dizininde bulunuyor.")
    
    # Dizin yapısı
    print("\nGüncel Dizin Yapısı:\n")
    
    # Ana dizin yapısını al, sadece ilk seviyedeki dizinleri göster
    root_structure = {'name': base_dir.name, 'type': 'directory', 'children': []}
    
    # Dışlanacak dizinler
    excluded_dirs = ['.git', 'venv', '.venv', '__pycache__', 'node_modules', 'dist', 'staticfiles', 'media']
    
    # Ana dizindeki her bir öğeyi listeye ekle
    for item in sorted(os.listdir(base_dir)):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.') and item not in excluded_dirs:
            root_structure['children'].append({'name': item, 'type': 'directory'})
    
    # Dizin yapısını yazdır
    for i, child in enumerate(root_structure['children']):
        is_last = i == len(root_structure['children']) - 1
        print_directory_structure(child, 0, is_last)
    
    # Sonuç
    print("\nTaşıma işlemi tamamlandı.")
    print("\nNotlar:")
    print("- Django ayarlarını kontrol edin ve gerekli düzenlemeleri yapın.")
    print("- Modüller arası bağımlılıklarda sorun yaşanabilir, test edin.")
    print("- Test ortamında projeyi çalıştırın ve herhangi bir hata olup olmadığını kontrol edin.")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    generate_summary() 