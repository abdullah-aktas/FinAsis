# -*- coding: utf-8 -*-
"""
Finance uygulaması URL yapılandırmaları
"""

from django.urls import include, path
from .api.urls import urlpatterns as api_urlpatterns
from .urls.web_urls import urlpatterns as web_urlpatterns

app_name = 'finance'

# Delegate to web and api url modules to avoid duplication; keep this file minimal
urlpatterns = []
urlpatterns += web_urlpatterns
urlpatterns += api_urlpatterns