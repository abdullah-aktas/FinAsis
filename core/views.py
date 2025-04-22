from django.http import JsonResponse
from django.conf import settings
import requests
import yfinance as yf
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

logger = logging.getLogger(__name__)

def get_weather_data(request):
    """Kullanıcının IP adresine göre hava durumu bilgisini döndürür"""
    try:
        # IP adresinden şehir bilgisini al
        ip_response = requests.get('https://ipapi.co/json/')
        city = ip_response.json().get('city', 'Istanbul')
        
        # OpenWeatherMap API'den hava durumu bilgisini al
        weather_response = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather',
            params={
                'q': city,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'tr'
            }
        )
        weather_data = weather_response.json()
        
        return JsonResponse({
            'city': city,
            'temperature': round(weather_data['main']['temp']),
            'condition': weather_data['weather'][0]['description'].capitalize()
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def get_finance_data(request):
    """Güncel finans bilgilerini döndürür"""
    try:
        # BIST100 verisi
        bist100 = yf.Ticker("XU100.IS")
        bist100_data = bist100.history(period='1d')
        bist100_value = round(bist100_data['Close'].iloc[-1], 2)
        
        # Döviz kurları
        usd_try = yf.Ticker("USDTRY=X")
        eur_try = yf.Ticker("EURTRY=X")
        
        usd_data = usd_try.history(period='1d')
        eur_data = eur_try.history(period='1d')
        
        usd_value = round(usd_data['Close'].iloc[-1], 2)
        eur_value = round(eur_data['Close'].iloc[-1], 2)
        
        # Altın fiyatı (XAU/TRY)
        gold_try = yf.Ticker("XAUTRY=X")
        gold_data = gold_try.history(period='1d')
        gold_value = round(gold_data['Close'].iloc[-1], 2)
        
        return JsonResponse({
            'bist100': bist100_value,
            'usd': usd_value,
            'eur': eur_value,
            'gold': gold_value,
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
            from django.db import connection
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
            # Cache hit/miss oranı
            cache_stats = cache.client.get_stats()
            
            # Veritabanı sorgu sayısı
            from django.db import connection
            query_count = len(connection.queries)
            
            # İşlem süresi
            process = psutil.Process(os.getpid())
            process_time = process.cpu_times()
            
            return Response({
                'cache': {
                    'hits': cache_stats.get('hits', 0),
                    'misses': cache_stats.get('misses', 0),
                    'ratio': cache_stats.get('hits', 0) / (cache_stats.get('misses', 0) + 1),
                },
                'database': {
                    'queries': query_count,
                },
                'process': {
                    'user_time': process_time.user,
                    'system_time': process_time.system,
                    'children_user_time': process_time.children_user,
                    'children_system_time': process_time.children_system,
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
        
        # Sistem durumu
        try:
            health_viewset = HealthCheckViewSet()
            health_viewset.request = self.request
            system_status = health_viewset.system(self.request).data
            context['system_status'] = system_status
        except:
            context['system_status'] = None
        
        # Performans metrikleri
        try:
            performance_viewset = HealthCheckViewSet()
            performance_viewset.request = self.request
            performance_metrics = performance_viewset.performance(self.request).data
            context['performance_metrics'] = performance_metrics
        except:
            context['performance_metrics'] = None
        
        return context

class ErrorView(TemplateView):
    """
    Hata sayfaları için temel görünüm
    """
    template_name = 'core/error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_code'] = self.kwargs.get('code', 500)
        context['error_message'] = self.kwargs.get('message', 'Bir hata oluştu')
        return context 