#!/usr/bin/env python
"""
Django MVT (Model-View-Template) yapısını tüm uygulamalara uygulamak için otomasyon betiği.
Bu betik, uygulama dizinlerini kontrol eder ve gerekli dizin yapısını oluşturur.
"""

import os
import sys
import argparse
from pathlib import Path

# Django ayarlarını yükle
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Django ortamını başlat
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.apps import apps
from django.conf import settings

def setup_mvt_structure():
    """
    Tüm uygulamalar için MVT dizin yapısını oluşturur.
    """
    print("Django MVT yapısını uygulamalara uygulama işlemi başlatılıyor...")
    
    # Django uygulamalarını al
    django_apps = [app for app in apps.get_app_configs() if not app.name.startswith('django.') and not app.name.startswith('rest_framework')]
    
    for app in django_apps:
        print(f"\n[*] {app.name} uygulaması MVT yapısı düzenleniyor...")
        
        # Uygulama dizini yolunu al
        app_dir = app.path
        app_name = app.name.split('.')[-1]
        
        # 1. views dizini oluştur
        views_dir = os.path.join(app_dir, 'views')
        if not os.path.exists(views_dir):
            os.makedirs(views_dir)
            print(f"  - {app_name}/views/ dizini oluşturuldu.")
            
            # __init__.py dosyasını oluştur
            with open(os.path.join(views_dir, '__init__.py'), 'w', encoding='utf-8') as f:
                f.write(f'"""\n{app_name} uygulaması için görünümler (views) modülü\n"""\n\n')
            print(f"  - {app_name}/views/__init__.py dosyası oluşturuldu.")
        
        # 2. templates dizini oluştur
        templates_dir = os.path.join(app_dir, 'templates', app_name)
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            print(f"  - {app_name}/templates/{app_name}/ dizini oluşturuldu.")
        
        # 3. Mevcut views.py dosyasını taşı
        views_py = os.path.join(app_dir, 'views.py')
        if os.path.exists(views_py):
            # views.py içeriğini al
            with open(views_py, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Eğer içerik varsa, views/generic.py'ye taşı
            if content.strip():
                with open(os.path.join(views_dir, 'generic.py'), 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # views/__init__.py'yi güncelle
                with open(os.path.join(views_dir, '__init__.py'), 'a', encoding='utf-8') as f:
                    f.write('from .generic import *\n')
                
                print(f"  - views.py dosyası views/generic.py'ye taşındı.")
            
            # Eski views.py dosyasını sil
            os.remove(views_py)
            print(f"  - Eski views.py dosyası silindi.")
        
        # 4. forms.py dosyasını kontrol et ve forms dizini oluştur
        forms_py = os.path.join(app_dir, 'forms.py')
        if os.path.exists(forms_py):
            forms_dir = os.path.join(app_dir, 'forms')
            if not os.path.exists(forms_dir):
                os.makedirs(forms_dir)
                
                # __init__.py dosyasını oluştur
                with open(os.path.join(forms_dir, '__init__.py'), 'w', encoding='utf-8') as f:
                    f.write(f'"""\n{app_name} uygulaması için formlar modülü\n"""\n\n')
                
                # forms.py içeriğini al
                with open(forms_py, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Eğer içerik varsa, forms/generic.py'ye taşı
                if content.strip():
                    with open(os.path.join(forms_dir, 'generic.py'), 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # forms/__init__.py'yi güncelle
                    with open(os.path.join(forms_dir, '__init__.py'), 'a', encoding='utf-8') as f:
                        f.write('from .generic import *\n')
                    
                    print(f"  - forms.py dosyası forms/generic.py'ye taşındı.")
                
                # Eski forms.py dosyasını sil
                os.remove(forms_py)
                print(f"  - Eski forms.py dosyası silindi.")
        
        # 5. Diğer potansiyel dizinleri oluştur
        for dirname in ['serializers', 'utils', 'tests', 'api']:
            dir_path = os.path.join(app_dir, dirname)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
                # __init__.py dosyasını oluştur
                with open(os.path.join(dir_path, '__init__.py'), 'w', encoding='utf-8') as f:
                    f.write(f'"""\n{app_name} uygulaması için {dirname} modülü\n"""\n\n')
                
                print(f"  - {app_name}/{dirname}/ dizini oluşturuldu.")
        
        # 6. urls.py dosyasını kontrol et
        urls_py = os.path.join(app_dir, 'urls.py')
        if not os.path.exists(urls_py):
            with open(urls_py, 'w', encoding='utf-8') as f:
                f.write(f'"""\n{app_name} uygulaması URL yapılandırmaları\n"""\n\n')
                f.write('from django.urls import path\n')
                f.write(f'from apps.{app_name} import views\n\n')
                f.write(f'app_name = "{app_name}"\n\n')
                f.write('urlpatterns = [\n')
                f.write('    # URL pattern\'leri buraya eklenecek\n')
                f.write(']\n')
            
            print(f"  - {app_name}/urls.py dosyası oluşturuldu.")
    
    print("\nDjango MVT yapısı tüm uygulamalara başarıyla uygulandı.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Django MVT yapısını tüm uygulamalara uygula')
    args = parser.parse_args()
    
    setup_mvt_structure() 