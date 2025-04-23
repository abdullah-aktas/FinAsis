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
    
    # JWT Token URL'leri
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # İki faktörlü kimlik doğrulama URL'leri
    path('api/2fa/setup/', TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('api/2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('api/2fa/disable/', TwoFactorDisableView.as_view(), name='2fa_disable'),
    
    # İzin yönetimi URL'leri
    path('api/check-permission/', CheckPermissionView.as_view(), name='check_permission'),
    path('api/user-permissions/', UserPermissionsView.as_view(), name='user_permissions'),
    path('api/delegate-permission/', DelegatePermissionView.as_view(), name='delegate_permission'),
    path('api/revoke-permission/', RevokePermissionView.as_view(), name='revoke_permission'),
    
    # Kullanıcı yönetimi URL'leri
    path('api/users/', include('users.urls')),
    
    # Django REST Framework auth URL'leri
    path('api-auth/', include('rest_framework.urls')),
    
    # Django Allauth URL'leri
    path('accounts/', include('allauth.urls')),
]

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