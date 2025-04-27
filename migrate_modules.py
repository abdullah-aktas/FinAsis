#!/usr/bin/env python
"""
Bu script, apps/ dizinindeki modülleri ana dizine taşır ve bağlantıları düzenler
"""
import os
import shutil
import re
from pathlib import Path

# Projenin ana dizini
BASE_DIR = Path(__file__).resolve().parent

def update_file_imports(file_path, old_prefix, new_prefix):
    """Dosya içerisindeki import ifadelerini günceller"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if content is None or len(content) < 2:
                print(f"❗ {file_path} dosyası boş veya çok kısa!")
                # Gerekirse otomatik düzeltme eklenebilir
        
        # Import ifadelerini güncelle
        pattern = fr'(from|import)\s+{old_prefix}\.([^\s\.]+)'
        updated_content = re.sub(pattern, fr'\1 {new_prefix}.\2', content)
        
        # Direkt modül referanslarını güncelle
        pattern = fr'{old_prefix}\.([^\s\.\(\),]+)'
        updated_content = re.sub(pattern, fr'{new_prefix}.\1', updated_content)
        
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print(f"Imports updated in {file_path}")
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def update_app_config(app_dir, old_name, new_name):
    """AppConfig sınıfındaki name değerini günceller"""
    apps_py_path = os.path.join(app_dir, 'apps.py')
    if os.path.exists(apps_py_path):
        try:
            with open(apps_py_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # name değerini güncelle
            updated_content = re.sub(
                fr"name\s*=\s*['\"]({old_name})['\"]", 
                f"name = '{new_name}'", 
                content
            )
            
            # ready metodunda import ifadelerini güncelle
            updated_content = re.sub(
                fr"import\s+{old_name}\.", 
                f"import {new_name}.", 
                updated_content
            )
            
            if content != updated_content:
                with open(apps_py_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                print(f"Updated AppConfig in {apps_py_path}")
                
        except Exception as e:
            print(f"Error updating AppConfig in {apps_py_path}: {e}")

def process_python_files(directory, old_prefix, new_prefix):
    """Belirtilen dizindeki tüm Python dosyalarında import ifadelerini günceller"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                update_file_imports(file_path, old_prefix, new_prefix)

def main():
    # Apps dizininde bulunan tüm modüller
    apps_dir = os.path.join(BASE_DIR, 'apps')
    modules = [d for d in os.listdir(apps_dir) 
               if os.path.isdir(os.path.join(apps_dir, d)) and not d.startswith('__')]
    
    print(f"Found modules: {', '.join(modules)}")
    
    for module in modules:
        print(f"\nProcessing module: {module}")
        old_module_path = os.path.join(apps_dir, module)
        new_module_path = os.path.join(BASE_DIR, module)
        
        # Eğer hedef dizin zaten varsa, önce onu yedekleyelim
        if os.path.exists(new_module_path):
            backup_path = f"{new_module_path}_backup"
            print(f"Target directory exists, backing up to {backup_path}")
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.move(new_module_path, backup_path)
        
        # Modülü ana dizine kopyala
        print(f"Copying {old_module_path} to {new_module_path}")
        shutil.copytree(old_module_path, new_module_path)
        
        # AppConfig sınıfını güncelle
        old_name = f'apps.{module}'
        new_name = module
        update_app_config(new_module_path, old_name, new_name)
        
        # Modül içindeki import ifadelerini güncelle
        process_python_files(new_module_path, f'apps.{module}', module)
        
    # Django settings.py dosyasını güncelle
    settings_path = os.path.join(BASE_DIR, 'config/settings/base.py')
    if os.path.exists(settings_path):
        print("\nUpdating Django settings...")
        update_file_imports(settings_path, 'apps', '')
    
    # Tüm projedeki diğer Python dosyalarında import ifadelerini güncelle
    print("\nUpdating imports in all project files...")
    for module in modules:
        process_python_files(BASE_DIR, f'apps.{module}', module)
    
    print("\nMigration completed. Please check the files for any remaining references.")
    print("Remember to update INSTALLED_APPS in settings.py manually if needed.")

if __name__ == "__main__":
    main() 