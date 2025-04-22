#!/usr/bin/env python
"""
Bu script, URL patternlerini ve url paketlerindeki import ifadelerini günceller.
"""
import os
import re
from pathlib import Path

# Projenin ana dizini
BASE_DIR = Path(__file__).resolve().parent

def update_urls_py(file_path):
    """
    urls.py dosyalarındaki import ifadelerini günceller
    """
    try:
        if not os.path.exists(file_path):
            return
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Import ifadelerini güncelle
        updated_content = re.sub(
            r'from apps\.(\w+)', 
            r'from \1', 
            content
        )
        
        # include() ifadelerini güncelle
        updated_content = re.sub(
            r'include\([\'"]apps\.(\w+)', 
            r'include([\'\1', 
            updated_content
        )
        
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print(f"Updated URLs in {file_path}")
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def find_all_urls_py():
    """
    Proje içindeki tüm urls.py dosyalarını bulur ve günceller
    """
    # Ana config/urls.py dosyasını güncelle
    main_urls_py = os.path.join(BASE_DIR, 'config/urls.py')
    update_urls_py(main_urls_py)
    
    # Modüllerin urls.py dosyalarını güncelle
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file == 'urls.py' and 'venv' not in root and '.git' not in root:
                file_path = os.path.join(root, file)
                update_urls_py(file_path)

if __name__ == "__main__":
    find_all_urls_py() 