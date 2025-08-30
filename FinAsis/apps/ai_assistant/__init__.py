# -*- coding: utf-8 -*-
"""
Yapay zeka destekli finansal asistan ve otomasyon modüllerini içeren uygulama.
"""
default_app_config = 'ai_assistant.apps.AIAssistantConfig'

from rest_framework.routers import DefaultRouter
from .api import MyViewSet

router = DefaultRouter()
router.register(r'ai-assistant', MyViewSet, basename='ai-assistant')
urlpatterns = router.urls
