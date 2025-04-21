from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core import views
from apps.core.views import admin as admin_views
from django.conf.urls.i18n import i18n_patterns

# Language-independent URLs
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Dil değiştirme için
    path('health/', views.health_check, name='health_check'),  # Sağlık kontrolü endpoint
]

# Language-dependent URLs
urlpatterns += i18n_patterns(
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('api-auth/', include('rest_framework.urls')),
    path('accounting/', include(('apps.accounting.urls', 'accounting'), namespace='accounting')),
    path('crm/', include(('apps.crm.urls', 'crm'), namespace='crm')),
    path('finance/', include(('apps.finance.urls', 'finance'), namespace='finance')),  # Finance uygulaması
    path('pricing/', views.pricing, name='pricing'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript'), name='service-worker.js'),
    path('api/', include('apps.api.urls')),
    path('edocument/', include('edocument.urls')),
    path('assistant/', include('apps.assistant.urls')),
    # Kullanıcı yönetimi için URL'ler
    path('users/', include(('apps.users.urls', 'users'), namespace='users')),
    # Admin Panel
    path('admin/', include(([
        path('', admin_views.admin_index, name='index'),
        path('users/', admin_views.admin_users_list, name='users_list'),
        path('users/add/', admin_views.admin_users_add, name='users_add'),
        path('permissions/', admin_views.admin_permissions, name='permissions'),
        path('transactions/', admin_views.admin_transactions, name='transactions'),
        path('reports/', admin_views.admin_reports, name='reports'),
        path('settings/', admin_views.admin_settings, name='settings'),
        path('logs/', admin_views.admin_logs, name='logs'),
        path('backups/', admin_views.admin_backups, name='backups'),
        path('integrations/', admin_views.admin_integrations, name='integrations'),
        path('ai-assistant/', admin_views.admin_ai_assistant, name='ai_assistant'),
        path('notifications/', admin_views.admin_notifications, name='notifications'),
        path('help/', admin_views.admin_help, name='help'),
        path('documentation/', admin_views.admin_documentation, name='documentation'),
        path('support/', admin_views.admin_support, name='support'),
        path('profile/', admin_views.admin_profile, name='profile'),
    ], 'admin'))),
    prefix_default_language=True  # Varsayılan dil için de prefix ekle
)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 