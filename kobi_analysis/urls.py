"""
KOBİ Analysis URLs
"""
from django.urls import path
from . import views

app_name = 'kobi_analysis'

urlpatterns = [
    # Main Dashboard
    path('', views.kobi_dashboard, name='dashboard'),
    
    # Financial Analysis
    path('analysis/<int:analysis_id>/', views.financial_analysis_detail, name='analysis_detail'),
    path('analysis/generate/', views.generate_analysis, name='generate_analysis'),
    
    # Planning & Forecasting
    path('budget/', views.budget_planning, name='budget_planning'),
    path('cash-flow/', views.cash_flow_forecast, name='cash_flow_forecast'),
    path('goals/', views.goals_tracking, name='goals_tracking'),
    
    # Analysis Tools
    path('risk/', views.risk_management, name='risk_management'),
    path('competitor/', views.competitor_analysis, name='competitor_analysis'),
    path('swot/', views.swot_analysis, name='swot_analysis'),
    path('metrics/', views.performance_metrics, name='performance_metrics'),
    path('reports/', views.advisory_reports, name='advisory_reports'),
    
    # AJAX Endpoints
    path('ajax/quick-stats/', views.ajax_quick_stats, name='ajax_quick_stats'),
    path('ajax/health-trend/', views.ajax_health_trend, name='ajax_health_trend'),
]

