#!/usr/bin/env python
"""
Bu script, Django settings.py dosyasındaki INSTALLED_APPS listesini günceller.
"""
import os
import re
from pathlib import Path

# Projenin ana dizini
BASE_DIR = Path(__file__).resolve().parent

def update_installed_apps():
    """
    config/settings/base.py dosyasındaki INSTALLED_APPS listesini günceller
    """
    settings_path = os.path.join(BASE_DIR, 'config/settings/base.py')
    if not os.path.exists(settings_path):
        print(f"Settings file {settings_path} not found.")
        return

    try:
        with open(settings_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Installed apps bölümünü bul
        installed_apps_pattern = r'INSTALLED_APPS\s*=\s*\[(.*?)\]'
        installed_apps_match = re.search(installed_apps_pattern, content, re.DOTALL)
        
        if not installed_apps_match:
            print("INSTALLED_APPS section not found in settings.")
            return
            
        installed_apps_section = installed_apps_match.group(1)
        
        # 'apps.xxx' formatındaki tüm uygulamaları bul ve güncelle
        updated_section = re.sub(
            r"'apps\.(\w+)\.apps\.(\w+Config)'", 
            r"'\1.apps.\2'", 
            installed_apps_section
        )
        
        # apps.xxx formatını xxx formatına çevir
        updated_section = re.sub(
            r"'apps\.(\w+)'", 
            r"'\1'", 
            updated_section
        )
        
        # Değiştirilmiş içeriği dosyaya geri yaz
        updated_content = content.replace(installed_apps_match.group(1), updated_section)
        
        with open(settings_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        print(f"INSTALLED_APPS in {settings_path} successfully updated.")
        
    except Exception as e:
        print(f"Error updating settings.py: {e}")

if __name__ == "__main__":
    update_installed_apps() 