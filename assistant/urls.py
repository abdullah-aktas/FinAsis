# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from . import views

router = DefaultRouter()
router.register(r'sessions', views.ChatSessionViewSet, basename='session')
router.register(r'messages', views.ChatMessageViewSet, basename='message')
router.register(r'prompts', views.PagePromptViewSet, basename='prompt')
router.register(r'preferences', views.UserPreferenceViewSet, basename='preference')
router.register(r'capabilities', views.AssistantCapabilityViewSet, basename='capability')
router.register(r'performance', views.AssistantPerformanceViewSet, basename='performance')

app_name = 'assistant'

urlpatterns = [
    # API URL'leri
    path('api/', include(router.urls)),
    path('api/docs/', include_docs_urls(title='FinAsis Assistant API')),
    path('api/process-message/', views.process_chat_message, name='process-message'),

    # Web Arayüzü URL'leri
    path('sessions/', views.ChatSessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:pk>/', views.ChatSessionDetailView.as_view(), name='session-detail'),
    path('prompts/', views.PagePromptListView.as_view(), name='prompt-list'),
    path('preferences/', views.UserPreferenceUpdateView.as_view(), name='preference-update'),
] 