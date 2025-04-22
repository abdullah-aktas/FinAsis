from django.urls import path
from . import views
from .views import ocr

app_name = 'ai_assistant'

urlpatterns = [
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