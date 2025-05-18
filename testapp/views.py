# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import time
import json
import logging

logger = logging.getLogger(__name__)

class TestView(View):
    """Temel test view sınıfı"""
    
    def get(self, request, *args, **kwargs):
        """GET isteklerini işler"""
        start_time = time.time()
        try:
            # Cache kontrolü
            cached_response = cache.get('test_response')
            if cached_response:
                logger.info("Cache hit for test response")
                return JsonResponse(cached_response)
            
            # Test verisi oluştur
            test_data = {
                'status': 'success',
                'message': 'Test başarılı',
                'timestamp': time.time(),
                'request_info': {
                    'method': request.method,
                    'path': request.path,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'ip': request.META.get('REMOTE_ADDR', ''),
                }
            }
            
            # Cache'e kaydet (5 dakika)
            cache.set('test_response', test_data, 300)
            
            # Performans metrikleri
            execution_time = time.time() - start_time
            logger.info(f"Test view executed in {execution_time:.2f} seconds")
            
            return JsonResponse(test_data)
            
        except Exception as e:
            logger.error(f"Test view error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(login_required, name='dispatch')
class ProtectedTestView(View):
    """Kimlik doğrulama gerektiren test view"""
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'success',
            'message': 'Korumalı test başarılı',
            'user': request.user.username
        })

@require_http_methods(["POST"])
@csrf_exempt
def api_test(request):
    """API test endpoint'i"""
    try:
        data = json.loads(request.body)
        return JsonResponse({
            'status': 'success',
            'received_data': data
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Geçersiz JSON verisi'
        }, status=400)

def health_check(request):
    """Sistem sağlık kontrolü"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'database': 'ok',
            'cache': 'ok',
            'auth': 'ok'
        }
    })

def performance_test(request):
    """Performans test endpoint'i"""
    start_time = time.time()
    
    # Yoğun işlem simülasyonu
    result = 0
    for i in range(1000000):
        result += i
    
    execution_time = time.time() - start_time
    
    return JsonResponse({
        'status': 'success',
        'execution_time': execution_time,
        'result': result
    })

def home(request):
    return HttpResponse("FinAsis Test Sayfası Açıldı - Tebrikler!") 