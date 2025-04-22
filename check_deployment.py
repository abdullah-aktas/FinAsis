#!/usr/bin/env python
"""
Bu script projenin canlı ortama geçiş için gerekli kontrolleri yapar.
- Yapılandırma dosyalarını kontrol eder
- Güvenlik ayarlarını kontrol eder
- Veritabanı migrasyonlarını kontrol eder
- URL yapılandırmalarını kontrol eder
- Statik dosyaları kontrol eder
- API endpoint'lerini kontrol eder
- Çeşitli diğer hazırlık kontrollerini yapar
"""
import os
import re
import sys
import logging
import importlib
from pathlib import Path
import subprocess
import json

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deployment_check.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
BASE_DIR = Path(__file__).resolve().parent

def run_command(command):
    """
    Sistem komutu çalıştırır ve sonucunu döndürür
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_settings_security():
    """
    Güvenlik ayarlarını kontrol eder
    """
    logger.info("\n📋 Güvenlik Ayarlarını Kontrol Ediliyor...")
    
    try:
        from config.settings.base import SECRET_KEY, DEBUG, ALLOWED_HOSTS
        from config.settings.prod import SECRET_KEY as PROD_SECRET_KEY
        
        # Secret Key kontrolü
        if 'insecure' in SECRET_KEY or 'django-insecure' in SECRET_KEY:
            logger.warning("⚠️ Dev ortamında güvensiz bir SECRET_KEY kullanılıyor.")
        
        if os.environ.get('DJANGO_SECRET_KEY') is None:
            logger.warning("⚠️ DJANGO_SECRET_KEY çevre değişkeni tanımlanmamış.")
        
        if PROD_SECRET_KEY == SECRET_KEY:
            logger.warning("⚠️ Production ve development ortamları aynı SECRET_KEY'i kullanıyor.")
        
        # DEBUG modu kontrolü
        if DEBUG:
            logger.warning("⚠️ DEBUG modu açık! Canlı ortamda kapatılmalı.")
        
        # ALLOWED_HOSTS kontrolü
        if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['*']:
            logger.warning("⚠️ ALLOWED_HOSTS güvenli ayarlanmamış. Canlı ortamda belirli domain'lere izin verilmeli.")
        
        logger.info("✅ Güvenlik ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Ayar dosyası yüklenirken hata: {e}")
        return False
    
    return True

def check_database_settings():
    """
    Veritabanı ayarlarını kontrol eder
    """
    logger.info("\n📋 Veritabanı Ayarlarını Kontrol Ediliyor...")
    
    try:
        from config.settings.base import DATABASES
        from config.settings.prod import DATABASES as PROD_DATABASES
        
        # Veritabanı engine kontrolü
        if PROD_DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
            logger.warning("⚠️ Canlı ortamda PostgreSQL kullanılması önerilir.")
        
        # Bağlantı ayarları kontrolü
        if 'CONN_MAX_AGE' not in PROD_DATABASES['default'] or PROD_DATABASES['default']['CONN_MAX_AGE'] is None:
            logger.warning("⚠️ CONN_MAX_AGE ayarlanmamış. Performans için ayarlanması önerilir.")
        
        # Veritabanı kullanıcı adı güvenliği
        if PROD_DATABASES['default'].get('USER') in ['postgres', 'root', 'admin']:
            logger.warning("⚠️ Varsayılan veritabanı kullanıcı adı kullanılıyor. Güvenlik için değiştirilmeli.")
        
        logger.info("✅ Veritabanı ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Veritabanı ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_static_files():
    """
    Statik dosya ayarlarını kontrol eder
    """
    logger.info("\n📋 Statik Dosya Ayarlarını Kontrol Ediliyor...")
    
    try:
        from config.settings.base import STATIC_URL, STATIC_ROOT, STATICFILES_DIRS
        
        # STATIC_ROOT kontrolü
        if not STATIC_ROOT:
            logger.warning("⚠️ STATIC_ROOT tanımlanmamış. Canlı ortamda gereklidir.")
        
        # STATICFILES_DIRS kontrolü
        if not STATICFILES_DIRS:
            logger.warning("⚠️ STATICFILES_DIRS tanımlanmamış. Özel statik dosyalar var mı?")
        
        # Statik dosyaların varlığı kontrolü
        if not os.path.exists(STATIC_ROOT):
            logger.warning(f"⚠️ STATIC_ROOT dizini ({STATIC_ROOT}) bulunamadı. 'collectstatic' çalıştırılmalı.")
        
        # Whitenoise kontrolü
        from config.settings.base import MIDDLEWARE
        if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
            logger.warning("⚠️ WhiteNoiseMiddleware MIDDLEWARE listesinde bulunamadı. Statik dosyalar için önerilir.")
        
        logger.info("✅ Statik dosya ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Statik dosya ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_installed_apps():
    """
    Yüklü uygulamaları kontrol eder
    """
    logger.info("\n📋 Yüklü Uygulamalar Kontrol Ediliyor...")
    
    try:
        from config.settings.base import INSTALLED_APPS
        
        # Debug araçlarının kontrolü
        debug_apps = ['debug_toolbar', 'django_extensions']
        for app in debug_apps:
            if app in INSTALLED_APPS:
                logger.warning(f"⚠️ Debug aracı '{app}' INSTALLED_APPS içinde. Canlı ortamda kaldırılmalı.")
        
        # AppConfig doğruluğu kontrolü
        invalid_apps = []
        for app in INSTALLED_APPS:
            if '..' in app:
                invalid_apps.append(app)
        
        if invalid_apps:
            logger.warning(f"⚠️ Şu uygulamaların AppConfig tanımı hatalı: {', '.join(invalid_apps)}")
        
        logger.info("✅ Yüklü uygulamalar kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Yüklü uygulamalar kontrol edilirken hata: {e}")
        return False
    
    return True

def check_migrations():
    """
    Veritabanı migrasyonlarını kontrol eder
    """
    logger.info("\n📋 Veritabanı Migrasyonlarını Kontrol Ediliyor...")
    
    # Migrate --check komutunu çalıştır
    returncode, stdout, stderr = run_command("python manage.py migrate --plan")
    
    if returncode != 0:
        logger.error(f"❌ Migration kontrolü başarısız: {stderr}")
        return False
    
    # Bekleyen migrasyon var mı?
    if "No planned migration operations" not in stdout:
        logger.warning("⚠️ Bekleyen migrasyonlar var. Canlıya almadan önce uygulanmalı.")
        logger.warning(f"Migrasyonlar: {stdout}")
    else:
        logger.info("✅ Tüm migrasyonlar uygulanmış durumda.")
    
    # Eksik migrasyon dosyaları var mı?
    returncode, stdout, stderr = run_command("python manage.py makemigrations --check")
    
    if returncode != 0:
        logger.warning("⚠️ Oluşturulmamış migration dosyaları var. Canlıya almadan önce oluşturulmalı.")
    else:
        logger.info("✅ Tüm model değişiklikleri migration dosyalarına aktarılmış.")
    
    return True

def check_url_patterns():
    """
    URL desenlerini kontrol eder
    """
    logger.info("\n📋 URL Yapılandırmasını Kontrol Ediliyor...")
    
    # URL'leri kontrol et
    returncode, stdout, stderr = run_command("python manage.py show_urls")
    
    if returncode != 0:
        logger.error(f"❌ URL'ler kontrol edilirken hata: {stderr}")
        return False
    
    # Django admin URL'i güvenli mi?
    admin_urls = []
    for line in stdout.splitlines():
        if "admin" in line and "admin/" in line:
            admin_urls.append(line.strip())
    
    if admin_urls and "admin/" in admin_urls[0]:
        logger.warning("⚠️ Django admin URL'i varsayılan (admin/). Güvenlik için değiştirmeniz önerilir.")
    
    logger.info("✅ URL yapılandırması kontrol edildi.")
    
    return True

def check_debug_settings():
    """
    Debug ayarlarını kontrol eder
    """
    logger.info("\n📋 Debug Ayarlarını Kontrol Ediliyor...")
    
    try:
        # Production settings'te DEBUG kontrolü
        sys.path.append(str(BASE_DIR))
        from config.settings.prod import DEBUG as PROD_DEBUG
        
        if PROD_DEBUG:
            logger.error("❌ Canlı ortam ayarlarında DEBUG = True! Bu mutlaka False olmalı.")
            return False
        
        # Diğer debug ayarları
        from config.settings.base import INTERNAL_IPS
        if INTERNAL_IPS and '0.0.0.0' in INTERNAL_IPS:
            logger.warning("⚠️ INTERNAL_IPS çok geniş tanımlanmış.")
        
        logger.info("✅ Debug ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Debug ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_media_files():
    """
    Media dosya ayarlarını kontrol eder
    """
    logger.info("\n📋 Media Dosya Ayarlarını Kontrol Ediliyor...")
    
    try:
        from config.settings.base import MEDIA_URL, MEDIA_ROOT
        
        # MEDIA_ROOT kontrolü
        if not MEDIA_ROOT:
            logger.warning("⚠️ MEDIA_ROOT tanımlanmamış. Canlı ortamda gereklidir.")
        
        # Media dizini var mı?
        if not os.path.exists(MEDIA_ROOT):
            logger.warning(f"⚠️ MEDIA_ROOT dizini ({MEDIA_ROOT}) bulunamadı. Oluşturulmalı.")
        else:
            # Media dizininin yazma izni var mı?
            if not os.access(MEDIA_ROOT, os.W_OK):
                logger.warning(f"⚠️ MEDIA_ROOT dizininde ({MEDIA_ROOT}) yazma izni yok!")
        
        logger.info("✅ Media dosya ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Media dosya ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_api_endpoints():
    """
    API endpoint'lerini kontrol eder
    """
    logger.info("\n📋 API Endpoint'leri Kontrol Ediliyor...")
    
    # API modülü var mı?
    api_dir = os.path.join(BASE_DIR, 'api')
    if not os.path.exists(api_dir) or not os.path.isdir(api_dir):
        logger.info("ℹ️ API modülü bulunamadı, API endpoint'leri kontrol edilmiyor.")
        return True
    
    # API URL'leri kontrol et
    returncode, stdout, stderr = run_command("python manage.py show_urls | grep api")
    
    if returncode != 0 and returncode != 1:  # grep komutunda eşleşme olmazsa 1 döner
        logger.error(f"❌ API URL'leri kontrol edilirken hata: {stderr}")
        return False
    
    # API throttling ayarları kontrol et
    try:
        from config.settings.base import REST_FRAMEWORK
        
        if 'DEFAULT_THROTTLE_CLASSES' not in REST_FRAMEWORK or not REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES']:
            logger.warning("⚠️ API throttling tanımlanmamış. DDoS saldırılarına karşı koruma için önerilir.")
        
        logger.info("✅ API endpoint'leri kontrol edildi.")
        
    except (ImportError, KeyError) as e:
        logger.error(f"❌ API ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_template_settings():
    """
    Template ayarlarını kontrol eder
    """
    logger.info("\n📋 Template Ayarlarını Kontrol Ediliyor...")
    
    try:
        from config.settings.base import TEMPLATES
        
        # Template dizinleri var mı?
        for engine in TEMPLATES:
            if engine['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
                for template_dir in engine.get('DIRS', []):
                    if not os.path.exists(template_dir):
                        logger.warning(f"⚠️ Template dizini ({template_dir}) bulunamadı.")
        
        logger.info("✅ Template ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Template ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_requirements():
    """
    Gerekli paketleri kontrol eder
    """
    logger.info("\n📋 Gerekli Paketleri Kontrol Ediliyor...")
    
    # requirements.txt var mı?
    req_file = os.path.join(BASE_DIR, 'requirements.txt')
    if not os.path.exists(req_file):
        logger.error("❌ requirements.txt dosyası bulunamadı!")
        return False
    
    # requirements.txt içeriğini kontrol et
    with open(req_file, 'r') as f:
        requirements = f.read()
    
    # Debug paketleri var mı?
    debug_packages = ['django-debug-toolbar', 'django-extensions', 'ipython', 'werkzeug']
    for package in debug_packages:
        if package in requirements and '#' + package not in requirements:
            logger.warning(f"⚠️ Debug paketi '{package}' requirements.txt'de aktif. Canlı ortamda kaldırılmalı.")
    
    # Güvenlik paketleri var mı?
    security_packages = ['django-cors-headers', 'django-csp', 'django-permissions-policy']
    missing_security = []
    for package in security_packages:
        if package not in requirements:
            missing_security.append(package)
    
    if missing_security:
        logger.warning(f"⚠️ Güvenlik paketleri eksik: {', '.join(missing_security)}")
    
    logger.info("✅ Gerekli paketler kontrol edildi.")
    
    return True

def check_logging_settings():
    """
    Loglama ayarlarını kontrol eder
    """
    logger.info("\n📋 Loglama Ayarlarını Kontrol Ediliyor...")
    
    try:
        from config.settings.base import LOGGING
        
        # Log dizini var mı?
        log_dir = os.path.join(BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            logger.warning(f"⚠️ Log dizini ({log_dir}) bulunamadı. Oluşturulmalı.")
        
        # File handler tanımlı mı?
        has_file_handler = False
        for handler_name, handler in LOGGING.get('handlers', {}).items():
            if handler.get('class') == 'logging.FileHandler' or handler.get('class') == 'logging.handlers.RotatingFileHandler':
                has_file_handler = True
                
                # Log dosyasının dizini var mı?
                log_file = handler.get('filename')
                if log_file and not os.path.exists(os.path.dirname(log_file)):
                    logger.warning(f"⚠️ Log dosyası ({log_file}) için dizin bulunamadı.")
        
        if not has_file_handler:
            logger.warning("⚠️ Dosya log handler'ı tanımlanmamış. Canlı ortamda önerilir.")
        
        logger.info("✅ Loglama ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Loglama ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def create_deployment_report():
    """
    Canlıya alma kontrollerini çalıştırır ve bir rapor oluşturur
    """
    success = True
    
    logger.info("🔍 CANLI ORTAM HAZIRLIK KONTROLÜ")
    logger.info("===============================")
    logger.info(f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    logger.info(f"Proje Dizini: {BASE_DIR}")
    
    # Güvenlik ayarları
    if not check_settings_security():
        success = False
    
    # Veritabanı ayarları
    if not check_database_settings():
        success = False
    
    # Statik dosya ayarları
    if not check_static_files():
        success = False
    
    # Yüklü uygulamalar
    if not check_installed_apps():
        success = False
    
    # Migrasyonlar
    if not check_migrations():
        success = False
    
    # URL desenleri
    if not check_url_patterns():
        success = False
    
    # Debug ayarları
    if not check_debug_settings():
        success = False
    
    # Media dosya ayarları
    if not check_media_files():
        success = False
    
    # API endpoint'leri
    if not check_api_endpoints():
        success = False
    
    # Template ayarları
    if not check_template_settings():
        success = False
    
    # Gerekli paketler
    if not check_requirements():
        success = False
    
    # Loglama ayarları
    if not check_logging_settings():
        success = False
    
    # Sonuç
    if success:
        logger.info("\n✅ HAZIRIZ! Tüm kontroller başarıyla tamamlandı.")
        logger.info("Projenizi canlı ortama alabilirsiniz.")
    else:
        logger.warning("\n⚠️ DİKKAT! Bazı kontroller başarısız oldu.")
        logger.warning("Yukarıdaki uyarıları dikkate alarak gerekli düzeltmeleri yapın ve testi tekrarlayın.")
    
    # HTML rapor oluştur
    html_report = generate_html_report()
    with open("deployment_report.html", "w") as f:
        f.write(html_report)
    
    logger.info(f"\nDetaylı rapor 'deployment_report.html' dosyasına kaydedildi.")
    logger.info(f"Log dosyası 'deployment_check.log' içinde bulunabilir.\n")

def generate_html_report():
    """
    HTML formatında rapor oluşturur
    """
    html = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinAsis Canlı Ortam Hazırlık Raporu</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #2c3e50; margin-top: 30px; }
        .success { color: #27ae60; }
        .warning { color: #f39c12; }
        .error { color: #e74c3c; }
        .info { color: #3498db; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow: auto; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
        .footer { margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px; font-size: 0.9em; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FinAsis Canlı Ortam Hazırlık Raporu</h1>
        <p><strong>Tarih:</strong> """ + datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S') + """</p>
        <p><strong>Proje Dizini:</strong> """ + str(BASE_DIR) + """</p>
        
        <h2>Güvenlik Ayarları</h2>
        <p>Güvenlik ayarlarınızı canlı ortama geçmeden önce gözden geçirin:</p>
        <ul>
            <li>SECRET_KEY güvenli ve ortama özgü olmalı</li>
            <li>DEBUG modu kapalı olmalı</li>
            <li>ALLOWED_HOSTS doğru yapılandırılmalı</li>
            <li>CSRF ve güvenlik ayarları kontrol edilmeli</li>
        </ul>
        
        <h2>Veritabanı</h2>
        <p>Veritabanı migrasyonlarınızı kontrol edin:</p>
        <pre>python manage.py migrate --plan</pre>
        <p>Tüm modellerin migrasyon dosyaları oluşturulmuş olmalıdır:</p>
        <pre>python manage.py makemigrations --check</pre>
        
        <h2>Statik Dosyalar</h2>
        <p>Statik dosyalarınızı toplayın:</p>
        <pre>python manage.py collectstatic</pre>
        
        <h2>Gerekli Kontrol Listesi</h2>
        <table>
            <tr>
                <th>Kontrol</th>
                <th>Durum</th>
                <th>Açıklama</th>
            </tr>
            <tr>
                <td>DEBUG = False</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Production settings'te DEBUG = False olmalı</td>
            </tr>
            <tr>
                <td>SECRET_KEY</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Güvenli ve ortama özgü olmalı</td>
            </tr>
            <tr>
                <td>ALLOWED_HOSTS</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Sadece izin verilen domainler listede olmalı</td>
            </tr>
            <tr>
                <td>Veritabanı Migrasyonları</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Tüm migrasyonlar uygulanmış olmalı</td>
            </tr>
            <tr>
                <td>Statik Dosyalar</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>collectstatic çalıştırılmış olmalı</td>
            </tr>
            <tr>
                <td>Media Dizini</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Dizin oluşturulmuş ve yazma izni verilmiş olmalı</td>
            </tr>
            <tr>
                <td>Gereksiz Paketler</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Debug araçları kaldırılmış olmalı</td>
            </tr>
            <tr>
                <td>Loglama</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Dosya loglama etkinleştirilmiş olmalı</td>
            </tr>
            <tr>
                <td>API Güvenliği</td>
                <td class="warning">⚠️ Kontrol Edilmeli</td>
                <td>Throttling ve diğer güvenlik önlemleri alınmış olmalı</td>
            </tr>
        </table>
        
        <h2>Öneriler</h2>
        <ul>
            <li>Düzenli backup planı oluşturun</li>
            <li>Monitoring ve alarm sistemleri kurun</li>
            <li>Güvenlik testleri yapın</li>
            <li>SSL/TLS sertifikalarını yapılandırın</li>
            <li>Yük testi yapın</li>
        </ul>
        
        <div class="footer">
            <p>Bu rapor otomatik olarak oluşturulmuştur. Daha detaylı bilgi için log dosyasını inceleyebilirsiniz.</p>
        </div>
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    create_deployment_report() 