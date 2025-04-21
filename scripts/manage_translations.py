#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Çeviri dosyalarını yönetmek için kapsamlı bir script.
Bu script, Django projesi için .po ve .mo dosyalarını oluşturmayı, 
derlemyi ve durumlarını kontrol etmeyi sağlar.

Kullanım:
$ python scripts/manage_translations.py make      # po dosyalarını günceller
$ python scripts/manage_translations.py compile   # po dosyalarını derler
$ python scripts/manage_translations.py status    # çeviri durumunu gösterir
$ python scripts/manage_translations.py init      # ilk kez çeviri dosyalarını hazırlar
"""

import os
import sys
import subprocess
from glob import glob
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_DIR = os.path.join(BASE_DIR, 'locale')
DJANGO_APPS = []  # Django ile gelen ve çevirileri olan uygulamalar
PROJECT_APPS = [app for app in settings.INSTALLED_APPS if app.startswith('apps.') or 
                not app.startswith('django.') and not app.startswith('rest_framework')]
LANGUAGES = [lang_code for lang_code, lang_name in settings.LANGUAGES]

def get_app_dirs():
    """Tüm uygulamaların dizinlerini döndürür"""
    app_dirs = []
    
    # Proje uygulamalarını ekle
    for app in PROJECT_APPS:
        if app.startswith('apps.'):
            app_dir = os.path.join(BASE_DIR, app.replace('.', '/'))
        else:
            app_dir = os.path.join(BASE_DIR, app.replace('.', '/'))
        if os.path.exists(app_dir):
            app_dirs.append(app_dir)
    
    # Core ve diğer dizinleri ekle
    app_dirs.append(os.path.join(BASE_DIR, 'core'))
    app_dirs.append(os.path.join(BASE_DIR, 'templates'))
    app_dirs.append(os.path.join(BASE_DIR, 'static'))
    
    return app_dirs

def make_messages():
    """Django'nun makemessages komutunu çalıştırarak çeviri dosyalarını günceller"""
    print("Çeviri dosyaları güncelleniyor...")
    
    for lang in LANGUAGES:
        # Django komutunu çalıştır
        cmd = [
            'django-admin', 'makemessages',
            '--locale={}'.format(lang),
            '--ignore=venv/*',
            '--ignore=node_modules/*',
            '--ignore=*/migrations/*',
            '--ignore=*/static/CACHE/*',
            '--no-obsolete',
            '--extension=html,py,txt',
            '--no-location'
        ]
        
        # Verbosity ayarını ekle
        cmd.append('--verbosity=1')
        
        # Komutu çalıştır
        print(f"👉 {' '.join(cmd)}")
        subprocess.call(cmd)
    
    print("✅ Çeviri dosyaları güncellendi.")

def compile_messages():
    """Django'nun compilemessages komutunu çalıştırarak çeviri dosyalarını derler"""
    print("Çeviri dosyaları derleniyor...")
    
    # Django komutunu çalıştır
    cmd = [
        'django-admin', 'compilemessages',
        '--ignore=venv/*',
        '--ignore=node_modules/*'
    ]
    
    # Verbosity ayarını ekle
    cmd.append('--verbosity=1')
    
    # Komutu çalıştır
    print(f"👉 {' '.join(cmd)}")
    subprocess.call(cmd)
    
    print("✅ Çeviri dosyaları derlendi.")

def check_status():
    """Çeviri dosyalarının durumunu kontrol eder ve çevrilmemiş string sayısını gösterir"""
    print("Çeviri dosyalarının durumu kontrol ediliyor...\n")
    
    total_stats = {lang: {'total': 0, 'translated': 0, 'fuzzy': 0, 'untranslated': 0} for lang in LANGUAGES}
    
    for lang in LANGUAGES:
        lang_dir = os.path.join(LOCALE_DIR, lang, 'LC_MESSAGES')
        if not os.path.exists(lang_dir):
            print(f"⚠️ {lang} dili için çeviri dizini bulunamadı: {lang_dir}")
            continue
        
        po_files = glob(os.path.join(lang_dir, '*.po'))
        if not po_files:
            print(f"⚠️ {lang} dili için .po dosyası bulunamadı")
            continue
        
        print(f"🔍 {lang} dili için durum:")
        
        for po_file in po_files:
            domain = os.path.basename(po_file).split('.')[0]
            cmd = ['msgfmt', '--statistics', po_file, '-o', '/dev/null']
            
            try:
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8').strip()
                print(f"  📊 {domain}.po: {output}")
                
                # İstatistikleri ayrıştır
                stats = {'total': 0, 'translated': 0, 'fuzzy': 0, 'untranslated': 0}
                
                if 'translated' in output:
                    translated = int(output.split(' translated')[0].split(' ')[-1])
                    stats['translated'] = translated
                    total_stats[lang]['translated'] += translated
                
                if 'fuzzy' in output:
                    fuzzy = int(output.split(' fuzzy')[0].split(' ')[-1])
                    stats['fuzzy'] = fuzzy
                    total_stats[lang]['fuzzy'] += fuzzy
                
                if 'untranslated' in output:
                    untranslated = int(output.split(' untranslated')[0].split(' ')[-1])
                    stats['untranslated'] = untranslated
                    total_stats[lang]['untranslated'] += untranslated
                
                stats['total'] = stats['translated'] + stats['fuzzy'] + stats['untranslated']
                total_stats[lang]['total'] += stats['total']
                
                # Çevirme yüzdesini hesapla
                if stats['total'] > 0:
                    percentage = (stats['translated'] / stats['total']) * 100
                    print(f"    📈 %{percentage:.1f} tamamlandı")
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Hata: {e}")
        
        print("")
    
    # Toplam istatistikleri göster
    print("📋 Genel Durum:")
    for lang in LANGUAGES:
        stats = total_stats[lang]
        if stats['total'] > 0:
            percentage = (stats['translated'] / stats['total']) * 100
            print(f"  🌐 {lang}: {stats['translated']}/{stats['total']} çevrildi (%{percentage:.1f})")
            if stats['fuzzy'] > 0:
                print(f"    ⚠️ {stats['fuzzy']} belirsiz çeviri")
            if stats['untranslated'] > 0:
                print(f"    ❌ {stats['untranslated']} çevrilmemiş string")
        else:
            print(f"  🌐 {lang}: Çeviri dosyası bulunamadı veya boş")
    
    print("\n✅ Çeviri durumu kontrolü tamamlandı.")

def init_translations():
    """Tüm diller için ilk kez çeviri dosyaları oluşturur"""
    print("Çeviri dizinleri oluşturuluyor...")
    
    # Locale dizinini oluştur
    if not os.path.exists(LOCALE_DIR):
        os.makedirs(LOCALE_DIR)
        print(f"✅ {LOCALE_DIR} dizini oluşturuldu")
    
    # Çeviri dosyaları oluştur
    for lang in LANGUAGES:
        lang_dir = os.path.join(LOCALE_DIR, lang, 'LC_MESSAGES')
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
            print(f"✅ {lang_dir} dizini oluşturuldu")
    
    # Çeviri dosyalarını oluştur
    make_messages()
    
    print("\n✅ Çeviri dosyaları başarıyla oluşturuldu.")
    print("📝 İpuçları:")
    print("  - Şablonlarda çeviri kullanımı: {% trans \"Çevrilecek Metin\" %}")
    print("  - Python dosyalarında çeviri kullanımı: _('Çevrilecek Metin')")
    print("  - Lazy çeviriler için: gettext_lazy('Çevrilecek Metin')")

def print_help():
    """Kullanım bilgilerini yazdırır"""
    print("""
Django Çeviri Yönetim Aracı
---------------------------
Kullanım:
  python scripts/manage_translations.py [komut]

Komutlar:
  make      - Çeviri (.po) dosyalarını günceller
  compile   - Çeviri (.po) dosyalarını derler
  status    - Çevirilerin durumunu gösterir
  init      - İlk kez çeviri dosyalarını oluşturur
  help      - Bu yardım mesajını gösterir
    """)

def main():
    """Ana çalıştırma fonksiyonu"""
    # Komut satırı argümanları
    parser = ArgumentParser(description='Django çeviri dosyalarını yönetir',
                           formatter_class=ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('command', nargs='?', default='help',
                      choices=['make', 'compile', 'status', 'init', 'help'],
                      help='Çalıştırılacak komut')
    
    # Argümanları ayrıştır
    args = parser.parse_args()
    
    # Komutu çalıştır
    if args.command == 'make':
        make_messages()
    elif args.command == 'compile':
        compile_messages()
    elif args.command == 'status':
        check_status()
    elif args.command == 'init':
        init_translations()
    else:
        print_help()

if __name__ == '__main__':
    main() 