from django.shortcuts import render
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
from django.core.cache import cache
from redis.exceptions import RedisError
import redis
import time
import os
import psutil
import socket
import json

def home(request):
    return render(request, 'home.html')

def pricing(request):
    return render(request, 'pricing.html')

def health_check(request):
    """
    Sistem sağlık kontrolü - Docker ve Kubernetes için kullanılır
    """
    # Veritabanı kontrolü
    db_conn_alive = True
    try:
        connections['default'].cursor()
    except OperationalError:
        db_conn_alive = False
    
    # Redis kontrolü
    redis_alive = True
    try:
        cache.get('health_check_key')
    except RedisError:
        redis_alive = False
    
    # Disk kullanım kontrolü
    disk_usage = psutil.disk_usage('/app')
    disk_percent = disk_usage.percent
    disk_warning = disk_percent > 80
    
    # RAM kullanım kontrolü
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_warning = ram_percent > 80
    
    # CPU kullanım kontrolü
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_warning = cpu_percent > 80
    
    # Ortam bilgileri
    env_info = {
        'hostname': socket.gethostname(),
        'django_settings': os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown'),
        'debug_mode': os.environ.get('DJANGO_DEBUG', 'False'),
    }
    
    # Genel sistem durumu
    status = all([db_conn_alive, redis_alive, not disk_warning, not ram_warning, not cpu_warning])
    
    response_data = {
        'status': 'healthy' if status else 'unhealthy',
        'database': 'connected' if db_conn_alive else 'disconnected',
        'redis': 'connected' if redis_alive else 'disconnected',
        'disk': {
            'total': f"{disk_usage.total / (1024**3):.2f}GB",
            'used': f"{disk_usage.used / (1024**3):.2f}GB",
            'free': f"{disk_usage.free / (1024**3):.2f}GB",
            'percent': f"{disk_percent}%",
            'warning': disk_warning
        },
        'ram': {
            'total': f"{ram.total / (1024**3):.2f}GB",
            'used': f"{ram.used / (1024**3):.2f}GB",
            'free': f"{ram.available / (1024**3):.2f}GB",
            'percent': f"{ram_percent}%",
            'warning': ram_warning
        },
        'cpu': {
            'percent': f"{cpu_percent}%",
            'warning': cpu_warning
        },
        'environment': env_info,
        'timestamp': psutil.time.time()
    }
    
    status_code = 200 if status else 503
    return JsonResponse(response_data, status=status_code) 