from django.shortcuts import render
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
import redis
import time

def home(request):
    return render(request, 'home.html')

def pricing(request):
    return render(request, 'pricing.html')

def health_check(request):
    """
    Sistem sağlık kontrolü endpoint'i.
    Veritabanı, Redis ve diğer kritik servislerin durumunu kontrol eder.
    """
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': start_time,
        'services': {}
    }

    # Veritabanı kontrolü
    try:
        db_conn = connections['default']
        db_conn.cursor()
        health_status['services']['database'] = {
            'status': 'healthy',
            'response_time': time.time() - start_time
        }
    except OperationalError as e:
        health_status['services']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'

    # Redis kontrolü (eğer kullanılıyorsa)
    if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
        try:
            redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
            redis_client.ping()
            health_status['services']['redis'] = {
                'status': 'healthy',
                'response_time': time.time() - start_time
            }
        except Exception as e:
            health_status['services']['redis'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'

    # Sistem bilgileri
    health_status['system'] = {
        'python_version': settings.PYTHON_VERSION,
        'django_version': settings.DJANGO_VERSION,
        'environment': settings.ENVIRONMENT,
    }

    # Toplam yanıt süresi
    health_status['total_response_time'] = time.time() - start_time

    # HTTP durum kodu
    status_code = 200 if health_status['status'] == 'healthy' else 503

    return JsonResponse(health_status, status=status_code) 