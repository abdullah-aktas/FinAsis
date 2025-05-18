# -*- coding: utf-8 -*-
"""
FinAsis - URL Yapılandırması
----------------------------
Bu dosya, FinAsis uygulamasının ana URL yapılandırmasını içerir.

API Versiyonlama Stratejisi:
- v1: Mevcut stabil API
- v2: Geliştirme aşamasındaki yeni özellikler
- v3: Gelecek planlanan özellikler

URL Yapılandırma Kuralları:
1. Tüm API endpoint'leri /api/v{version}/ altında olmalı
2. Her modül kendi namespace'ine sahip olmalı
3. URL pattern'leri açıklayıcı isimlendirilmeli
4. CRUD işlemleri için standart URL yapısı kullanılmalı
"""

from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore
from django.views.generic import TemplateView # type: ignore
from core import views
from django.conf.urls.i18n import i18n_patterns # type: ignore
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from permissions.views import (
    RoleViewSet,
    ResourceViewSet,
    PermissionViewSet,
    PermissionDelegationViewSet,
    AuditLogViewSet,
    IPWhitelistViewSet,
    TwoFactorSetupView,
    TwoFactorVerifyView,
    TwoFactorDisableView,
    CheckPermissionView,
    UserPermissionsView,
    DelegatePermissionView,
    RevokePermissionView,
)

from core.views import metrics

# API Dokümantasyonu için Swagger yapılandırması
schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version='v1',
        description="FinAsis API Dokümantasyonu",
        terms_of_service="https://www.finasis.com/terms/",
        contact=openapi.Contact(email="api@finasis.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Language-independent URLs
urlpatterns = [
    # API Dokümantasyonu
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),
    
    # Dil ve Sağlık Kontrolü
    path('i18n/', include('django.conf.urls.i18n'), name='language-switch'),
    path('health/', TemplateView.as_view(template_name='health.html'), name='health-check'),
    
    # Ana Sayfalar
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
]

# Admin URLs
urlpatterns += [
    path('admin/', admin.site.urls, name='admin-panel'),
]

# API Versiyon 1 URLs
api_v1_patterns = [
    # Kimlik Doğrulama (JWT)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Kullanıcı Yönetimi
    path('users/', include(('users.urls', 'users'), namespace='users')),

    # Finans Modülleri
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),

    # Diğer API modülleri eklenebilir
    # path('checks/', include(('checks.urls', 'checks'), namespace='checks')),
    # path('assets/', include(('assets.urls', 'assets'), namespace='assets')),
    # path('stock/', include(('stock_management.urls', 'stock_management'), namespace='stock_management')),
]

# API Versiyon 2 URLs (Geliştirme Aşamasında)
api_v2_patterns = [
    # path('ai-assistant/', include('ai_assistant.urls', namespace='ai-assistant')),
    path('blockchain/', include('blockchain.urls', namespace='blockchain')),
]

# API URL'lerini ana URL yapılandırmasına ekle
urlpatterns += [
    path('api/v1/', include(api_v1_patterns)),
    path('api/v2/', include(api_v2_patterns)),
]

# Language-dependent URLs
urlpatterns += i18n_patterns(
    # Ana sayfalar
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript'), name='service-worker'),
    
    # Finans modülleri
    path('finance/', include('finance.urls')),
    path('checks/', include('checks.urls')),
    
    # İş yönetimi
    path('virtual-company/', include('virtual_company.urls')),
    path('assets/', include('assets.urls')),
    path('stock/', include('stock_management.urls')),
    
    # Belgeler ve entegrasyonlar
    # path('edocument/', include('edocument.urls')),  # Geçici olarak devre dışı bırakıldı
    # path('integrations/', include('integrations.urls')),  # Geçici olarak devre dışı bırakıldı
    # path('blockchain/', include('blockchain.urls')),  # Geçici olarak devre dışı bırakıldı
    
    # Analizler ve raporlama
    # path('analytics/', include('analytics.urls')),  # Geçici olarak devre dışı bırakıldı
    
    # Yardımcı sistemler
    # path('assistant/', include('assistant.urls')),  # Geçici olarak devre dışı bırakıldı
    # path('ai-assistant/', include('ai_assistant.urls')),  # Geçici olarak devre dışı bırakıldı
    
    # Pazarlama ve sosyal medya
    # path('seo/', include('seo.urls')),  # Geçici olarak devre dışı bırakıldı
    # path('social/', include('social.urls')),  # Geçici olarak devre dışı bırakıldı
    
    # Oyunlar ve eğitimler
    # path('games/', include('games.urls')),  # Geçici olarak devre dışı bırakıldı
    
    prefix_default_language=True
)

# Debug modunda statik ve medya dosyaları
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Remove old URLs
# path('accounts/', include('accounts.urls')),
# path('permissions/', include('permissions.urls')),

# API Router
router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'permission-delegations', PermissionDelegationViewSet, basename='permission-delegation')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'ip-whitelist', IPWhitelistViewSet, basename='ip-whitelist')

# API URL'leri
urlpatterns += [
    path('api/', include(router.urls)),
    
    # İki faktörlü kimlik doğrulama URL'leri
    path('api/2fa/setup/', TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('api/2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('api/2fa/disable/', TwoFactorDisableView.as_view(), name='2fa_disable'),
    
    # İzin yönetimi URL'leri
    path('api/check-permission/', CheckPermissionView.as_view(), name='check_permission'),
    path('api/user-permissions/', UserPermissionsView.as_view(), name='user_permissions'),
    path('api/delegate-permission/', DelegatePermissionView.as_view(), name='delegate_permission'),
    path('api/revoke-permission/', RevokePermissionView.as_view(), name='revoke_permission'),
    
    # Django REST Framework auth URL'leri
    path('api-auth/', include('rest_framework.urls')),
]

urlpatterns += [
    # API Dokümantasyonu
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += [
    path('metrics/', metrics, name='metrics'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core apps
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('permissions/', include('permissions.urls')),
    
    # Business apps 
    path('finance/', include('finance.urls')),
    path('accounting/', include('finance.accounting.urls')),
    path('banking/', include('finance.banking.urls')),
    path('einvoice/', include('finance.einvoice.urls')),
    
    # Operation apps
    path('stock/', include('stock_management.urls')),
    path('assets/', include('assets.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),
    path('virtual-company/', include('virtual_company.urls')),
    path('analytics/', include('analytics.urls')),
    path('seo/', include('seo.urls')),
    path('blockchain/', include('blockchain.urls')),
    
    # Games
    path('games/', include('games.urls')),
    
    # API endpoints
    path('api/v1/', include('config.api_router')),
    
    # Health checks
    path('health/', include('health_check.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)