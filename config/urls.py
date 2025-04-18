from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('customer-management/', include('apps.customers.urls')),
    path('company-management/', include('apps.company.urls')),
    path('ext-services/', include('apps.integrations.services.urls')),
    path('seo-management/', include('apps.seo.urls')),
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('ai-assistant/', include(('apps.ai_assistant.urls', 'ai_assistant'), namespace='ai_assistant')),
    path('blockchain/', include(('apps.blockchain.urls', 'blockchain'), namespace='blockchain')),
    path('virtual-company/', include(('apps.virtual_company.urls', 'virtual_company'), namespace='virtual_company')),
    path('games/', include(('apps.games.game_app.urls', 'game_app'), namespace='game_app')),
    path('analytics/', include(('apps.analytics.urls', 'analytics'), namespace='analytics')),
    path('api-auth/', include('rest_framework.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounting/', include(('apps.accounting.urls', 'accounting'), namespace='accounting')),
    path('crm/', include('apps.crm.urls')),
    # path('api/', include('apps.api.urls')),  # API URL'si geçici olarak kaldırıldı
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript'), name='service-worker.js'),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 