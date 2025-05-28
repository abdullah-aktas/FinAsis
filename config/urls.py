from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView

# View'ları import et
from .views import home, privacy_policy, terms_view
from FinAsis.views import dashboard, education, pricing, legal, contact

from FinAsis.apps.accounting.admin import FinAsisAdminSite

finasis_admin_site = FinAsisAdminSite()

# Tüm admin kayıtlarını yeni admin site'ye taşı
from FinAsis.apps.accounting import admin as accounting_admin
from FinAsis.apps.accounts import admin as accounts_admin
from FinAsis.apps.games import admin as games_admin
from FinAsis.apps.ai_assistant import admin as ai_admin
from FinAsis.apps.blockchain import admin as blockchain_admin

urlpatterns = [
    # Yönetici Paneli
    path('admin/', finasis_admin_site.urls),

    # Ana Sayfa
    path('', home, name='home'),
    path('', home),

    # Gizlilik Politikası Sayfası
    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    # Kullanım Koşulları
    path('terms/', terms_view, name='terms'),

    # Uygulama URL'leri
    path('accounting/', include('FinAsis.apps.accounting.urls')),
    path('accounts/', include('FinAsis.apps.accounts.urls')),
    path('games/', include('FinAsis.apps.games.urls')),
    path('ai-assistant/', include('FinAsis.apps.ai_assistant.urls')),
    path('blockchain/', include('FinAsis.apps.blockchain.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('education/', education, name='education'),
    path('pricing/', pricing, name='pricing'),
    path('legal/', legal, name='legal'),
    path('contact/', contact, name='contact'),
    path('favicon.ico', RedirectView.as_view(url='/static/common/favicon.ico', permanent=True)),
]

# Medya dosyaları (sadece DEBUG modda servis edilir)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
