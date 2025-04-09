"""
URL configuration for finasis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('education/', include('education.urls')),
    path('virtual-company/', include('virtual_company.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),
    path('games/', include('game_app.urls')),
    path('accounting/', include('accounting.urls')),
    path('blockchain/', include('blockchain.urls')),
    path('crm/', include('crm.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

