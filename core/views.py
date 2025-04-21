from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.db import connections, connection
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
import psutil
import datetime
import redis
import json
import os

def home(request):
    """Ana sayfa görünümü"""
    return render(request, 'home.html')

@require_GET
@never_cache
def health_check(request):
    """
    Sistem sağlık kontrolü görünümü
    Bu görünüm, sistemin bileşenlerinin durumunu kontrol eder ve sonuçları JSON olarak döndürür.
    
    Parametreler:
    - verbose: True ise, detaylı sonuçlar döndürülür (varsayılan: False)
    """
    verbose = request.GET.get('verbose', 'false').lower() == 'true'
    
    health_data = {
        'status': 'pass',
        'datetime': timezone.now().isoformat(),
        'version': getattr(settings, 'VERSION', 'unknown'),
        'checks': {}
    }
    
    # Veritabanı kontrolü
    db_status = check_database()
    health_data['checks']['database'] = db_status
    if db_status['status'] == 'fail':
        health_data['status'] = 'fail'
    
    # Redis kontrolü
    redis_status = check_redis()
    health_data['checks']['redis'] = redis_status
    if redis_status['status'] == 'fail':
        health_data['status'] = 'fail'
    
    # Önbellek kontrolü
    cache_status = check_cache()
    health_data['checks']['cache'] = cache_status
    if cache_status['status'] == 'fail':
        health_data['status'] = 'fail'
    
    # Sistemin disk ve CPU durumu
    if verbose:
        system_status = check_system_resources()
        health_data['checks']['system'] = system_status
        if system_status['status'] == 'fail':
            health_data['status'] = 'fail'
        
        # Statik dosyalar kontrolü
        static_status = check_static_files()
        health_data['checks']['static_files'] = static_status
        if static_status['status'] == 'fail':
            health_data['status'] = 'warn'
        
        # Media dosyaları kontrolü
        media_status = check_media_files()
        health_data['checks']['media_files'] = media_status
        if media_status['status'] == 'fail':
            health_data['status'] = 'warn'
    
    # HTTP durum kodunu belirle (fail: 503, warn: 200, pass: 200)
    status_code = 503 if health_data['status'] == 'fail' else 200
    
    # Sonuçları JSON formatında döndür
    response = JsonResponse(health_data)
    response.status_code = status_code
    return response

def check_database():
    """Veritabanı bağlantısını kontrol eder"""
    try:
        # Veritabanı bağlantısını test et
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # Bağlantının gecikme süresini ölç
        start_time = datetime.datetime.now()
        cursor.execute("SELECT 1")
        latency = (datetime.datetime.now() - start_time).total_seconds()
        
        # Veritabanı versiyonunu al
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        return {
            'status': 'pass',
            'latency': latency,
            'version': version,
            'message': 'Database is healthy'
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': f'Database connection failed: {str(e)}'
        }

def check_redis():
    """Redis bağlantısını kontrol eder"""
    try:
        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.from_url(redis_url)
        
        # Redis bağlantısını test et
        start_time = datetime.datetime.now()
        redis_client.ping()
        latency = (datetime.datetime.now() - start_time).total_seconds()
        
        # Redis versiyonunu al
        info = redis_client.info()
        
        return {
            'status': 'pass',
            'latency': latency,
            'version': info.get('redis_version', 'unknown'),
            'message': 'Redis is healthy'
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': f'Redis connection failed: {str(e)}'
        }

def check_cache():
    """Django önbelleğini kontrol eder"""
    try:
        # Önbelleği test et
        key = 'health_check_test_key'
        value = 'health_check_test_value'
        
        start_time = datetime.datetime.now()
        cache.set(key, value, 10)
        cached_value = cache.get(key)
        latency = (datetime.datetime.now() - start_time).total_seconds()
        
        if cached_value != value:
            return {
                'status': 'fail',
                'message': 'Cache set/get failed'
            }
        
        return {
            'status': 'pass',
            'latency': latency,
            'message': 'Cache is healthy'
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': f'Cache check failed: {str(e)}'
        }

def check_system_resources():
    """Sistem kaynaklarını kontrol eder"""
    try:
        # Disk kullanımını kontrol et
        disk_usage = psutil.disk_usage('/')
        disk_percent = disk_usage.percent
        disk_free_gb = disk_usage.free / (1024 * 1024 * 1024)
        
        # CPU kullanımını kontrol et
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Bellek kullanımını kontrol et
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_free_gb = memory.available / (1024 * 1024 * 1024)
        
        # Systemİn durumunu belirle
        status = 'pass'
        messages = []
        
        # Disk alanı kritik mi?
        if disk_percent > 90:
            status = 'fail'
            messages.append(f'Critical disk usage: {disk_percent}%')
        elif disk_percent > 80:
            status = 'warn'
            messages.append(f'High disk usage: {disk_percent}%')
        
        # CPU yükü kritik mi?
        if cpu_percent > 90:
            status = 'fail'
            messages.append(f'Critical CPU usage: {cpu_percent}%')
        elif cpu_percent > 80:
            status = 'warn'
            messages.append(f'High CPU usage: {cpu_percent}%')
        
        # Bellek kullanımı kritik mi?
        if memory_percent > 90:
            status = 'fail'
            messages.append(f'Critical memory usage: {memory_percent}%')
        elif memory_percent > 80:
            status = 'warn'
            messages.append(f'High memory usage: {memory_percent}%')
        
        return {
            'status': status,
            'disk': {
                'total_gb': disk_usage.total / (1024 * 1024 * 1024),
                'used_gb': disk_usage.used / (1024 * 1024 * 1024),
                'free_gb': disk_free_gb,
                'percent': disk_percent
            },
            'cpu': {
                'percent': cpu_percent,
                'cores': psutil.cpu_count()
            },
            'memory': {
                'total_gb': memory.total / (1024 * 1024 * 1024),
                'used_gb': memory.used / (1024 * 1024 * 1024),
                'free_gb': memory_free_gb,
                'percent': memory_percent
            },
            'message': ', '.join(messages) if messages else 'System resources are healthy'
        }
    except Exception as e:
        return {
            'status': 'warn',
            'message': f'System resources check failed: {str(e)}'
        }

def check_static_files():
    """Statik dosyaları kontrol eder"""
    try:
        # Statik dosya dizini mevcut mu?
        static_root = getattr(settings, 'STATIC_ROOT', None)
        static_exists = static_root and os.path.exists(static_root)
        
        # Temel CSS ve JS dosyaları mevcut mu?
        css_exists = False
        js_exists = False
        
        if static_exists:
            css_path = os.path.join(static_root, 'css', 'styles.css')
            js_path = os.path.join(static_root, 'js', 'app.js')
            
            css_exists = os.path.exists(css_path)
            js_exists = os.path.exists(js_path)
        
        if not static_exists:
            return {
                'status': 'fail',
                'message': 'Static root directory does not exist'
            }
        
        if not css_exists or not js_exists:
            return {
                'status': 'warn',
                'message': 'Some core static files are missing'
            }
        
        return {
            'status': 'pass',
            'static_root': static_root,
            'message': 'Static files are available'
        }
    except Exception as e:
        return {
            'status': 'warn',
            'message': f'Static files check failed: {str(e)}'
        }

def check_media_files():
    """Media dosyaları dizinini kontrol eder"""
    try:
        # Media dizini mevcut mu?
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        media_exists = media_root and os.path.exists(media_root)
        
        if not media_exists:
            return {
                'status': 'warn',
                'message': 'Media root directory does not exist'
            }
        
        # Yazılabilir mi?
        is_writable = os.access(media_root, os.W_OK)
        
        if not is_writable:
            return {
                'status': 'fail',
                'message': 'Media directory is not writable'
            }
        
        return {
            'status': 'pass',
            'media_root': media_root,
            'message': 'Media directory is available and writable'
        }
    except Exception as e:
        return {
            'status': 'warn',
            'message': f'Media files check failed: {str(e)}'
        }

def handler404(request, exception):
    """
    404 Hata Sayfası (Sayfa Bulunamadı)
    """
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    """
    500 Hata Sayfası (Sunucu Hatası)
    """
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    """
    403 Hata Sayfası (Erişim Reddedildi)
    """
    return render(request, 'errors/403.html', status=403)

def handler400(request, exception):
    """
    400 Hata Sayfası (Geçersiz İstek)
    """
    return render(request, 'errors/400.html', status=400) 