# -*- coding: utf-8 -*-
"""
API URLs yapılandırması
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions

from api.views import (
    health_views,
    bank_views, 
    finance_views,
    user_views,
    FinanceViewSet,
    CRMViewSet,
    AccountingViewSet,
    AnalyticsViewSet,
    ScanView
)

# API Schema için
schema_view = get_schema_view(
    openapi.Info(
        title=_("FinAsis API"),
        default_version='v1',
        description=_("FinAsis REST API dokümantasyonu"),
        terms_of_service="https://finasis.com.tr/terms/",
        contact=openapi.Contact(email="contact@finasis.com.tr"),
        license=openapi.License(name="Ticari Lisans"),
    ),
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
)

# DRF Router
router = DefaultRouter()
router.register(r'finance', FinanceViewSet, basename='finance')
router.register(r'crm', CRMViewSet, basename='crm')
router.register(r'accounting', AccountingViewSet, basename='accounting')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

# API URL patterns
urlpatterns = [
    # API Dokümentasyonu
    path('docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('docs/', include_docs_urls(title=_('FinAsis API Dokümantasyonu'))),
    
    # API v1
    path('v1/', include([
        # Ana API Endpoint'leri
        path('', include(router.urls)),
        
        # Dokümantasyon
        path('schema/', get_schema_view(
            title='FinAsis API',
            description='FinAsis Finansal Yönetim Sistemi API Dokümantasyonu',
            version='1.0.0',
            public=True,
        )),
        
        # Kimlik Doğrulama
        path('auth/', include('rest_framework.urls')),
        path('token/', include('rest_framework_social_oauth2.urls')),
        
        # Modül Bazlı API'ler
        path('finance/', include('api.finance.urls')),
        path('crm/', include('api.crm.urls')),
        path('accounting/', include('api.accounting.urls')),
        path('analytics/', include('api.analytics.urls')),
    ])),
    
    # Sağlık kontrolü
    path('health/', health_views.api_health_check, name='api_health_check'),
    
    # Finans işlemleri
    path('v1/finance/bank-summary/', bank_views.bank_summary, name='api_bank_summary'),
    path('v1/finance/einvoice-summary/', finance_views.einvoice_summary, name='api_einvoice_summary'),
    
    # Raporlar
    path('v1/reports/monthly-transactions/', finance_views.monthly_transactions_report, name='api_monthly_transactions'),
    path('v1/reports/financial-summary/', finance_views.financial_summary_report, name='api_financial_summary'),
    
    # Scan işlemi
    path('scan/', ScanView.as_view(), name='scan'),
] 