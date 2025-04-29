# -*- coding: utf-8 -*-
"""
API sağlık kontrolü görünümleri
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
import redis
import time
import os
import psutil
from django.conf import settings

@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """
    API sağlık durumunu kontrol eder.
    """
    start_time = time.time()
    
    # Temel sağlık bilgileri
    health_data = {
        'status': 'ok',
        'timestamp': time.time(),
        'api_version': 'v1',
        'checks': {}
    }
    
    # Veritabanı bağlantısını kontrol et
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_result = cursor.fetchone()[0]
            health_data['checks']['database'] = {
                'status': 'ok' if db_result == 1 else 'error',
                'details': 'Connected to PostgreSQL'
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
            'details': 'Connected to Redis'
        }
    except Exception as e:
        health_data['checks']['redis'] = {
            'status': 'error',
            'details': str(e)
        }
        health_data['status'] = 'error'
    
    # Cache'i kontrol et
    try:
        cache_key = 'api_health_check_test'
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
    
    # Uygulama bilgilerini ekle
    health_data['application'] = {
        'environment': settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'unknown',
        'debug_mode': settings.DEBUG,
    }
    
    # Detaylı mod
    detailed = request.query_params.get('detailed', 'false').lower() == 'true'
    if detailed:
        # Sistem kaynaklarını ekle
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_data['system'] = {
                'memory': {
                    'percent': memory.percent,
                    'available_mb': memory.available / (1024 * 1024),
                },
                'disk': {
                    'percent': disk.percent,
                    'free_gb': disk.free / (1024 * 1024 * 1024),
                },
                'cpu': {
                    'percent': psutil.cpu_percent(interval=0.1),
                }
            }
        except Exception as e:
            health_data['system'] = {
                'status': 'error',
                'details': str(e)
            }
    
    # Yanıt süresini ölç
    health_data['response_time_ms'] = (time.time() - start_time) * 1000
    
    return Response(health_data)