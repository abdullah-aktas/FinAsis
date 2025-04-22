from django.urls import path
from . import views
from .views import ocr

app_name = 'ai_assistant'

urlpatterns = [
    # UserInteraction URLs
    path('userinteraction/', views.UserInteractionListView.as_view(), name='userinteraction_list'),
    path('userinteraction/<int:pk>/', views.UserInteractionDetailView.as_view(), name='userinteraction_detail'),
    path('userinteraction/create/', views.UserInteractionCreateView.as_view(), name='userinteraction_create'),
    path('userinteraction/<int:pk>/update/', views.UserInteractionUpdateView.as_view(), name='userinteraction_update'),
    path('userinteraction/<int:pk>/delete/', views.UserInteractionDeleteView.as_view(), name='userinteraction_delete'),

    # FinancialPrediction URLs
    path('financialprediction/', views.FinancialPredictionListView.as_view(), name='financialprediction_list'),
    path('financialprediction/<int:pk>/', views.FinancialPredictionDetailView.as_view(), name='financialprediction_detail'),
    path('financialprediction/create/', views.FinancialPredictionCreateView.as_view(), name='financialprediction_create'),
    path('financialprediction/<int:pk>/update/', views.FinancialPredictionUpdateView.as_view(), name='financialprediction_update'),
    path('financialprediction/<int:pk>/delete/', views.FinancialPredictionDeleteView.as_view(), name='financialprediction_delete'),

    # FinancialReport URLs
    path('financialreport/', views.FinancialReportListView.as_view(), name='financialreport_list'),
    path('financialreport/<int:pk>/', views.FinancialReportDetailView.as_view(), name='financialreport_detail'),
    path('financialreport/create/', views.FinancialReportCreateView.as_view(), name='financialreport_create'),
    path('financialreport/<int:pk>/update/', views.FinancialReportUpdateView.as_view(), name='financialreport_update'),
    path('financialreport/<int:pk>/delete/', views.FinancialReportDeleteView.as_view(), name='financialreport_delete'),

    # AnomalyDetection URLs
    path('anomalydetection/', views.AnomalyDetectionListView.as_view(), name='anomalydetection_list'),
    path('anomalydetection/<int:pk>/', views.AnomalyDetectionDetailView.as_view(), name='anomalydetection_detail'),
    path('anomalydetection/create/', views.AnomalyDetectionCreateView.as_view(), name='anomalydetection_create'),
    path('anomalydetection/<int:pk>/update/', views.AnomalyDetectionUpdateView.as_view(), name='anomalydetection_update'),
    path('anomalydetection/<int:pk>/delete/', views.AnomalyDetectionDeleteView.as_view(), name='anomalydetection_delete'),

    # TrendAnalysis URLs
    path('trendanalysis/', views.TrendAnalysisListView.as_view(), name='trendanalysis_list'),
    path('trendanalysis/<int:pk>/', views.TrendAnalysisDetailView.as_view(), name='trendanalysis_detail'),
    path('trendanalysis/create/', views.TrendAnalysisCreateView.as_view(), name='trendanalysis_create'),
    path('trendanalysis/<int:pk>/update/', views.TrendAnalysisUpdateView.as_view(), name='trendanalysis_update'),
    path('trendanalysis/<int:pk>/delete/', views.TrendAnalysisDeleteView.as_view(), name='trendanalysis_delete'),

    # Nakit Akışı Tahmini
    path('forecast/', views.forecast_view, name='forecast'),
    path('api/forecast/', views.forecast_api, name='forecast_api'),
    
    # Risk Skorlama
    path('risk-score/<int:customer_id>/', views.risk_score_view, name='risk_score'),
    path('api/risk-score/<int:customer_id>/', views.risk_score_api, name='risk_score_api'),
    
    # OCR İşlemleri
    path('ocr/upload/', views.ocr_upload_view, name='ocr_upload'),
    path('api/ocr/process/', views.ocr_process_api, name='ocr_process_api'),
    path('ocr/process/', ocr.process_document, name='ocr_process'),
    path('ocr/status/', ocr.ocr_status, name='ocr_status'),
] 