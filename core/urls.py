from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

# Dil desteği için
from django.conf.urls.i18n import i18n_patterns

# API Dokümantasyonu için
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Dokümantasyonu
schema_view = get_schema_view(
   openapi.Info(
      title="FinAsis API",
      default_version='v1',
      description="FinAsis finansal yönetim API'si",
      terms_of_service="https://finasis.com.tr/terms/",
      contact=openapi.Contact(email="contact@finasis.com.tr"),
      license=openapi.License(name="Tescilli"),
   ),
   public=True,
   permission_classes=(permissions.IsAuthenticated,),
)

# Uygulama URL'leri
urlpatterns = [
    # Sağlık kontrolü ve API dokümantasyonu gibi çevirilmeyen URL'ler
    path('health/', views.health_check, name='health_check'),
    path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # PWA ve Service Worker
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('offline-test/', TemplateView.as_view(template_name='offline_test.html'), name='offline_test'),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript'), name='service-worker.js'),
    
    # Dil değiştirme URL'i
    path('i18n/', include('django.conf.urls.i18n')),
]

# Çoklu dil destekli URL'ler
urlpatterns += i18n_patterns(
    # Ana sayfalar
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    
    # Uygulama URL'leri
    path('users/', include(('apps.hr_management.urls', 'apps.hr_management'), namespace='hr_management')),
    path('customer-management/', include('customer_management.urls')),
    path('company-management/', include('company_management.urls')),
    path('ext-services/', include('apps.integrations.services.urls')),
    path('seo-management/', include('seo_management.urls')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('ai-assistant/', include(('ai_assistant.urls', 'ai_assistant'), namespace='ai_assistant')),
    path('blockchain/', include(('blockchain.urls', 'blockchain'), namespace='blockchain')),
    path('virtual-company/', include(('virtual_company.urls', 'virtual_company'), namespace='virtual_company')),
    path('games/', include(('apps.games.urls', 'games'), namespace='games')),
    path('social/', include('social_django.urls', namespace='social')),
    path('analytics/', include(('analytics.urls', 'analytics'), namespace='analytics')),
    path('accounting/', include(('accounting.urls', 'accounting'), namespace='accounting')),
    path('crm/', include('crm.urls')),
    path('api/', include('apps.social.urls')),  # Sosyal medya API URL'leri
    
    # API ve Auth URL'leri
    path('api-auth/', include('rest_framework.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # URL'lerin sonuna dil öneki eklemek için (örn. /tr/)
    prefix_default_language=True
)

# Hata sayfaları
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'
handler400 = 'core.views.handler400'

# Geliştirme ortamında static ve media dosyalarının sunulması
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 