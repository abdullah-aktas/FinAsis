from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core import views
from django.conf.urls.i18n import i18n_patterns
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Language-independent URLs
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Dil değiştirme için
    path('health/', views.health_check, name='health_check'),  # Sağlık kontrolü endpoint
    path('api/', include('api.urls')),  # API endpoints
]

# Language-dependent URLs
urlpatterns += i18n_patterns(
    # Ana sayfalar
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('pricing/', views.pricing, name='pricing'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript'), name='service-worker.js'),
    
    # Kullanıcı ve kimlik doğrulama
    path('users/', include('users.urls')),
    path('accounts/', include('accounts.urls')),
    path('permissions/', include('permissions.urls')),
    
    # Finans modülleri
    path('finance/', include('finance.urls')),
    path('accounting/', include('accounting.urls')),
    path('checks/', include('checks.urls')),
    
    # İş yönetimi
    path('crm/', include('crm.urls')),
    path('virtual-company/', include('virtual_company.urls')),
    path('hr/', include('hr_management.urls')),
    path('assets/', include('assets.urls')),
    path('stock/', include('stock_management.urls')),
    
    # Belgeler ve entegrasyonlar
    path('edocument/', include('edocument.urls')),
    path('integrations/', include('integrations.urls')),
    path('blockchain/', include('blockchain.urls')),
    
    # Analizler ve raporlama
    path('analytics/', include('analytics.urls')),
    
    # Yardımcı sistemler
    path('assistant/', include('assistant.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),
    
    # Pazarlama ve sosyal medya
    path('seo/', include('seo.urls')),
    path('social/', include('social.urls')),
    
    # Oyunlar ve eğitimler
    path('games/', include('games.urls')),
    
    prefix_default_language=True  # Varsayılan dil için de prefix ekle
)

# Debug araçları
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version='v1',
        description="FinAsis Kontrol ve Analiz Sistemi API Dokümantasyonu",
        terms_of_service="https://www.finasis.com/terms/",
        contact=openapi.Contact(email="info@finasis.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    # API Dokümantasyonu
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 