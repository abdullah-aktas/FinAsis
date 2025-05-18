# -*- coding: utf-8 -*-
"""
Core Modülü - URL Yapılandırması
--------------------------------
Bu dosya, FinAsis uygulamasının temel URL yapılandırmasını içerir.

URL Yapısı:
- / - Ana sayfa
- /dashboard/ - Ana kontrol paneli
- /api/v1/core/ - Ana core API endpoint'i
- /api/v1/core/health/ - Sistem sağlık kontrolü
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HealthCheckViewSet, 
    DashboardView, 
    ErrorView,
    home,
    pricing,
    get_weather_data,
    get_finance_data,
    set_language,
)

app_name = 'core'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'health', HealthCheckViewSet, basename='health')

urlpatterns = [
    # Ana Sayfalar
    path('', home, name='home'),
    path('pricing/', pricing, name='pricing'),
    
    # Dashboard ve Kontrol Paneli
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/<str:section>/', DashboardView.as_view(), name='dashboard-section'),
    
    # API Endpoint'leri
    path('api/', include(router.urls)),
    path('api/weather/', get_weather_data, name='weather-data'),
    path('api/finance/', get_finance_data, name='finance-data'),
    
    # Hata Sayfaları
    path('error/<int:code>/', ErrorView.as_view(), name='error'),
    path('error/<int:code>/<str:message>/', ErrorView.as_view(), name='error-with-message'),
    
    # Sistem Durumu
    path('status/', HealthCheckViewSet.as_view({'get': 'list'}), name='system-status'),
    path('status/<str:component>/', HealthCheckViewSet.as_view({'get': 'retrieve'}), name='component-status'),
    
    # Dil seçici
    path('set-language/', set_language, name='set_language'),
] 