# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Django yönetim komutları için komut satırı aracı.
Bu dosya, Django projesinin yönetim komutlarını çalıştırmak için kullanılır.
"""

import os
import sys
from pathlib import Path
from typing import NoReturn
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def setup_environment() -> None:
    """Ortam değişkenlerini ve Django ayarlarını yapılandırır."""
    try:
        # Proje kök dizinini belirle
        project_root = Path(__file__).resolve().parent
        os.chdir(project_root)
        # logger.info(f"Proje dizini: {project_root}")

        # Django ayarlarını yapılandır
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinAsis.settings')
        
        # Python yolunu ayarla
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            
        # logger.info("Ortam değişkenleri başarıyla yapılandırıldı")
    except Exception as e:
        # logger.error(f"Ortam yapılandırma hatası: {str(e)}")
        sys.exit(1)

def check_dependencies() -> None:
    """Gerekli bağımlılıkların varlığını kontrol eder."""
    try:
        import django
        # logger.info(f"Django sürümü: {django.get_version()}")
    except ImportError:
        # logger.error(
        #     "Django bulunamadı. Lütfen şunları kontrol edin:\n"
        #     "1. Django yüklü mü?\n"
        #     "2. PYTHONPATH ortam değişkeni doğru ayarlanmış mı?\n"
        #     "3. Sanal ortam aktif mi?"
        # )
        sys.exit(1)

def execute_command() -> NoReturn:
    """Django yönetim komutunu çalıştırır."""
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
        sys.exit(0)  # Başarılı çalışma durumunda çıkış
    except Exception as e:
        # logger.error(f"Komut çalıştırma hatası: {str(e)}")
        sys.exit(1)

def main() -> NoReturn:
    """Ana fonksiyon."""
    try:
        setup_environment()
        check_dependencies()
        execute_command()
    except KeyboardInterrupt:
        # logger.info("Program kullanıcı tarafından sonlandırıldı")
        sys.exit(0)
    except Exception as e:
        # logger.error(f"Beklenmeyen hata: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
