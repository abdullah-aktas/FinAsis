from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# View'ları import et
from .views import (
    home,
    privacy_policy,
    terms_view,
    help_content_api,
    kvkk_view,
    finance_home,
    finance_reports,
    education_index,
    games_all,
    tradesim_play,
    tradesim_detail,
    blockchain,
    profile,
    investor_info_form,
    corporate_offer,
)
from src.views import dashboard, education, pricing, legal, contact

from src.apps.accounting.admin import FinAsisAdminSite
from django.contrib import admin as django_admin

finasis_admin_site = FinAsisAdminSite()
finasis_admin_site._registry = django_admin.site._registry

# Tüm admin kayıtlarını yeni admin site'ye taşı
from src.apps.accounting import admin as accounting_admin
from src.apps.accounts import admin as accounts_admin
from src.apps.games import admin as games_admin
from src.apps.ai_assistant import admin as ai_admin
from src.apps.blockchain import admin as blockchain_admin

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
        path('virtual_company/', include('FinAsis.apps.virtual_company.urls')),
    path('accounts/', include('FinAsis.apps.accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('games/', include('FinAsis.apps.games.urls')),
    path('finance/', include('FinAsis.apps.finance.urls')),
    path('ai-assistant/', include('FinAsis.apps.ai_assistant.urls')),
    path('blockchain/', blockchain, name='blockchain'),
    path('finance/home/', finance_home, name='finance-home'),
    path('finance/reports/', finance_reports, name='finance-reports'),
    path('education/index/', education_index, name='education-index'),
    path('games/all/', games_all, name='games-all'),
    path('games/tradesim/play/', tradesim_play, name='tradesim-play'),
    path('games/tradesim/detail/', tradesim_detail, name='tradesim-detail'),
    path('accounts/profile/', profile, name='profile'),
    path('investor_info_form/', investor_info_form, name='investor_info_form'),
    path('dashboard/', dashboard, name='dashboard'),
    path('education/', education, name='education'),
    path('pricing/', pricing, name='pricing'),
    path('legal/', legal, name='legal'),
    path('common/', include('FinAsis.apps.common.urls')),
    path('legal/kvkk/', kvkk_view, name='kvkk'),
    path('contact/', contact, name='contact'),
    # i18n dil değiştirme endpointleri
    path('i18n/', include('django.conf.urls.i18n')),
    # Basit yardım içeriği API'si (dev placeholder)
    # Ürünler
    path('products/finans/', TemplateView.as_view(template_name='products/finans.html'), name='products-finans'),
    path('products/egitim/', TemplateView.as_view(template_name='products/egitim.html'), name='products-egitim'),
    path('products/blockchain/', TemplateView.as_view(template_name='products/blockchain.html'), name='products-blockchain'),
    path('products/oyunlar/', TemplateView.as_view(template_name='products/oyunlar.html'), name='products-oyunlar'),
    # Kurumsal
    path('corporate/', TemplateView.as_view(template_name='corporate.html'), name='corporate'),
    path('corporate/offer/', corporate_offer, name='corporate-offer'),
        path('corporate/about/', TemplateView.as_view(template_name='corporate/about.html'), name='corporate-about'),
        path('corporate/team/', TemplateView.as_view(template_name='corporate/team.html'), name='corporate-team'),
        path('corporate/sustainability/', TemplateView.as_view(template_name='corporate/sustainability.html'), name='corporate-sustainability'),
    # Çözümler
    path('solutions/entegrasyon/', TemplateView.as_view(template_name='solutions/entegrasyon.html'), name='solutions-entegrasyon'),
    path('solutions/raporlama/', TemplateView.as_view(template_name='solutions/raporlama.html'), name='solutions-raporlama'),
    path('solutions/analitik/', TemplateView.as_view(template_name='solutions/analitik.html'), name='solutions-analitik'),
    # Kaynaklar
    path('resources/', TemplateView.as_view(template_name='resources.html'), name='resources'),
        path('resources/guides/', TemplateView.as_view(template_name='resources/guides.html'), name='resources-guides'),
        path('resources/docs/', TemplateView.as_view(template_name='resources/docs.html'), name='resources-docs'),
        path('resources/training/', TemplateView.as_view(template_name='resources/training.html'), name='resources-training'),
    # Destek
    path('support/', TemplateView.as_view(template_name='support.html'), name='support'),
        path('support/live/', TemplateView.as_view(template_name='support/live.html'), name='support-live'),
        path('support/faq/', TemplateView.as_view(template_name='support/faq.html'), name='support-faq'),
        path('support/tech/', TemplateView.as_view(template_name='support/tech.html'), name='support-tech'),
    # Blog
    path('blog/', TemplateView.as_view(template_name='blog.html'), name='blog'),
        path('blog/news/', TemplateView.as_view(template_name='blog/news.html'), name='blog-news'),
        path('blog/expert/', TemplateView.as_view(template_name='blog/expert.html'), name='blog-expert'),
        path('blog/startup/', TemplateView.as_view(template_name='blog/startup.html'), name='blog-startup'),
    path('yonetim/api/help-content/', help_content_api, name='help_content'),
    path('favicon.ico', RedirectView.as_view(url='/static/common/favicon.ico', permanent=True)),
    # Yardım sayfası
    path('help/', TemplateView.as_view(template_name='help/index.html'), name='help'),

    # Sağlık ve dokümantasyon
    path('health/', health_check),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Medya dosyaları (sadece DEBUG modda servis edilir)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
