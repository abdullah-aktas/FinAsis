# -*- coding: utf-8 -*-
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
try:
    router.register(r'ai-models', views.AIModelViewSet)
except AttributeError:
    pass
try:
    router.register(r'user-interactions', views.UserInteractionViewSet)
except AttributeError:
    pass
try:
    router.register(r'financial-predictions', views.FinancialPredictionViewSet)
except AttributeError:
    pass
try:
    router.register(r'ai-feedback', views.AIFeedbackViewSet)
except AttributeError:
    pass
try:
    router.register(r'financial-reports', views.FinancialReportViewSet)
except AttributeError:
    pass
try:
    router.register(r'anomaly-detections', views.AnomalyDetectionViewSet)
except AttributeError:
    pass
try:
    router.register(r'trend-analysis', views.TrendAnalysisViewSet)
except AttributeError:
    pass
try:
    router.register(r'user-preferences', views.UserPreferenceViewSet)
except AttributeError:
    pass
try:
    router.register(r'ai-insights', views.AIInsightViewSet)
except AttributeError:
    pass
try:
    router.register(r'recommendations', views.RecommendationViewSet)
except AttributeError:
    pass
try:
    router.register(r'notifications', views.NotificationViewSet)
except AttributeError:
    pass
try:
    router.register(r'market-analysis', views.MarketAnalysisViewSet)
except AttributeError:
    pass
try:
    router.register(r'chat', views.ChatViewSet, basename='chat')
except AttributeError:
    pass
try:
    router.register(r'financial-analysis', views.FinancialAnalysisViewSet, basename='financial-analysis')
except AttributeError:
    pass
try:
    router.register(r'ocr', views.OCRViewSet, basename='ocr')
except AttributeError:
    pass

urlpatterns = [
    # Canonical home name only
    path('api/', include(router.urls)),
    # ML tabanlı özel API endpointleri
    path('ml/risk-score/', views.risk_score_api, name='ml-risk-score'),
    path('ml/financial-forecast/', views.financial_forecast_api, name='ml-financial-forecast'),
    # Frontend eski link uyumluluğu
    path('forecast/', views.financial_forecast_api, name='forecast-alias'),
    path('ml/recommendation/', views.recommendation_api, name='ml-recommendation'),
    path('assistant/chat/', views.ai_assistant_chat, name='ai-assistant-chat'),
    path('ocr/', views.ocr_upload_view, name='ocr'),
    path('a_i_model/', views.AIModelListView.as_view(), name='a_i_model_list'),
    path('a_i_model/<int:pk>/', views.AIModelDetailView.as_view(), name='a_i_model_detail'),
    path('a_i_model/create/', views.AIModelCreateView.as_view(), name='a_i_model_create'),
    path('a_i_model/<int:pk>/update/', views.AIModelUpdateView.as_view(), name='a_i_model_update'),
    path('a_i_model/<int:pk>/delete/', views.AIModelDeleteView.as_view(), name='a_i_model_delete'),
    path('user_interaction/', views.UserInteractionListView.as_view(), name='user_interaction_list'),
    path('user_interaction/<int:pk>/', views.UserInteractionDetailView.as_view(), name='user_interaction_detail'),
    path('user_interaction/create/', views.UserInteractionCreateView.as_view(), name='user_interaction_create'),
    path('user_interaction/<int:pk>/update/', views.UserInteractionUpdateView.as_view(), name='user_interaction_update'),
    path('user_interaction/<int:pk>/delete/', views.UserInteractionDeleteView.as_view(), name='user_interaction_delete'),
    path('financial_prediction/', views.FinancialPredictionListView.as_view(), name='financial_prediction_list'),
    path('financial_prediction/<int:pk>/', views.FinancialPredictionDetailView.as_view(), name='financial_prediction_detail'),
    path('financial_prediction/create/', views.FinancialPredictionCreateView.as_view(), name='financial_prediction_create'),
    path('financial_prediction/<int:pk>/update/', views.FinancialPredictionUpdateView.as_view(), name='financial_prediction_update'),
    path('financial_prediction/<int:pk>/delete/', views.FinancialPredictionDeleteView.as_view(), name='financial_prediction_delete'),
    path('a_i_feedback/', views.AIFeedbackListView.as_view(), name='a_i_feedback_list'),
    path('a_i_feedback/<int:pk>/', views.AIFeedbackDetailView.as_view(), name='a_i_feedback_detail'),
    path('a_i_feedback/create/', views.AIFeedbackCreateView.as_view(), name='a_i_feedback_create'),
    path('a_i_feedback/<int:pk>/update/', views.AIFeedbackUpdateView.as_view(), name='a_i_feedback_update'),
    path('a_i_feedback/<int:pk>/delete/', views.AIFeedbackDeleteView.as_view(), name='a_i_feedback_delete'),
    path('financial_report/', views.FinancialReportListView.as_view(), name='financial_report_list'),
    path('financial_report/<int:pk>/', views.FinancialReportDetailView.as_view(), name='financial_report_detail'),
    path('financial_report/create/', views.FinancialReportCreateView.as_view(), name='financial_report_create'),
    path('financial_report/<int:pk>/update/', views.FinancialReportUpdateView.as_view(), name='financial_report_update'),
    path('financial_report/<int:pk>/delete/', views.FinancialReportDeleteView.as_view(), name='financial_report_delete'),
    path('anomaly_detection/', views.AnomalyDetectionListView.as_view(), name='anomaly_detection_list'),
    path('anomaly_detection/<int:pk>/', views.AnomalyDetectionDetailView.as_view(), name='anomaly_detection_detail'),
    path('anomaly_detection/create/', views.AnomalyDetectionCreateView.as_view(), name='anomaly_detection_create'),
    path('anomaly_detection/<int:pk>/update/', views.AnomalyDetectionUpdateView.as_view(), name='anomaly_detection_update'),
    path('anomaly_detection/<int:pk>/delete/', views.AnomalyDetectionDeleteView.as_view(), name='anomaly_detection_delete'),
    path('trend_analysis/', views.TrendAnalysisListView.as_view(), name='trend_analysis_list'),
    path('trend_analysis/<int:pk>/', views.TrendAnalysisDetailView.as_view(), name='trend_analysis_detail'),
    path('trend_analysis/create/', views.TrendAnalysisCreateView.as_view(), name='trend_analysis_create'),
    path('trend_analysis/<int:pk>/update/', views.TrendAnalysisUpdateView.as_view(), name='trend_analysis_update'),
    path('trend_analysis/<int:pk>/delete/', views.TrendAnalysisDeleteView.as_view(), name='trend_analysis_delete'),
    path('user_preference/', views.UserPreferenceListView.as_view(), name='user_preference_list'),
    path('user_preference/<int:pk>/', views.UserPreferenceDetailView.as_view(), name='user_preference_detail'),
    path('user_preference/create/', views.UserPreferenceCreateView.as_view(), name='user_preference_create'),
    path('user_preference/<int:pk>/update/', views.UserPreferenceUpdateView.as_view(), name='user_preference_update'),
    path('user_preference/<int:pk>/delete/', views.UserPreferenceDeleteView.as_view(), name='user_preference_delete'),
    path('a_i_insight/', views.AIInsightListView.as_view(), name='a_i_insight_list'),
    path('a_i_insight/<int:pk>/', views.AIInsightDetailView.as_view(), name='a_i_insight_detail'),
    path('a_i_insight/create/', views.AIInsightCreateView.as_view(), name='a_i_insight_create'),
    path('a_i_insight/<int:pk>/update/', views.AIInsightUpdateView.as_view(), name='a_i_insight_update'),
    path('a_i_insight/<int:pk>/delete/', views.AIInsightDeleteView.as_view(), name='a_i_insight_delete'),
    path('recommendation/', views.RecommendationListView.as_view(), name='recommendation_list'),
    path('recommendation/<int:pk>/', views.RecommendationDetailView.as_view(), name='recommendation_detail'),
    path('recommendation/create/', views.RecommendationCreateView.as_view(), name='recommendation_create'),
    path('recommendation/<int:pk>/update/', views.RecommendationUpdateView.as_view(), name='recommendation_update'),
    path('recommendation/<int:pk>/delete/', views.RecommendationDeleteView.as_view(), name='recommendation_delete'),
    path('notification/', views.NotificationListView.as_view(), name='notification_list'),
    path('notification/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('notification/create/', views.NotificationCreateView.as_view(), name='notification_create'),
    path('notification/<int:pk>/update/', views.NotificationUpdateView.as_view(), name='notification_update'),
    path('notification/<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
    path('market_analysis/', views.MarketAnalysisListView.as_view(), name='market_analysis_list'),
    path('market_analysis/<int:pk>/', views.MarketAnalysisDetailView.as_view(), name='market_analysis_detail'),
    path('market_analysis/create/', views.MarketAnalysisCreateView.as_view(), name='market_analysis_create'),
    path('market_analysis/<int:pk>/update/', views.MarketAnalysisUpdateView.as_view(), name='market_analysis_update'),
    path('market_analysis/<int:pk>/delete/', views.MarketAnalysisDeleteView.as_view(), name='market_analysis_delete'),
    path('', views.home, name='home'),
    # Aliases requested by front-end links
    path('chat/', views.ai_chat, name='chat_alias'),
    path('recommendation_list/', views.RecommendationListView.as_view(), name='recommendation_list_alias'),
    path('financial_report_list/', views.FinancialReportListView.as_view(), name='financial_report_list_alias'),
    path('market_analysis_list/', views.MarketAnalysisListView.as_view(), name='market_analysis_list_alias'),
] 