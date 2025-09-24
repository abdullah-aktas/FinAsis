from django.contrib import admin
from django.urls import path, include
from django.templatetags.static import static as _static  # ensure static tag lib available for templates
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
    home, privacy_policy, terms_view, help_content_api, kvkk_view,
    corporate, resources_view, support_view,
    products_finans, products_egitim, products_blockchain, products_oyunlar,
    solutions_enteg, solutions_raporlama, solutions_analitik,
    corporate_offer, corporate_about, corporate_team, corporate_sustainability,
    corporate_careers, corporate_press, corporate_investors, corporate_security,
)
from .views import search_view
from .views import set_language_compat
from src.views import dashboard, education, pricing, legal, contact

from src.apps.accounting.admin import FinAsisAdminSite
from django.contrib import admin as django_admin

# Load all admin modules so default admin.site registry is complete
django_admin.autodiscover()

# Clone complete registry to custom AdminSite
finasis_admin_site = FinAsisAdminSite()
finasis_admin_site._registry = django_admin.site._registry.copy()

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
    return JsonResponse({'status': 'ok', 'version': 'v1'})

urlpatterns = [
    # Yönetici Paneli
    path('admin/', finasis_admin_site.urls),

    # Ana Sayfa
    path('', home, name='home'),

    # Gizlilik Politikası Sayfası
    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    # Kullanım Koşulları
    path('terms/', terms_view, name='terms'),

    # Uygulama URL'leri (namespaced)
    path('accounting/', include(('src.apps.accounting.urls', 'accounting'), namespace='accounting')),
    path('accounts/', include(('src.apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('accounts/', include('django.contrib.auth.urls')),  # auth views (namespacelenmiyor)
    path('games/', include(('src.apps.games.urls', 'games'), namespace='games')),
    path('finance/', include(('src.apps.finance.urls', 'finance'), namespace='finance')),
    path('ai-assistant/', include(('src.apps.ai_assistant.urls', 'ai_assistant'), namespace='ai_assistant')),
    path('blockchain/', include(('src.apps.blockchain.urls', 'blockchain'), namespace='blockchain')),
    path('dashboard/', dashboard, name='dashboard'),
    path('education/', education, name='education'),
        # Search (simple placeholder)
        path('search/', search_view, name='search'),
        # Sitemap
        path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml'), name='sitemap'),
    path('pricing/', pricing, name='pricing'),
    # Blog
    path('blog/', TemplateView.as_view(template_name='blog.html'), name='blog'),
    path('blog/news/', TemplateView.as_view(template_name='blog/news.html'), name='blog-news'),
    path('blog/expert/', TemplateView.as_view(template_name='blog/expert.html'), name='blog-expert'),
    path('blog/startup/', TemplateView.as_view(template_name='blog/startup.html'), name='blog-startup'),
    path('corporate/', corporate, name='corporate'),
    path('corporate/about/', corporate_about, name='corporate-about'),
    path('corporate/team/', corporate_team, name='corporate-team'),
    path('corporate/sustainability/', corporate_sustainability, name='corporate-sustainability'),
    path('corporate/careers/', corporate_careers, name='corporate-careers'),
    path('corporate/press/', corporate_press, name='corporate-press'),
    path('corporate/investors/', corporate_investors, name='corporate-investors'),
    path('corporate/security/', corporate_security, name='corporate-security'),
    path('corporate/offer/', corporate_offer, name='corporate-offer'),
    path('resources/', resources_view, name='resources'),
    path('resources/guides/', TemplateView.as_view(template_name='resources/guides.html'), name='resources-guides'),
    path('resources/docs/', TemplateView.as_view(template_name='resources/docs.html'), name='resources-docs'),
    path('resources/training/', TemplateView.as_view(template_name='resources/training.html'), name='resources-training'),
    path('support/', support_view, name='support'),
    path('support/live/', TemplateView.as_view(template_name='support/live.html'), name='support-live'),
    path('support/faq/', TemplateView.as_view(template_name='support/faq.html'), name='support-faq'),
    path('support/tech/', TemplateView.as_view(template_name='support/tech.html'), name='support-tech'),
    # Yönetim paneli (uygulama içi)
    path('yonetim/', include(('src.apps.management.urls', 'management'), namespace='management')),
    # Products
    path('products/finans/', products_finans, name='products_finans'),
    path('products/egitim/', products_egitim, name='products_egitim'),
    path('products/blockchain/', products_blockchain, name='products_blockchain'),
    path('products/oyunlar/', products_oyunlar, name='products_oyunlar'),
    # Billing
    path('billing/', include(('src.apps.billing.urls', 'billing'), namespace='billing')),
    # Solutions
    path('solutions/entegrasyon/', solutions_enteg, name='solutions_enteg'),
    path('solutions/raporlama/', solutions_raporlama, name='solutions_raporlama'),
    path('solutions/analitik/', solutions_analitik, name='solutions_analitik'),
    # Virtual Company app (namespaced)
        path('virtual_company/', include(('src.apps.virtual_company.urls', 'virtual_company'), namespace='virtual_company')),
    # PWA manifest temporary fix
    path('static/manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/manifest+json')),
    path('legal/', legal, name='legal'),
        path('common/', include('src.apps.common.urls')),
    path('legal/kvkk/', kvkk_view, name='kvkk'),
    path('contact/', contact, name='contact'),
    # API v1
    path('api/v1/health/', health_check, name='api-health'),
    path('api/v1/', include('src.api.urls')),
    # i18n dil değiştirme endpointleri (GET uyumlu override + include)
    path('i18n/setlang/', set_language_compat, name='set_language_compat'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('favicon.ico', RedirectView.as_view(url='/static/common/favicon.ico', permanent=True)),
    # Yardım sayfası
    path('help/', TemplateView.as_view(template_name='help/index.html'), name='help'),

    # Sağlık ve dokümantasyon
    path('health/', health_check),
    path('api/v1/health/', health_check, name='api-health'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Medya dosyaları (sadece DEBUG modda servis edilir)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
