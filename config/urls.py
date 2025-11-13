from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from config import oidc as oidc_config

from corporate import views as corporate_views
from core_ui import views as core_ui_views
from locale.views import set_language

urlpatterns = [
    path('', core_ui_views.landing_home, name='home'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('accounting/', include(('accounting.urls', 'accounting'), namespace='accounting')),
    path('ai-assistant/', include(('ai_assistant.urls', 'ai_assistant'), namespace='ai_assistant')),
    path('audit/', include(('audit.urls', 'audit'), namespace='audit')),
    path('billing/', include(('billing.urls', 'billing'), namespace='billing')),
    path('blockchain/', include(('blockchain.urls', 'blockchain'), namespace='blockchain')),
    path('common/', include(('common.urls', 'common'), namespace='common')),
    path('core-ui/', include(('core_ui.urls', 'core_ui'), namespace='core_ui')),
    path('education/', include(('education.urls', 'education'), namespace='education')),
    path('corporate/', include(('corporate.urls', 'corporate'), namespace='corporate')),
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),
    path('contact/', corporate_views.contact, name='contact'),
    path('search/', core_ui_views.site_search, name='search'),
    path('games/', include(('games.urls', 'games'), namespace='games')),
    path('integrations/gib/', include(('integrator_gib.urls', 'integrator_gib'), namespace='integrator_gib')),
    path('integrations/mock/', include(('integrator_mock.urls', 'integrator_mock'), namespace='integrator_mock')),
    path('kobi-analysis/', include(('kobi_analysis.urls', 'kobi_analysis'), namespace='kobi_analysis')),
    path('management/', include(('management.urls', 'management'), namespace='management')),
    path('developers/', include(('developer_portal.urls', 'developer_portal'), namespace='developer_portal')),
    path('partners/', include(('partners.urls', 'partners'), namespace='partners')),
    path('permissions/', include(('permissions.urls', 'permissions'), namespace='permissions')),
    path('security/', include(('security.urls', 'security'), namespace='security')),
    path('submissions/', include(('submissions.urls', 'submissions'), namespace='submissions')),
    path('tenancy/', include(('tenancy.urls', 'tenancy'), namespace='tenancy')),
    path('virtual-company/', include(('virtual_company.urls', 'virtual_company'), namespace='virtual_company')),
    path('api/dashboard/', include(('api.urls_dashboard', 'api_dashboard'), namespace='api_dashboard')),
    path('locale/', include(('locale.urls', 'locale'), namespace='locale')),
    path('set-language-compat/', set_language, name='set_language_compat'),
]

if 'django_prometheus' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('', include('django_prometheus.urls')),
    ]

MARKETING_ROUTES = [
    ('pricing/', 'pricing', 'pricing'),
    ('support/', 'support', 'support'),
    ('products/muhasebe/', 'products_muhasebe', 'products_muhasebe'),
    ('products/finans/', 'products_finans', 'products_finans'),
    ('products/egitim/', 'products_egitim', 'products_egitim'),
    ('products/blockchain/', 'products_blockchain', 'products_blockchain'),
    ('products/oyunlar/', 'products_oyunlar', 'products_oyunlar'),
    ('products/edonusum/', 'products_edonusum', 'products_edonusum'),
    ('products/edenetim/', 'products_edenetim', 'products_edenetim'),
    ('products/yapay-zeka/', 'products_yapay_zeka', 'products_yapay_zeka'),
    ('solutions/entegrasyon/', 'solutions_enteg', 'solutions_enteg'),
    ('solutions/raporlama/', 'solutions_raporlama', 'solutions_raporlama'),
    ('solutions/analitik/', 'solutions_analitik', 'solutions_analitik'),
    ('terms/', 'terms', 'terms'),
    ('privacy-policy/', 'privacy_policy', 'privacy_policy'),
    ('cookie-policy/', 'cookie_policy', 'cookie_policy'),
    ('legal/', 'legal', 'legal'),
    ('legal/kvkk/', 'legal_kvkk', 'legal_kvkk'),
    ('risk-warning/', 'risk_warning', 'risk_warning'),
    ('resources/cfo-playbook/', 'resources_cfo_playbook', 'resources_cfo_playbook'),
    ('resources/compliance-checklist/', 'resources_compliance_checklist', 'resources_compliance_checklist'),
    ('training/finance-dashboard/', 'training_finance_dashboard', 'training_finance_dashboard'),
    ('training/compliance-engine/', 'training_compliance_engine', 'training_compliance_engine'),
    ('training/gamification-students/', 'training_gamification_students', 'training_gamification_students'),
    ('developer/api/', 'developer_api', 'developer_api'),
    ('blog/', 'blog', 'blog'),
]

urlpatterns += [
    path('resources/', core_ui_views.resource_hub, name='resources'),
    path('resources/guides/', core_ui_views.resource_guides, name='resources_guides'),
    path('resources/docs/', core_ui_views.resource_docs, name='resources_docs'),
    path('resources/training/', core_ui_views.resource_training, name='resources_training'),
    path('resources/academy/', core_ui_views.resource_academy, name='resources_academy'),
    path('resources/developer-hub/', core_ui_views.resource_developer_hub, name='resources_developer_hub'),
    path('resources/partner-marketplace/', core_ui_views.resource_partner_marketplace, name='resources_partner_marketplace'),
]

urlpatterns += [
    path(route, core_ui_views.marketing_page, {'page_key': page_key}, name=name)
    for route, page_key, name in MARKETING_ROUTES
]
urlpatterns += [
    path(
        'favicon.ico',
        RedirectView.as_view(
            url=settings.STATIC_URL + 'common/favicon.ico',
            permanent=True
        ),
        name='favicon'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if oidc_config.OIDC_ENABLED and oidc_config.KEYCLOAK_CLIENT_SECRET:
    urlpatterns += [
        path('oidc/', include('mozilla_django_oidc.urls')),
    ]

