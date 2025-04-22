"""
Sağlık kontrolü için görünümler (health checks)
"""

from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from django.core.cache import cache
import redis
import json
import os
import psutil
import time
import platform
from django.views.decorators.cache import never_cache

@never_cache
def health_check(request):
    """
    Sistemin durumunu kontrol eden endpoint.
    Veritabanı, Redis ve sistem durumunu kontrol eder.
    """
    start_time = time.time()
    
    # Temel sağlık bilgileri
    health_data = {
        'status': 'ok',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Veritabanı bağlantısını kontrol et
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_result = cursor.fetchone()[0]
            health_data['checks']['database'] = {
                'status': 'ok' if db_result == 1 else 'error',
                'details': 'PostgreSQL connection successful'
            }
    except Exception as e:
        health_data['checks']['database'] = {
            'status': 'error',
            'details': str(e)
        }
        health_data['status'] = 'error'
    
    # Redis bağlantısını kontrol et
    try:
        redis_client = redis.from_url(settings.CACHES['default']['LOCATION'])
        redis_result = redis_client.ping()
        health_data['checks']['redis'] = {
            'status': 'ok' if redis_result else 'error',
            'details': 'Redis connection successful'
        }
    except Exception as e:
        health_data['checks']['redis'] = {
            'status': 'error',
            'details': str(e)
        }
        health_data['status'] = 'error'
    
    # Cache'i kontrol et
    try:
        cache_key = 'health_check_test'
        cache_value = 'test_value'
        cache.set(cache_key, cache_value, 10)
        cache_result = cache.get(cache_key) == cache_value
        health_data['checks']['cache'] = {
            'status': 'ok' if cache_result else 'error',
            'details': 'Cache working properly'
        }
    except Exception as e:
        health_data['checks']['cache'] = {
            'status': 'error',
            'details': str(e)
        }
        health_data['status'] = 'error'
    
    # Statik dosyalar dizinini kontrol et
    static_dir = settings.STATIC_ROOT
    try:
        if os.path.exists(static_dir) and os.path.isdir(static_dir):
            health_data['checks']['static_files'] = {
                'status': 'ok',
                'details': f'Static files directory exists: {static_dir}'
            }
        else:
            health_data['checks']['static_files'] = {
                'status': 'warning',
                'details': f'Static files directory not found: {static_dir}'
            }
    except Exception as e:
        health_data['checks']['static_files'] = {
            'status': 'error',
            'details': str(e)
        }
    
    # Media dosyaları dizinini kontrol et
    media_dir = settings.MEDIA_ROOT
    try:
        if os.path.exists(media_dir) and os.path.isdir(media_dir):
            health_data['checks']['media_files'] = {
                'status': 'ok',
                'details': f'Media files directory exists: {media_dir}'
            }
        else:
            health_data['checks']['media_files'] = {
                'status': 'warning',
                'details': f'Media files directory not found: {media_dir}'
            }
    except Exception as e:
        health_data['checks']['media_files'] = {
            'status': 'error',
            'details': str(e)
        }
    
    # Sistem kaynaklarını kontrol et
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data['checks']['system'] = {
            'status': 'ok',
            'details': {
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'cpu': {
                    'percent': psutil.cpu_percent(interval=0.1)
                }
            }
        }
        
        # Eğer memory veya disk kullanımı %90'ın üzerindeyse uyarı ver
        if memory.percent > 90 or disk.percent > 90:
            health_data['checks']['system']['status'] = 'warning'
    except Exception as e:
        health_data['checks']['system'] = {
            'status': 'error',
            'details': str(e)
        }
    
    # Uygulama versiyonu ve sistem bilgilerini ekle
    health_data['application'] = {
        'version': os.environ.get('APP_VERSION', '1.0.0'),
        'environment': os.environ.get('DJANGO_SETTINGS_MODULE', '').split('.')[-1],
        'debug': settings.DEBUG,
        'system': {
            'platform': platform.system(),
            'release': platform.release(),
            'python': platform.python_version()
        }
    }
    
    # Yanıt süresini ölç
    health_data['response_time'] = time.time() - start_time
    
    # Detaylı mod
    verbose = request.GET.get('verbose', 'false').lower() == 'true'
    if not verbose:
        # Detaylı mod kapalıysa sadece durum bilgisini döndür
        return JsonResponse({
            'status': health_data['status'],
            'response_time': health_data['response_time']
        })
    
    return JsonResponse(health_data) 