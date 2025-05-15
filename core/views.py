# -*- coding: utf-8 -*-
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import requests
from datetime import datetime
import json
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils import timezone
import logging
import psutil
import os
from django.utils import translation
from django.http import HttpResponseRedirect
from django.db import connection
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

def get_weather_data(request):
    """Kullanıcının IP adresine göre hava durumu bilgisini döndürür"""
    try:
        # IP adresinden şehir bilgisini al
        ip_response = requests.get('https://ipapi.co/json/')
        city = ip_response.json().get('city', 'Istanbul')
        
        return JsonResponse({
            'city': city,
            'temperature': 20,
            'condition': 'Güneşli'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def get_finance_data(request):
    """Güncel finans bilgilerini döndürür"""
    try:
        return JsonResponse({
            'bist100': 10000.00,
            'usd': 30.50,
            'eur': 33.20,
            'gold': 2000.00,
            'last_updated': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

class HealthCheckViewSet(viewsets.ViewSet):
    """
    Sistem sağlık kontrolü için ViewSet
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def system(self, request):
        """
        Sistem kaynaklarının durumunu kontrol eder
        """
        try:
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Bellek kullanımı
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Veritabanı bağlantısı
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = True
            
            # Redis bağlantısı
            redis_status = False
            try:
                cache.get('health_check')
                redis_status = True
            except:
                pass
            
            # Celery durumu
            celery_status = False
            try:
                from config.celery import app
                celery_status = app.control.inspect().active() is not None
            except:
                pass

            return Response({
                'status': 'healthy',
                'timestamp': timezone.now(),
                'system': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory_percent,
                    'disk_usage': disk_percent,
                },
                'services': {
                    'database': db_status,
                    'redis': redis_status,
                    'celery': celery_status,
                },
                'version': settings.VERSION,
            })
        except Exception as e:
            logger.error(f"Sistem sağlık kontrolü hatası: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        Sistem performans metriklerini döndürür
        """
        try:
            # Veritabanı sorgu sayısı
            query_count = len(connection.queries)
            
            # İşlem süresi
            process = psutil.Process(os.getpid())
            process_time = process.cpu_times()
            
            return Response({
                'database': {
                    'queries': query_count,
                },
                'process': {
                    'user_time': process_time.user,
                    'system_time': process_time.system,
                },
            })
        except Exception as e:
            logger.error(f"Performans metrikleri hatası: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardView(TemplateView):
    """
    Ana dashboard görünümü
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard'
        return context

class ErrorView(TemplateView):
    """
    Hata sayfaları için temel görünüm
    """
    template_name = 'core/error.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Hata'
        return context

def health_check(request):
    """
    Sistem sağlık kontrolü
    """
    # Veritabanı durumu
    db_status = True
    try:
        connection.ensure_connection()
    except Exception:
        db_status = False

    # Cache durumu
    cache_status = True
    try:
        cache.get('health_check')
    except Exception:
        cache_status = False

    # Sistem durumu
    status = {
        'database': db_status,
        'cache': cache_status,
        'status': 'healthy' if all([db_status, cache_status]) else 'unhealthy'
    }

    return JsonResponse(status)

def home(request):
    """
    Ana sayfa görünümü.
    """
    return render(request, 'core/home.html')

def pricing(request):
    """
    Fiyatlandırma sayfası görünümü.
    """
    return render(request, 'core/pricing.html')

def set_language(request):
    """
    Kullanıcıdan gelen dil seçimini session ve cookie'ye kaydeder.
    """
    next_url = request.POST.get('next', request.GET.get('next', '/'))
    lang_code = request.POST.get('language', request.GET.get('language'))
    if lang_code and lang_code in dict(settings.LANGUAGES):
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        translation.activate(lang_code)
        return response
    return HttpResponseRedirect(next_url)

def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST) 