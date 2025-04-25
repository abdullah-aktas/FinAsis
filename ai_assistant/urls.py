"""
AI Assistant Modülü - URL Yapılandırması
--------------------------------------
Bu dosya, Yapay Zeka Asistanı modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v2/ai-assistant/ - Ana AI asistan API endpoint'i
- /api/v2/ai-assistant/chat/ - Sohbet yönetimi
- /api/v2/ai-assistant/tasks/ - Görev yönetimi
- /api/v2/ai-assistant/analytics/ - AI analitikleri
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ai_assistant'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'analytics', views.AIAnalyticsViewSet, basename='analytics')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Sohbet Yönetimi
    path('chat/', views.ChatListView.as_view(), name='chat-list'),
    path('chat/<uuid:pk>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path('chat/create/', views.ChatCreateView.as_view(), name='chat-create'),
    path('chat/<uuid:pk>/update/', views.ChatUpdateView.as_view(), name='chat-update'),
    path('chat/<uuid:pk>/delete/', views.ChatDeleteView.as_view(), name='chat-delete'),
    
    # Görev Yönetimi
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<uuid:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task-create'),
    path('tasks/<uuid:pk>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<uuid:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    
    # AI Analitikleri
    path('analytics/', views.AIAnalyticsListView.as_view(), name='analytics-list'),
    path('analytics/<uuid:pk>/', views.AIAnalyticsDetailView.as_view(), name='analytics-detail'),
    path('analytics/create/', views.AIAnalyticsCreateView.as_view(), name='analytics-create'),
    path('analytics/<uuid:pk>/update/', views.AIAnalyticsUpdateView.as_view(), name='analytics-update'),
    path('analytics/<uuid:pk>/delete/', views.AIAnalyticsDeleteView.as_view(), name='analytics-delete'),
    
    # AI Araçları
    path('tools/summarize/', views.SummarizeView.as_view(), name='summarize'),
    path('tools/translate/', views.TranslateView.as_view(), name='translate'),
    path('tools/classify/', views.ClassifyView.as_view(), name='classify'),
    path('tools/generate/', views.GenerateView.as_view(), name='generate'),
] 