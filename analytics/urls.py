"""
Analytics Modülü - URL Yapılandırması
-----------------------------------
Bu dosya, Analitik modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/analytics/ - Ana analitik API endpoint'i
- /api/v1/analytics/dashboard/ - Analitik panelleri
- /api/v1/analytics/reports/ - Analitik raporları
- /api/v1/analytics/visualizations/ - Veri görselleştirmeleri
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'analytics'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'dashboards', views.DashboardViewSet, basename='dashboard')
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'visualizations', views.VisualizationViewSet, basename='visualization')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Analitik Panelleri
    path('dashboard/', views.DashboardListView.as_view(), name='dashboard-list'),
    path('dashboard/<uuid:pk>/', views.DashboardDetailView.as_view(), name='dashboard-detail'),
    path('dashboard/create/', views.DashboardCreateView.as_view(), name='dashboard-create'),
    path('dashboard/<uuid:pk>/update/', views.DashboardUpdateView.as_view(), name='dashboard-update'),
    path('dashboard/<uuid:pk>/delete/', views.DashboardDeleteView.as_view(), name='dashboard-delete'),
    
    # Analitik Raporları
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/<uuid:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report-create'),
    path('reports/<uuid:pk>/update/', views.ReportUpdateView.as_view(), name='report-update'),
    path('reports/<uuid:pk>/delete/', views.ReportDeleteView.as_view(), name='report-delete'),
    
    # Veri Görselleştirmeleri
    path('visualizations/', views.VisualizationListView.as_view(), name='visualization-list'),
    path('visualizations/<uuid:pk>/', views.VisualizationDetailView.as_view(), name='visualization-detail'),
    path('visualizations/create/', views.VisualizationCreateView.as_view(), name='visualization-create'),
    path('visualizations/<uuid:pk>/update/', views.VisualizationUpdateView.as_view(), name='visualization-update'),
    path('visualizations/<uuid:pk>/delete/', views.VisualizationDeleteView.as_view(), name='visualization-delete'),
    
    # Analitik Araçları
    path('tools/data-export/', views.DataExportView.as_view(), name='data-export'),
    path('tools/data-import/', views.DataImportView.as_view(), name='data-import'),
    path('tools/data-cleanup/', views.DataCleanupView.as_view(), name='data-cleanup'),
] 