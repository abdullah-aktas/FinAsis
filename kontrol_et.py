#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Proje Kontrol Sistemi
---------------------
Bu script, projenin gerekli paketlerini kontrol eder ve eksik olanları otomatik olarak yükler.
"""

import pkg_resources
import subprocess
import sys
import os
import time
from colorama import init, Fore, Style

# Colorama'yı başlat
init()

def check_packages():
    """
    requirements.txt dosyasındaki paketleri kontrol eder ve eksik olanları yükler.
    """
    print(f"{Fore.CYAN}Proje paketleri kontrol ediliyor...{Style.RESET_ALL}")
    
    # requirements.txt dosyasının varlığını kontrol et
    if not os.path.exists('requirements.txt'):
        print(f"{Fore.RED}Hata: requirements.txt dosyası bulunamadı!{Style.RESET_ALL}")
        return False
    
    # requirements.txt dosyasını oku
    with open('requirements.txt', 'r') as f:
        packages = f.read().splitlines()
    
    if not packages:
        print(f"{Fore.YELLOW}Uyarı: requirements.txt dosyası boş!{Style.RESET_ALL}")
        return False
    
    missing_packages = []
    installed_packages = []
    
    # Her paketi kontrol et
    for package in packages:
        # Boş satırları atla
        if not package.strip():
            continue
            
        # Yorum satırlarını atla
        if package.startswith('#'):
            continue
            
        try:
            pkg_resources.require(package)
            installed_packages.append(package)
            print(f"{Fore.GREEN}✓ {package} yüklü.{Style.RESET_ALL}")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
            missing_packages.append(package)
            print(f"{Fore.YELLOW}✗ {package} eksik.{Style.RESET_ALL}")
    
    # Eksik paketleri yükle
    if missing_packages:
        print(f"\n{Fore.CYAN}Eksik paketler yükleniyor...{Style.RESET_ALL}")
        for package in missing_packages:
            print(f"{Fore.CYAN}Yükleniyor: {package}{Style.RESET_ALL}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{Fore.GREEN}✓ {package} başarıyla yüklendi.{Style.RESET_ALL}")
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}✗ {package} yüklenirken hata oluştu!{Style.RESET_ALL}")
    
    # Özet bilgileri göster
    print(f"\n{Fore.CYAN}Kontrol Tamamlandı:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Yüklü Paketler: {len(installed_packages)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Eksik Paketler: {len(missing_packages)}{Style.RESET_ALL}")
    
    return True

def check_django_settings():
    """
    Django ayarlarını kontrol eder.
    """
    print(f"\n{Fore.CYAN}Django ayarları kontrol ediliyor...{Style.RESET_ALL}")
    
    try:
        import django
        from django.conf import settings
        
        # Django sürümünü göster
        print(f"{Fore.GREEN}Django Sürümü: {django.get_version()}{Style.RESET_ALL}")
        
        # DEBUG modunu kontrol et
        if settings.DEBUG:
            print(f"{Fore.YELLOW}Uyarı: DEBUG modu açık!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}DEBUG modu kapalı.{Style.RESET_ALL}")
        
        # Veritabanı ayarlarını kontrol et
        db_engine = settings.DATABASES['default']['ENGINE']
        print(f"{Fore.GREEN}Veritabanı: {db_engine}{Style.RESET_ALL}")
        
        # INSTALLED_APPS sayısını göster
        print(f"{Fore.GREEN}Yüklü Uygulamalar: {len(settings.INSTALLED_APPS)}{Style.RESET_ALL}")
        
        return True
    except ImportError:
        print(f"{Fore.RED}Hata: Django yüklü değil!{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}Hata: Django ayarları kontrol edilirken bir sorun oluştu: {str(e)}{Style.RESET_ALL}")
        return False

def check_env_file():
    """
    .env dosyasının varlığını ve içeriğini kontrol eder.
    """
    print(f"\n{Fore.CYAN}.env dosyası kontrol ediliyor...{Style.RESET_ALL}")
    
    if not os.path.exists('.env'):
        print(f"{Fore.RED}Hata: .env dosyası bulunamadı!{Style.RESET_ALL}")
        return False
    
    # .env dosyasını oku
    with open('.env', 'r') as f:
        env_vars = f.read().splitlines()
    
    # Gerekli değişkenleri kontrol et
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 
                    'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
    
    missing_vars = []
    for var in required_vars:
        found = False
        for line in env_vars:
            if line.startswith(f"{var}="):
                found = True
                break
        if not found:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"{Fore.YELLOW}Uyarı: Aşağıdaki değişkenler .env dosyasında eksik:{Style.RESET_ALL}")
        for var in missing_vars:
            print(f"{Fore.YELLOW}  - {var}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Tüm gerekli değişkenler .env dosyasında mevcut.{Style.RESET_ALL}")
    
    return len(missing_vars) == 0

def main():
    """
    Ana fonksiyon
    """
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}        PROJE KONTROL SİSTEMİ{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}")
    
    start_time = time.time()
    
    # Paketleri kontrol et
    packages_ok = check_packages()
    
    # Django ayarlarını kontrol et
    django_ok = check_django_settings()
    
    # .env dosyasını kontrol et
    env_ok = check_env_file()
    
    # Sonuçları göster
    print(f"\n{Fore.CYAN}=========================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}        KONTROL SONUÇLARI{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}")
    
    print(f"Paketler: {'✓' if packages_ok else '✗'}")
    print(f"Django Ayarları: {'✓' if django_ok else '✗'}")
    print(f".env Dosyası: {'✓' if env_ok else '✗'}")
    
    # Genel durum
    if packages_ok and django_ok and env_ok:
        print(f"\n{Fore.GREEN}Tüm kontroller başarılı! Proje çalışmaya hazır.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}Bazı kontroller başarısız oldu. Lütfen yukarıdaki uyarıları dikkate alın.{Style.RESET_ALL}")
    
    # Çalışma süresini göster
    elapsed_time = time.time() - start_time
    print(f"\n{Fore.CYAN}Kontrol süresi: {elapsed_time:.2f} saniye{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 