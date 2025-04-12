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

# Colorama'yı kontrol et ve yükle
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    print("Colorama kütüphanesi yükleniyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import init, Fore, Style
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
                    'DJANGO_SECRET_KEY', 'DJANGO_DEBUG', 'DJANGO_ALLOWED_HOSTS']
    
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

def check_offline_mode():
    """
    Çevrimdışı mod için gerekli ayarları kontrol eder.
    """
    print(f"\n{Fore.CYAN}Çevrimdışı mod ayarları kontrol ediliyor...{Style.RESET_ALL}")
    
    # SQLite veritabanının varlığını kontrol et
    if os.path.exists('db.sqlite3'):
        print(f"{Fore.GREEN}SQLite veritabanı mevcut.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Uyarı: SQLite veritabanı bulunamadı. Çevrimdışı mod için gerekli olabilir.{Style.RESET_ALL}")
    
    # Offline mod için gerekli dosyaların varlığını kontrol et
    offline_files = [
        'static/offline/index.html',
        'static/offline/app.js',
        'static/offline/styles.css'
    ]
    
    missing_files = []
    for file in offline_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"{Fore.YELLOW}Uyarı: Aşağıdaki çevrimdışı mod dosyaları eksik:{Style.RESET_ALL}")
        for file in missing_files:
            print(f"{Fore.YELLOW}  - {file}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Tüm çevrimdışı mod dosyaları mevcut.{Style.RESET_ALL}")
    
    return len(missing_files) == 0

def check_ai_ml_components():
    """
    Yapay zeka ve makine öğrenmesi bileşenlerini kontrol eder.
    """
    print(f"\n{Fore.CYAN}Yapay zeka ve makine öğrenmesi bileşenleri kontrol ediliyor...{Style.RESET_ALL}")
    
    # AI ve ML kütüphanelerinin varlığını kontrol et
    ai_ml_packages = [
        'openai',
        'langchain',
        'scikit-learn',
        'tensorflow',
        'pytorch',
        'spacy'
    ]
    
    missing_packages = []
    for package in ai_ml_packages:
        try:
            pkg_resources.require(package)
            print(f"{Fore.GREEN}✓ {package} yüklü.{Style.RESET_ALL}")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            missing_packages.append(package)
            print(f"{Fore.YELLOW}✗ {package} eksik.{Style.RESET_ALL}")
    
    # AI modellerinin varlığını kontrol et
    model_files = [
        'ai_assistant/models/chat_model',
        'ai_assistant/models/classification_model',
        'ai_assistant/models/recommendation_model'
    ]
    
    missing_models = []
    for model in model_files:
        if not os.path.exists(model):
            missing_models.append(model)
    
    if missing_models:
        print(f"{Fore.YELLOW}Uyarı: Aşağıdaki AI modelleri eksik:{Style.RESET_ALL}")
        for model in missing_models:
            print(f"{Fore.YELLOW}  - {model}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Tüm AI modelleri mevcut.{Style.RESET_ALL}")
    
    return len(missing_packages) == 0 and len(missing_models) == 0

def check_blockchain_components():
    """
    Blockchain bileşenlerini kontrol eder.
    """
    print(f"\n{Fore.CYAN}Blockchain bileşenleri kontrol ediliyor...{Style.RESET_ALL}")
    
    # Blockchain kütüphanelerinin varlığını kontrol et
    blockchain_packages = [
        'web3',
        'eth-account',
        'eth-typing',
        'eth-utils'
    ]
    
    missing_packages = []
    for package in blockchain_packages:
        try:
            pkg_resources.require(package)
            print(f"{Fore.GREEN}✓ {package} yüklü.{Style.RESET_ALL}")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            missing_packages.append(package)
            print(f"{Fore.YELLOW}✗ {package} eksik.{Style.RESET_ALL}")
    
    # Smart contract dosyalarının varlığını kontrol et
    contract_files = [
        'blockchain/contracts/FinasisToken.sol',
        'blockchain/contracts/FinasisMarketplace.sol',
        'blockchain/contracts/FinasisEducation.sol'
    ]
    
    missing_contracts = []
    for contract in contract_files:
        if not os.path.exists(contract):
            missing_contracts.append(contract)
    
    if missing_contracts:
        print(f"{Fore.YELLOW}Uyarı: Aşağıdaki smart contract dosyaları eksik:{Style.RESET_ALL}")
        for contract in missing_contracts:
            print(f"{Fore.YELLOW}  - {contract}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Tüm smart contract dosyaları mevcut.{Style.RESET_ALL}")
    
    return len(missing_packages) == 0 and len(missing_contracts) == 0

def check_mobile_components():
    """
    Mobil uygulama bileşenlerini kontrol eder.
    """
    print(f"\n{Fore.CYAN}Mobil uygulama bileşenleri kontrol ediliyor...{Style.RESET_ALL}")
    
    # React Native projesinin varlığını kontrol et
    if os.path.exists('FinasisMobile'):
        print(f"{Fore.GREEN}React Native projesi mevcut.{Style.RESET_ALL}")
        
        # package.json dosyasının varlığını kontrol et
        if os.path.exists('FinasisMobile/package.json'):
            print(f"{Fore.GREEN}package.json dosyası mevcut.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Uyarı: package.json dosyası bulunamadı.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Uyarı: React Native projesi bulunamadı.{Style.RESET_ALL}")
    
    # Offline mod için gerekli dosyaların varlığını kontrol et
    offline_files = [
        'FinasisMobile/src/offline/index.js',
        'FinasisMobile/src/offline/App.js',
        'FinasisMobile/src/offline/styles.js'
    ]
    
    missing_files = []
    for file in offline_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"{Fore.YELLOW}Uyarı: Aşağıdaki mobil çevrimdışı mod dosyaları eksik:{Style.RESET_ALL}")
        for file in missing_files:
            print(f"{Fore.YELLOW}  - {file}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Tüm mobil çevrimdışı mod dosyaları mevcut.{Style.RESET_ALL}")
    
    return len(missing_files) == 0

def check_education_components():
    """
    Eğitim modülü bileşenlerini kontrol eder.
    """
    print(f"\n{Fore.CYAN}Eğitim modülü bileşenleri kontrol ediliyor...{Style.RESET_ALL}")
    
    # Eğitim modülünün varlığını kontrol et
    if os.path.exists('education'):
        print(f"{Fore.GREEN}Eğitim modülü mevcut.{Style.RESET_ALL}")
        
        # Eğitim içeriklerinin varlığını kontrol et
        content_files = [
            'education/templates/education/courses.html',
            'education/templates/education/lessons.html',
            'education/templates/education/quizzes.html'
        ]
        
        missing_files = []
        for file in content_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"{Fore.YELLOW}Uyarı: Aşağıdaki eğitim içerik dosyaları eksik:{Style.RESET_ALL}")
            for file in missing_files:
                print(f"{Fore.YELLOW}  - {file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Tüm eğitim içerik dosyaları mevcut.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Uyarı: Eğitim modülü bulunamadı.{Style.RESET_ALL}")
    
    return True

def check_game_components():
    """
    Oyun modülü bileşenlerini kontrol eder.
    """
    print(f"\n{Fore.CYAN}Oyun modülü bileşenleri kontrol ediliyor...{Style.RESET_ALL}")
    
    # Oyun modülünün varlığını kontrol et
    if os.path.exists('game_app'):
        print(f"{Fore.GREEN}Oyun modülü mevcut.{Style.RESET_ALL}")
        
        # Oyun içeriklerinin varlığını kontrol et
        content_files = [
            'game_app/templates/game_app/games.html',
            'game_app/templates/game_app/leaderboard.html',
            'game_app/templates/game_app/achievements.html'
        ]
        
        missing_files = []
        for file in content_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"{Fore.YELLOW}Uyarı: Aşağıdaki oyun içerik dosyaları eksik:{Style.RESET_ALL}")
            for file in missing_files:
                print(f"{Fore.YELLOW}  - {file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Tüm oyun içerik dosyaları mevcut.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Uyarı: Oyun modülü bulunamadı.{Style.RESET_ALL}")
    
    return True

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
    
    # Çevrimdışı mod ayarlarını kontrol et
    offline_ok = check_offline_mode()
    
    # AI ve ML bileşenlerini kontrol et
    ai_ml_ok = check_ai_ml_components()
    
    # Blockchain bileşenlerini kontrol et
    blockchain_ok = check_blockchain_components()
    
    # Mobil bileşenleri kontrol et
    mobile_ok = check_mobile_components()
    
    # Eğitim bileşenlerini kontrol et
    education_ok = check_education_components()
    
    # Oyun bileşenlerini kontrol et
    game_ok = check_game_components()
    
    # Sonuçları göster
    print(f"\n{Fore.CYAN}=========================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}        KONTROL SONUÇLARI{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}")
    
    print(f"Paketler: {'✓' if packages_ok else '✗'}")
    print(f"Django Ayarları: {'✓' if django_ok else '✗'}")
    print(f".env Dosyası: {'✓' if env_ok else '✗'}")
    print(f"Çevrimdışı Mod: {'✓' if offline_ok else '✗'}")
    print(f"AI ve ML Bileşenleri: {'✓' if ai_ml_ok else '✗'}")
    print(f"Blockchain Bileşenleri: {'✓' if blockchain_ok else '✗'}")
    print(f"Mobil Bileşenler: {'✓' if mobile_ok else '✗'}")
    print(f"Eğitim Bileşenleri: {'✓' if education_ok else '✗'}")
    print(f"Oyun Bileşenleri: {'✓' if game_ok else '✗'}")
    
    # Genel durum
    if packages_ok and django_ok and env_ok:
        print(f"\n{Fore.GREEN}Temel kontroller başarılı! Proje çalışmaya hazır.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}Bazı temel kontroller başarısız oldu. Lütfen yukarıdaki uyarıları dikkate alın.{Style.RESET_ALL}")
    
    # Çalışma süresini göster
    elapsed_time = time.time() - start_time
    print(f"\n{Fore.CYAN}Kontrol süresi: {elapsed_time:.2f} saniye{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 