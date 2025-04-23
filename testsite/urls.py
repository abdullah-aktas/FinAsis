from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include('api.urls')),
    path('api/schema/', get_schema_view(
        title='FinAsis API',
        description='Finansal Yönetim Sistemi API',
        version='1.0.0'
    ), name='api-schema'),
    path('api/docs/', include_docs_urls(title='FinAsis API Documentation')),
    
    # Uygulama URL'leri
    path('', include('core.urls')),
    path('finance/', include('finance.urls')),
    path('stock/', include('stock_management.urls')),
    path('social/', include('social.urls')),
    path('ai/', include('ai_assistant.urls')),
    
    # Kimlik Doğrulama
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('users.urls')),
    
    # Hata Sayfaları
    path('400/', TemplateView.as_view(template_name='errors/400.html'), name='400'),
    path('403/', TemplateView.as_view(template_name='errors/403.html'), name='403'),
    path('404/', TemplateView.as_view(template_name='errors/404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='errors/500.html'), name='500'),
]

# Debug modunda statik ve medya dosyaları
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] 