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
router.register(r'ai-models', views.AIModelViewSet)
router.register(r'user-interactions', views.UserInteractionViewSet)
router.register(r'financial-predictions', views.FinancialPredictionViewSet)
router.register(r'ai-feedback', views.AIFeedbackViewSet)
router.register(r'financial-reports', views.FinancialReportViewSet)
router.register(r'anomaly-detections', views.AnomalyDetectionViewSet)
router.register(r'trend-analysis', views.TrendAnalysisViewSet)
router.register(r'user-preferences', views.UserPreferenceViewSet)
router.register(r'ai-insights', views.AIInsightViewSet)
router.register(r'recommendations', views.RecommendationViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'market-analysis', views.MarketAnalysisViewSet)
router.register(r'chat', views.ChatViewSet, basename='chat')
router.register(r'financial-analysis', views.FinancialAnalysisViewSet, basename='financial-analysis')
router.register(r'ocr', views.OCRViewSet, basename='ocr')

urlpatterns = [
    path('', include(router.urls)),
] 