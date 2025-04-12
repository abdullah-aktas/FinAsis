#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Proje Kontrol Sistemi
---------------------
Bu modül, projenin gerekli paketlerini ve bileşenlerini kontrol eder.
"""

import pkg_resources
import subprocess
import sys
import os
import time
from pathlib import Path

# Colorama'yı kontrol et ve yükle
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    print("Colorama kütüphanesi yükleniyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import init, Fore, Style
    init()

# Proje kök dizinini belirle
PROJECT_ROOT = Path(__file__).parent.parent.parent

def check_packages():
    """
    requirements.txt dosyasındaki paketleri kontrol eder ve eksik olanları yükler.
    """
    print(f"{Fore.CYAN}Proje paketleri kontrol ediliyor...{Style.RESET_ALL}")
    
    requirements_file = PROJECT_ROOT / 'requirements.txt'
    
    # requirements.txt dosyasının varlığını kontrol et
    if not requirements_file.exists():
        print(f"{Fore.RED}Hata: requirements.txt dosyası bulunamadı!{Style.RESET_ALL}")
        return False
    
    # requirements.txt dosyasını oku
    with open(requirements_file, 'r') as f:
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

# ... (diğer fonksiyonlar aynı kalacak, sadece dosya yolları PROJECT_ROOT kullanılarak güncellenecek)

def main():
    """
    Ana kontrol fonksiyonu
    """
    print(f"{Fore.CYAN}Proje kontrol sistemi başlatılıyor...{Style.RESET_ALL}")
    
    # Paketleri kontrol et
    check_packages()
    
    # Django ayarlarını kontrol et
    check_django_settings()
    
    # .env dosyasını kontrol et
    check_env_file()
    
    # Çevrimdışı mod ayarlarını kontrol et
    check_offline_mode()
    
    # AI/ML bileşenlerini kontrol et
    check_ai_ml_components()
    
    # Blockchain bileşenlerini kontrol et
    check_blockchain_components()
    
    # Mobil bileşenleri kontrol et
    check_mobile_components()
    
    # Eğitim bileşenlerini kontrol et
    check_education_components()
    
    # Oyun bileşenlerini kontrol et
    check_game_components()
    
    print(f"\n{Fore.GREEN}Proje kontrolü tamamlandı!{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 