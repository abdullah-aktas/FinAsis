from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounting/', include('accounting.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),
    path('crm/', include('crm.urls')),
    path('hr/', include('hr_management.urls')),
    path('virtual-company/', include('virtual_company.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 