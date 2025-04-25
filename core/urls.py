"""
Core Modülü - URL Yapılandırması
--------------------------------
Bu dosya, FinAsis uygulamasının temel URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/core/ - Ana core API endpoint'i
- /api/v1/core/health/ - Sistem sağlık kontrolü
- /api/v1/core/dashboard/ - Ana kontrol paneli
- /api/v1/core/error/ - Hata sayfaları
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthCheckViewSet, DashboardView, ErrorView

app_name = 'core'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'health', HealthCheckViewSet, basename='health')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Dashboard ve Kontrol Paneli
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/<str:section>/', DashboardView.as_view(), name='dashboard-section'),
    
    # Hata Sayfaları
    path('error/<int:code>/', ErrorView.as_view(), name='error'),
    path('error/<int:code>/<str:message>/', ErrorView.as_view(), name='error-with-message'),
    
    # Sistem Durumu
    path('status/', HealthCheckViewSet.as_view({'get': 'list'}), name='system-status'),
    path('status/<str:component>/', HealthCheckViewSet.as_view({'get': 'retrieve'}), name='component-status'),
] 