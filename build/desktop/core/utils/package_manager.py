#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paket Yönetim Sistemi
---------------------
Bu modül, projenin bağımlılıklarını yönetir ve eksik paketleri otomatik olarak yükler.
"""

import pkg_resources
import subprocess
from pathlib import Path

# Proje kök dizinini belirle
PROJECT_ROOT = Path(__file__).parent.parent.parent

def install_missing_packages(requirements_file=None):
    """
    requirements.txt dosyasındaki eksik paketleri yükler.
    
    Args:
        requirements_file (str, optional): requirements.txt dosyasının yolu.
            Varsayılan olarak proje kök dizinindeki requirements.txt kullanılır.
    """
    if requirements_file is None:
        requirements_file = PROJECT_ROOT / 'requirements.txt'
    else:
        requirements_file = Path(requirements_file)
    
    try:
        with open(requirements_file, 'r') as f:
            packages = f.read().splitlines()

        for package in packages:
            # Boş satırları ve yorumları atla
            if not package.strip() or package.startswith('#'):
                continue
                
            try:
                pkg_resources.require(package)
                print(f"{package} zaten yüklü.")
            except pkg_resources.DistributionNotFound:
                print(f"{package} eksik, yükleniyor...")
                subprocess.check_call(["pip", "install", package])
            except pkg_resources.VersionConflict as e:
                print(f"{package} için versiyon uyuşmazlığı: {e}. Güncelleniyor...")
                subprocess.check_call(["pip", "install", "--upgrade", package])
    except FileNotFoundError:
        print(f"'{requirements_file}' dosyası bulunamadı.")
    except Exception as e:
        print(f"Paket yükleme sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    install_missing_packages() 