from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path
from django.conf.urls import handler400, handler403, handler404, handler500

# API Dokümantasyonu
schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version='v1',
        description="FinAsis Finansal Yönetim Sistemi API Dokümantasyonu",
        terms_of_service="https://www.finasis.com/terms/",
        contact=openapi.Contact(email="api@finasis.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    # Admin paneli
    path('admin/', admin.site.urls),
    
    # API Dokümantasyonu
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Sağlık kontrolü
    path('health/', include('health_check.urls')),
    
    # Uygulama URL'leri
    path('api/finance/', include('finance.urls')),
    path('api/crm/', include('crm.urls')),
    path('api/edocument/', include('edocument.urls')),
    path('api/accounting/', include('accounting.urls')),
    path('api/banking/', include('banking.urls')),
    path('api/checks/', include('checks.urls')),
    path('api/virtual-company/', include('virtual_company.urls')),
    
    # Ana sayfa
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    path('', include('apps.home.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounting/', include('apps.accounting.urls')),
    path('stock/', include('apps.stock_management.urls')),
    path('banking/', include('apps.banking.urls')),
    path('reports/', include('apps.reports.urls')),
]

# Hata sayfaları
handler400 = 'FinAsis.views.bad_request'
handler403 = 'FinAsis.views.permission_denied'
handler404 = 'FinAsis.views.page_not_found'
handler500 = 'FinAsis.views.server_error'

# Debug modunda statik ve medya dosyaları
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 