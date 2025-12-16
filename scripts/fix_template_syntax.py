#!/usr/bin/env python
"""
Template syntax hatalarını düzeltir:
- {%% → {%
- crispy_forms_tags → bootstrap5
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

TEMPLATE_DIRS = [
    BASE_DIR / "permissions" / "templates",
    BASE_DIR / "templates",
]

def fix_template_file(file_path):
    """Template dosyasındaki syntax hatalarını düzelt"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # {%% → {% düzelt
        content = content.replace('{%%', '{%')
        content = content.replace('%%}', '%}')
        
        # crispy_forms_tags → bootstrap5
        if 'crispy_forms_tags' in content:
            content = content.replace('{% load crispy_forms_tags %}', '{% load bootstrap5 %}')
            # {{ form|crispy }} → {% bootstrap_form form layout='vertical' %}
            content = re.sub(
                r'\{\{\s*form\s*\|\s*crispy\s*\}\}',
                "{% bootstrap_form form layout='vertical' %}",
                content
            )
        
        # Değişiklik varsa kaydet
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Düzeltildi: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Hata ({file_path}): {e}")
        return False

def main():
    """Tüm template dosyalarını tara ve düzelt"""
    fixed_count = 0
    
    for template_dir in TEMPLATE_DIRS:
        if not template_dir.exists():
            continue
        
        for html_file in template_dir.rglob('*.html'):
            if fix_template_file(html_file):
                fixed_count += 1
    
    print(f"\n✅ Toplam {fixed_count} dosya düzeltildi.")

if __name__ == '__main__':
    main()

