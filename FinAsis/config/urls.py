from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# View'ları import et
from .views import home, privacy_policy, terms_view, help_content_api, kvkk_view
from FinAsis.views import dashboard, education, pricing, legal, contact

from FinAsis.apps.accounting.admin import FinAsisAdminSite
from django.contrib import admin as django_admin

finasis_admin_site = FinAsisAdminSite()
finasis_admin_site._registry = django_admin.site._registry

# Tüm admin kayıtlarını yeni admin site'ye taşı
from FinAsis.apps.accounting import admin as accounting_admin
from FinAsis.apps.accounts import admin as accounts_admin
from FinAsis.apps.games import admin as games_admin
from FinAsis.apps.ai_assistant import admin as ai_admin
from FinAsis.apps.blockchain import admin as blockchain_admin

schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version='v1',
        description="FinAsis API dokümantasyonu",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    # Yönetici Paneli
    path('admin/', finasis_admin_site.urls),

    # Ana Sayfa
    path('', home, name='home'),

    # Gizlilik Politikası Sayfası
    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    # Kullanım Koşulları
    path('terms/', terms_view, name='terms'),

    # Uygulama URL'leri
    path('accounting/', include('FinAsis.apps.accounting.urls')),
    path('accounts/', include('FinAsis.apps.accounts.urls')),
    path('games/', include('FinAsis.apps.games.urls')),
    path('finance/', include('FinAsis.apps.finance.urls')),
    path('ai-assistant/', include('FinAsis.apps.ai_assistant.urls')),
    path('blockchain/', include('FinAsis.apps.blockchain.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('education/', education, name='education'),
    path('pricing/', pricing, name='pricing'),
    path('legal/', legal, name='legal'),
    path('legal/kvkk/', kvkk_view, name='kvkk'),
    path('contact/', contact, name='contact'),
    # Basit yardım içeriği API'si (dev placeholder)
    path('yonetim/api/help-content/', help_content_api, name='help_content'),
    path('favicon.ico', RedirectView.as_view(url='/static/common/favicon.ico', permanent=True)),

    # Sağlık ve dokümantasyon
    path('health/', health_check),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Medya dosyaları (sadece DEBUG modda servis edilir)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
