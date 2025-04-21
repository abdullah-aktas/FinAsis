"""
API URLs yapılandırması
"""

from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions

from apps.api.views import (
    health_views,
    bank_views, 
    finance_views,
    user_views,
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
router = routers.DefaultRouter()
router.register(r'users', user_views.UserViewSet)
router.register(r'bank-accounts', bank_views.BankAccountViewSet)
router.register(r'transactions', bank_views.TransactionViewSet)
router.register(r'einvoices', finance_views.EInvoiceViewSet)

# API URL patterns
urlpatterns = [
    # API Dokümentasyonu
    path('docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('docs/', include_docs_urls(title=_('FinAsis API Dokümantasyonu'))),
    
    # API v1
    path('v1/', include(router.urls)),
    path('v1/auth/', include('rest_framework.urls')),
    
    # JWT token
    path('v1/token/', user_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', user_views.TokenRefreshView.as_view(), name='token_refresh'),
    
    # Sağlık kontrolü
    path('health/', health_views.api_health_check, name='api_health_check'),
    
    # Finans işlemleri
    path('v1/finance/bank-summary/', bank_views.bank_summary, name='api_bank_summary'),
    path('v1/finance/einvoice-summary/', finance_views.einvoice_summary, name='api_einvoice_summary'),
    
    # Raporlar
    path('v1/reports/monthly-transactions/', finance_views.monthly_transactions_report, name='api_monthly_transactions'),
    path('v1/reports/financial-summary/', finance_views.financial_summary_report, name='api_financial_summary'),
] 