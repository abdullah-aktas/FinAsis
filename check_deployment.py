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
import datetime
import subprocess
import json
import time
from pathlib import Path
from typing import Tuple, Dict, List, Any

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

def run_command(command: str) -> Tuple[int, str, str]:
    """
    Sistem komutu çalıştırır ve sonucunu döndürür
    
    Args:
        command: Çalıştırılacak komut
        
    Returns:
        Tuple[int, str, str]: (returncode, stdout, stderr)
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Komut çalıştırma hatası: {e}")
        return -1, "", str(e)

def check_settings_security() -> bool:
    """
    Güvenlik ayarlarını kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
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
        
        # Güvenlik başlıkları kontrolü
        from config.settings.base import MIDDLEWARE
        security_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'corsheaders.middleware.CorsMiddleware',
        ]
        
        missing_middleware = [mw for mw in security_middleware if mw not in MIDDLEWARE]
        if missing_middleware:
            logger.warning(f"⚠️ Eksik güvenlik middleware'leri: {', '.join(missing_middleware)}")
        
        logger.info("✅ Güvenlik ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Ayar dosyası yüklenirken hata: {e}")
        return False
    
    return True

def check_database_settings() -> bool:
    """
    Veritabanı ayarlarını kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
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
        
        # Veritabanı şifreleme kontrolü
        if not PROD_DATABASES['default'].get('OPTIONS', {}).get('sslmode', ''):
            logger.warning("⚠️ SSL modu ayarlanmamış. Veritabanı bağlantısı şifrelenmeli.")
        
        logger.info("✅ Veritabanı ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Veritabanı ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_static_files() -> bool:
    """
    Statik dosya ayarlarını kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
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
        
        # CDN kontrolü
        if not STATIC_URL.startswith('https://'):
            logger.warning("⚠️ STATIC_URL HTTPS ile başlamıyor. CDN kullanımı önerilir.")
        
        logger.info("✅ Statik dosya ayarları kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Statik dosya ayarları kontrol edilirken hata: {e}")
        return False
    
    return True

def check_installed_apps() -> bool:
    """
    Yüklü uygulamaları kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
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
        
        # Güvenlik uygulamaları kontrolü
        security_apps = [
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'corsheaders',
            'axes',
        ]
        
        missing_security = [app for app in security_apps if app not in INSTALLED_APPS]
        if missing_security:
            logger.warning(f"⚠️ Eksik güvenlik uygulamaları: {', '.join(missing_security)}")
        
        logger.info("✅ Yüklü uygulamalar kontrol edildi.")
        
    except ImportError as e:
        logger.error(f"❌ Yüklü uygulamalar kontrol edilirken hata: {e}")
        return False
    
    return True

def check_migrations() -> bool:
    """
    Veritabanı migrasyonlarını kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
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

def check_debug_settings() -> bool:
    """
    Debug ayarlarını kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n📋 Debug Ayarlarını Kontrol Ediliyor...")
    
    try:
        # Production settings'te DEBUG kontrolü
        sys.path.append(str(BASE_DIR))
        from config.settings.prod import DEBUG as PROD_DEBUG
        
        if PROD_DEBUG:
            logger.error("❌ Canlı ortam ayarlarında DEBUG = True! Bu mutlaka False olmalı.")
            return False
        
        # Debug araçlarının kontrolü
        try:
            from config.settings.base import INSTALLED_APPS
            debug_apps = ['debug_toolbar', 'django_extensions']
            for app in debug_apps:
                if app in INSTALLED_APPS:
                    logger.warning(f"⚠️ Debug aracı '{app}' INSTALLED_APPS içinde. Canlı ortamda kaldırılmalı.")
        except ImportError:
            logger.info("ℹ️ INSTALLED_APPS ayarı bulunamadı, debug araçları kontrolü atlanıyor.")
        
        # Debug middleware kontrolü
        try:
            from config.settings.base import MIDDLEWARE
            debug_middleware = [
                'debug_toolbar.middleware.DebugToolbarMiddleware',
                'django.contrib.admindocs.middleware.XViewMiddleware'
            ]
            for mw in debug_middleware:
                if mw in MIDDLEWARE:
                    logger.warning(f"⚠️ Debug middleware '{mw}' aktif. Canlı ortamda kaldırılmalı.")
        except ImportError:
            logger.info("ℹ️ MIDDLEWARE ayarı bulunamadı, debug middleware kontrolü atlanıyor.")
        
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

def check_docker_containers() -> bool:
    """
    Docker konteynerlerini kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n📋 Docker Konteynerleri Kontrol Ediliyor...")
    
    try:
        # Docker servis durumu
        returncode, stdout, stderr = run_command("docker info")
        if returncode != 0:
            logger.error("❌ Docker servisi çalışmıyor!")
            return False
        
        # Konteyner durumları
        returncode, stdout, stderr = run_command("docker ps -a")
        if returncode != 0:
            logger.error("❌ Docker konteynerleri listelenemedi!")
            return False
        
        # Gerekli konteynerler
        required_containers = ['web', 'db', 'redis', 'nginx']
        running_containers = [line.split()[-1] for line in stdout.splitlines()[1:]]
        
        # Eksik konteynerler
        missing_containers = [cont for cont in required_containers if cont not in running_containers]
        if missing_containers:
            logger.warning(f"⚠️ Eksik konteynerler: {', '.join(missing_containers)}")
        
        # Konteyner sağlık durumları
        for container in running_containers:
            returncode, stdout, stderr = run_command(f"docker inspect --format='{{{{.State.Health.Status}}}}' {container}")
            if returncode == 0 and stdout.strip() != "healthy":
                logger.warning(f"⚠️ {container} konteyneri sağlıklı değil!")
        
        # Konteyner kaynak kullanımı
        returncode, stdout, stderr = run_command("docker stats --no-stream")
        if returncode == 0:
            for line in stdout.splitlines()[1:]:
                container, cpu, mem, _ = line.split()[:4]
                if float(cpu.replace('%', '')) > 80:
                    logger.warning(f"⚠️ {container} yüksek CPU kullanıyor: {cpu}")
                if float(mem.replace('%', '')) > 80:
                    logger.warning(f"⚠️ {container} yüksek bellek kullanıyor: {mem}")
        
        logger.info("✅ Docker konteynerleri kontrol edildi.")
        
    except Exception as e:
        logger.error(f"❌ Docker kontrolü sırasında hata: {e}")
        return False
    
    return True

def check_ssl_certificates() -> bool:
    """
    SSL sertifikalarını kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n📋 SSL Sertifikaları Kontrol Ediliyor...")
    
    try:
        # Sertifika dizini kontrolü
        cert_dir = "/etc/letsencrypt/live"
        if not os.path.exists(cert_dir):
            logger.error("❌ SSL sertifika dizini bulunamadı!")
            return False
        
        # Sertifika dosyaları
        cert_files = {
            "fullchain.pem": "Sertifika zinciri",
            "privkey.pem": "Özel anahtar",
            "cert.pem": "Sertifika",
            "chain.pem": "Ara sertifika"
        }
        
        # Her domain için sertifika kontrolü
        for domain in os.listdir(cert_dir):
            domain_path = os.path.join(cert_dir, domain)
            if not os.path.isdir(domain_path):
                continue
            
            logger.info(f"\n🔍 {domain} domain'i için sertifika kontrolü:")
            
            # Sertifika dosyalarını kontrol et
            for file, desc in cert_files.items():
                file_path = os.path.join(domain_path, file)
                if not os.path.exists(file_path):
                    logger.warning(f"⚠️ {desc} dosyası bulunamadı: {file_path}")
                    continue
                
                # Dosya izinlerini kontrol et
                if file == "privkey.pem":
                    mode = os.stat(file_path).st_mode
                    if mode & 0o777 != 0o600:
                        logger.warning(f"⚠️ Özel anahtar dosyası izinleri güvenli değil: {oct(mode)}")
            
            # Sertifika geçerlilik süresini kontrol et
            returncode, stdout, stderr = run_command(f"openssl x509 -in {os.path.join(domain_path, 'cert.pem')} -noout -enddate")
            if returncode == 0:
                expiry_date = stdout.split('=')[1].strip()
                logger.info(f"✅ Sertifika son kullanma tarihi: {expiry_date}")
                
                # 30 günden az kaldıysa uyarı ver
                from datetime import datetime
                expiry = datetime.strptime(expiry_date, "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry - datetime.now()).days
                if days_left < 30:
                    logger.warning(f"⚠️ Sertifikanın süresi dolmak üzere! Kalan gün: {days_left}")
        
        logger.info("✅ SSL sertifikaları kontrol edildi.")
        
    except Exception as e:
        logger.error(f"❌ SSL sertifika kontrolü sırasında hata: {e}")
        return False
    
    return True

def collect_performance_metrics() -> bool:
    """
    Performans metriklerini toplar
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n📊 Performans Metrikleri Toplanıyor...")
    
    try:
        metrics = {
            "web": {},
            "db": {},
            "redis": {},
            "system": {}
        }
        
        # Web sunucusu metrikleri
        returncode, stdout, stderr = run_command("curl -s http://localhost/health/")
        if returncode == 0:
            try:
                health_data = json.loads(stdout)
                metrics["web"].update(health_data)
            except json.JSONDecodeError:
                logger.warning("⚠️ Health endpoint'inden JSON parse edilemedi")
        
        # Veritabanı metrikleri
        returncode, stdout, stderr = run_command("docker-compose exec db psql -U postgres -c \"SELECT * FROM pg_stat_database WHERE datname = 'finasis';\"")
        if returncode == 0:
            # PostgreSQL metriklerini parse et
            pass  # TODO: PostgreSQL metriklerini parse et
        
        # Redis metrikleri
        returncode, stdout, stderr = run_command("docker-compose exec redis redis-cli info")
        if returncode == 0:
            for line in stdout.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    metrics["redis"][key] = value
        
        # Sistem metrikleri
        returncode, stdout, stderr = run_command("top -bn1")
        if returncode == 0:
            # CPU ve bellek kullanımını parse et
            pass  # TODO: Sistem metriklerini parse et
        
        # Metrikleri kaydet
        with open("performance_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        logger.info("✅ Performans metrikleri toplandı ve kaydedildi.")
        
    except Exception as e:
        logger.error(f"❌ Performans metrikleri toplanırken hata: {e}")
        return False
    
    return True

def apply_fixes(suggestions: Dict[str, List[str]]) -> bool:
    """
    Otomatik düzeltme komutlarını uygular
    
    Args:
        suggestions: Düzeltme önerileri
        
    Returns:
        bool: Tüm düzeltmeler başarılı mı?
    """
    logger.info("\n🛠️ Otomatik Düzeltmeler Uygulanıyor...")
    success = True
    
    try:
        # Güvenlik düzeltmeleri
        if "Ortam değişkenleri dosyası (.env) oluşturulmalı" in suggestions["güvenlik"]:
            logger.info("📝 .env dosyası oluşturuluyor...")
            with open(".env", "w") as f:
                f.write("# Güvenli ortam değişkenleri\n")
                f.write("DJANGO_SECRET_KEY=your-secret-key-here\n")
                f.write("DEBUG=False\n")
                f.write("ALLOWED_HOSTS=your-domain.com\n")
        
        # Performans düzeltmeleri
        if "Statik dosyalar toplanmalı" in suggestions["performans"]:
            logger.info("📦 Statik dosyalar toplanıyor...")
            returncode, stdout, stderr = run_command("python manage.py collectstatic --noinput")
            if returncode != 0:
                logger.error(f"❌ Statik dosyalar toplanırken hata: {stderr}")
                success = False
        
        # Docker düzeltmeleri
        if "Docker servisleri başlatılmalı" in suggestions["docker"]:
            logger.info("🐳 Docker servisleri başlatılıyor...")
            returncode, stdout, stderr = run_command("docker-compose up -d")
            if returncode != 0:
                logger.error(f"❌ Docker servisleri başlatılırken hata: {stderr}")
                success = False
        
        # SSL düzeltmeleri
        if "SSL sertifikaları oluşturulmalı" in suggestions["ssl"]:
            logger.info("🔒 SSL sertifikaları oluşturuluyor...")
            returncode, stdout, stderr = run_command("certbot --nginx -d your-domain.com")
            if returncode != 0:
                logger.error(f"❌ SSL sertifikaları oluşturulurken hata: {stderr}")
                success = False
        
        # Veritabanı düzeltmeleri
        if "Bekleyen migrasyonlar uygulanmalı" in suggestions["veritabanı"]:
            logger.info("💾 Veritabanı migrasyonları uygulanıyor...")
            returncode, stdout, stderr = run_command("python manage.py migrate")
            if returncode != 0:
                logger.error(f"❌ Migrasyonlar uygulanırken hata: {stderr}")
                success = False
        
        # Loglama düzeltmeleri
        if "Log dizini oluşturulmalı" in suggestions["loglama"]:
            logger.info("📝 Log dizini oluşturuluyor...")
            os.makedirs("logs", exist_ok=True)
        
        if success:
            logger.info("✅ Tüm düzeltmeler başarıyla uygulandı.")
        else:
            logger.warning("⚠️ Bazı düzeltmeler başarısız oldu.")
        
    except Exception as e:
        logger.error(f"❌ Düzeltmeler uygulanırken hata: {e}")
        success = False
    
    return success

def collect_extended_metrics() -> bool:
    """
    Genişletilmiş performans metriklerini toplar
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n📊 Genişletilmiş Performans Metrikleri Toplanıyor...")
    
    try:
        metrics = {
            "web": {},
            "db": {},
            "redis": {},
            "system": {},
            "network": {},
            "storage": {}
        }
        
        # Web sunucusu detaylı metrikleri
        returncode, stdout, stderr = run_command("curl -s http://localhost/metrics/")
        if returncode == 0:
            try:
                metrics_data = json.loads(stdout)
                metrics["web"].update(metrics_data)
            except json.JSONDecodeError:
                logger.warning("⚠️ Metrics endpoint'inden JSON parse edilemedi")
        
        # Veritabanı detaylı metrikleri
        db_metrics = [
            "SELECT * FROM pg_stat_database WHERE datname = 'finasis';",
            "SELECT * FROM pg_stat_user_tables;",
            "SELECT * FROM pg_stat_user_indexes;",
            "SELECT * FROM pg_stat_activity;"
        ]
        
        for query in db_metrics:
            returncode, stdout, stderr = run_command(f"docker-compose exec db psql -U postgres -c \"{query}\"")
            if returncode == 0:
                # PostgreSQL metriklerini parse et ve kaydet
                pass
        
        # Redis detaylı metrikleri
        redis_commands = [
            "INFO memory",
            "INFO clients",
            "INFO stats",
            "INFO replication"
        ]
        
        for cmd in redis_commands:
            returncode, stdout, stderr = run_command(f"docker-compose exec redis redis-cli {cmd}")
            if returncode == 0:
                for line in stdout.splitlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metrics["redis"][f"{cmd.split()[1]}_{key}"] = value
        
        # Sistem detaylı metrikleri
        system_commands = {
            "top": "top -bn1",
            "vmstat": "vmstat 1 2",
            "iostat": "iostat -x 1 2",
            "netstat": "netstat -s"
        }
        
        for name, cmd in system_commands.items():
            returncode, stdout, stderr = run_command(cmd)
            if returncode == 0:
                metrics["system"][name] = stdout
        
        # Ağ metrikleri
        network_commands = {
            "bandwidth": "vnstat -i eth0 --json",
            "connections": "netstat -an | grep ESTABLISHED | wc -l",
            "latency": "ping -c 4 google.com"
        }
        
        for name, cmd in network_commands.items():
            returncode, stdout, stderr = run_command(cmd)
            if returncode == 0:
                metrics["network"][name] = stdout
        
        # Depolama metrikleri
        storage_commands = {
            "disk_usage": "df -h",
            "inode_usage": "df -i",
            "file_count": "find / -type f | wc -l"
        }
        
        for name, cmd in storage_commands.items():
            returncode, stdout, stderr = run_command(cmd)
            if returncode == 0:
                metrics["storage"][name] = stdout
        
        # Metrikleri kaydet
        with open("extended_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        logger.info("✅ Genişletilmiş performans metrikleri toplandı ve kaydedildi.")
        
    except Exception as e:
        logger.error(f"❌ Genişletilmiş performans metrikleri toplanırken hata: {e}")
        return False
    
    return True

def run_security_scan() -> bool:
    """
    Güvenlik taraması yapar
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n🔒 Güvenlik Taraması Yapılıyor...")
    
    try:
        security_issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # Bağımlılık güvenlik taraması
        returncode, stdout, stderr = run_command("safety check")
        if returncode != 0:
            security_issues["critical"].append("Güvenlik açığı olan bağımlılıklar tespit edildi")
        
        # Kod güvenlik taraması
        returncode, stdout, stderr = run_command("bandit -r .")
        if returncode != 0:
            security_issues["high"].append("Kod güvenlik açıkları tespit edildi")
        
        # SSL/TLS güvenlik taraması
        returncode, stdout, stderr = run_command("testssl.sh your-domain.com")
        if returncode != 0:
            security_issues["medium"].append("SSL/TLS güvenlik sorunları tespit edildi")
        
        # Dosya izinleri kontrolü
        sensitive_files = [
            ".env",
            "config/settings/prod.py",
            "manage.py"
        ]
        
        for file in sensitive_files:
            if os.path.exists(file):
                mode = os.stat(file).st_mode
                if mode & 0o777 != 0o600:
                    security_issues["high"].append(f"{file} dosyasının izinleri güvenli değil")
        
        # Güvenlik raporunu kaydet
        with open("security_scan.json", "w") as f:
            json.dump(security_issues, f, indent=2)
        
        # Kritik ve yüksek öncelikli sorunları logla
        for level in ["critical", "high"]:
            for issue in security_issues[level]:
                logger.error(f"❌ {level.upper()}: {issue}")
        
        logger.info("✅ Güvenlik taraması tamamlandı.")
        
    except Exception as e:
        logger.error(f"❌ Güvenlik taraması sırasında hata: {e}")
        return False
    
    return True

def check_backups() -> bool:
    """
    Yedekleme durumunu kontrol eder
    
    Returns:
        bool: Kontrol başarılı mı?
    """
    logger.info("\n💾 Yedekleme Durumu Kontrol Ediliyor...")
    
    try:
        backup_status = {
            "database": {},
            "files": {},
            "config": {}
        }
        
        # Veritabanı yedekleri
        backup_dir = "/backups/database"
        if os.path.exists(backup_dir):
            db_backups = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
            if db_backups:
                latest_backup = max(db_backups, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
                backup_time = os.path.getctime(os.path.join(backup_dir, latest_backup))
                backup_age = (time.time() - backup_time) / 3600  # Saat cinsinden
                
                backup_status["database"] = {
                    "latest": latest_backup,
                    "age_hours": backup_age,
                    "size_mb": os.path.getsize(os.path.join(backup_dir, latest_backup)) / (1024 * 1024)
                }
                
                if backup_age > 24:
                    logger.warning(f"⚠️ Son veritabanı yedeği {backup_age:.1f} saat önce alınmış")
            else:
                logger.error("❌ Veritabanı yedeği bulunamadı")
        
        # Dosya yedekleri
        file_backup_dir = "/backups/files"
        if os.path.exists(file_backup_dir):
            file_backups = [f for f in os.listdir(file_backup_dir) if f.endswith('.tar.gz')]
            if file_backups:
                latest_backup = max(file_backups, key=lambda x: os.path.getctime(os.path.join(file_backup_dir, x)))
                backup_time = os.path.getctime(os.path.join(file_backup_dir, latest_backup))
                backup_age = (time.time() - backup_time) / 3600
                
                backup_status["files"] = {
                    "latest": latest_backup,
                    "age_hours": backup_age,
                    "size_mb": os.path.getsize(os.path.join(file_backup_dir, latest_backup)) / (1024 * 1024)
                }
                
                if backup_age > 24:
                    logger.warning(f"⚠️ Son dosya yedeği {backup_age:.1f} saat önce alınmış")
            else:
                logger.error("❌ Dosya yedeği bulunamadı")
        
        # Yapılandırma yedekleri
        config_backup_dir = "/backups/config"
        if os.path.exists(config_backup_dir):
            config_backups = [f for f in os.listdir(config_backup_dir) if f.endswith('.json')]
            if config_backups:
                latest_backup = max(config_backups, key=lambda x: os.path.getctime(os.path.join(config_backup_dir, x)))
                backup_time = os.path.getctime(os.path.join(config_backup_dir, latest_backup))
                backup_age = (time.time() - backup_time) / 3600
                
                backup_status["config"] = {
                    "latest": latest_backup,
                    "age_hours": backup_age,
                    "size_mb": os.path.getsize(os.path.join(config_backup_dir, latest_backup)) / (1024 * 1024)
                }
                
                if backup_age > 24:
                    logger.warning(f"⚠️ Son yapılandırma yedeği {backup_age:.1f} saat önce alınmış")
            else:
                logger.error("❌ Yapılandırma yedeği bulunamadı")
        
        # Yedekleme durumunu kaydet
        with open("backup_status.json", "w") as f:
            json.dump(backup_status, f, indent=2)
        
        logger.info("✅ Yedekleme durumu kontrol edildi.")
        
    except Exception as e:
        logger.error(f"❌ Yedekleme kontrolü sırasında hata: {e}")
        return False
    
    return True

def suggest_fixes() -> Dict[str, List[str]]:
    """
    Otomatik düzeltme önerileri oluşturur
    
    Returns:
        Dict[str, List[str]]: Kategoriye göre düzeltme önerileri
    """
    suggestions = {
        "güvenlik": [],
        "performans": [],
        "docker": [],
        "ssl": [],
        "veritabanı": [],
        "loglama": []
    }
    
    try:
        # Güvenlik önerileri
        if not os.path.exists(".env"):
            suggestions["güvenlik"].append("Ortam değişkenleri dosyası (.env) oluşturulmalı")
        
        # Performans önerileri
        if not os.path.exists("staticfiles"):
            suggestions["performans"].append("Statik dosyalar toplanmalı: python manage.py collectstatic")
        
        # Docker önerileri
        returncode, stdout, stderr = run_command("docker-compose ps")
        if returncode != 0:
            suggestions["docker"].append("Docker servisleri başlatılmalı: docker-compose up -d")
        
        # SSL önerileri
        cert_dir = "/etc/letsencrypt/live"
        if not os.path.exists(cert_dir):
            suggestions["ssl"].append("SSL sertifikaları oluşturulmalı: certbot --nginx")
        
        # Veritabanı önerileri
        returncode, stdout, stderr = run_command("python manage.py showmigrations --list")
        if returncode == 0 and " [ ] " in stdout:
            suggestions["veritabanı"].append("Bekleyen migrasyonlar uygulanmalı: python manage.py migrate")
        
        # Loglama önerileri
        if not os.path.exists("logs"):
            suggestions["loglama"].append("Log dizini oluşturulmalı: mkdir logs")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"❌ Düzeltme önerileri oluşturulurken hata: {e}")
        return suggestions

def create_deployment_report() -> None:
    """
    Canlıya alma kontrollerini çalıştırır ve bir rapor oluşturur
    """
    success = True
    
    logger.info("🔍 CANLI ORTAM HAZIRLIK KONTROLÜ")
    logger.info("===============================")
    logger.info(f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    logger.info(f"Proje Dizini: {BASE_DIR}")
    
    # Kontrolleri çalıştır
    checks = [
        (check_settings_security, "Güvenlik Ayarları"),
        (check_database_settings, "Veritabanı Ayarları"),
        (check_static_files, "Statik Dosya Ayarları"),
        (check_installed_apps, "Yüklü Uygulamalar"),
        (check_migrations, "Veritabanı Migrasyonları"),
        (check_url_patterns, "URL Yapılandırması"),
        (check_debug_settings, "Debug Ayarları"),
        (check_media_files, "Media Dosya Ayarları"),
        (check_api_endpoints, "API Endpoint'leri"),
        (check_template_settings, "Template Ayarları"),
        (check_requirements, "Gerekli Paketler"),
        (check_logging_settings, "Loglama Ayarları"),
        (check_docker_containers, "Docker Konteynerleri"),
        (check_ssl_certificates, "SSL Sertifikaları"),
        (collect_performance_metrics, "Performans Metrikleri"),
        (collect_extended_metrics, "Genişletilmiş Performans Metrikleri"),
        (run_security_scan, "Güvenlik Taraması"),
        (check_backups, "Yedekleme Durumu"),
    ]
    
    for check_func, check_name in checks:
        logger.info(f"\n🔍 {check_name} Kontrol Ediliyor...")
        if not check_func():
            success = False
    
    # Düzeltme önerilerini al
    suggestions = suggest_fixes()
    
    # Otomatik düzeltmeleri uygula
    if suggestions:
        if not apply_fixes(suggestions):
            success = False
    
    # Sonuç
    if success:
        logger.info("\n✅ HAZIRIZ! Tüm kontroller başarıyla tamamlandı.")
        logger.info("Projenizi canlı ortama alabilirsiniz.")
    else:
        logger.warning("\n⚠️ DİKKAT! Bazı kontroller başarısız oldu.")
        logger.warning("Yukarıdaki uyarıları dikkate alarak gerekli düzeltmeleri yapın ve testi tekrarlayın.")
    
    # Düzeltme önerilerini göster
    logger.info("\n💡 DÜZELTME ÖNERİLERİ:")
    for category, items in suggestions.items():
        if items:
            logger.info(f"\n{category.upper()}:")
            for item in items:
                logger.info(f"  - {item}")
    
    # HTML rapor oluştur
    html_report = generate_html_report(suggestions)
    with open("deployment_report.html", "w") as f:
        f.write(html_report)
    
    logger.info(f"\nDetaylı rapor 'deployment_report.html' dosyasına kaydedildi.")
    logger.info(f"Log dosyası 'deployment_check.log' içinde bulunabilir.")
    logger.info(f"Performans metrikleri 'performance_metrics.json' ve 'extended_metrics.json' dosyalarında bulunabilir.")
    logger.info(f"Güvenlik taraması sonuçları 'security_scan.json' dosyasında bulunabilir.")
    logger.info(f"Yedekleme durumu 'backup_status.json' dosyasında bulunabilir.\n")

def generate_html_report(suggestions: Dict[str, List[str]]) -> str:
    """
    HTML formatında rapor oluşturur
    
    Args:
        suggestions: Düzeltme önerileri
        
    Returns:
        str: HTML raporu
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
        
        <h2>Düzeltme Önerileri</h2>
        <div class="suggestions">
    """
    
    for category, items in suggestions.items():
        if items:
            html += f"""
            <h3>{category.title()}</h3>
            <ul>
            """
            for item in items:
                html += f"<li>{item}</li>"
            html += "</ul>"
    
    html += """
        </div>
        <style>
            .suggestions {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .suggestions h3 {
                color: #2c3e50;
                margin-top: 15px;
            }
            .suggestions ul {
                margin-left: 20px;
            }
            .suggestions li {
                margin: 5px 0;
            }
        </style>
    """
    
    html += """
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