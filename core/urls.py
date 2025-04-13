from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('customer-management/', include('customer_management.urls')),
    path('company-management/', include('company_management.urls')),
    path('ext-services/', include('ext_services.urls')),
    path('seo-management/', include('seo_management.urls')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('education/', include(('education.urls', 'education'), namespace='education')),
    path('ai-assistant/', include(('ai_assistant.urls', 'ai_assistant'), namespace='ai_assistant')),
    path('blockchain/', include(('blockchain.urls', 'blockchain'), namespace='blockchain')),
    path('virtual-company/', include(('virtual_company.urls', 'virtual_company'), namespace='virtual_company')),
    path('game/', include(('game_app.urls', 'game_app'), namespace='game_app')),
    path('analytics/', include(('analytics.urls', 'analytics'), namespace='analytics')),
    path('api-auth/', include('rest_framework.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounting/', include(('accounting.urls', 'accounting'), namespace='accounting')),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 