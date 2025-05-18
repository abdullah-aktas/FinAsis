# -*- coding: utf-8 -*-
"""
SEO Modülü - URL Yapılandırması
------------------------------
Bu dosya, Arama Motoru Optimizasyonu modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/seo/ - Ana SEO API endpoint'i
- /api/v1/seo/metadata/ - Meta veri yönetimi
- /api/v1/seo/keywords/ - Anahtar kelime yönetimi
- /api/v1/seo/analytics/ - SEO analitikleri
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'seo'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'metadata', views.SEOMetadataViewSet, basename='metadata')
router.register(r'keywords', views.SEOKeywordViewSet, basename='keyword')
router.register(r'analytics', views.SEOAnalyticsViewSet, basename='analytics')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Meta Veri Yönetimi
    path('metadata/', views.SEOMetadataListView.as_view(), name='metadata-list'),
    path('metadata/<uuid:pk>/', views.SEOMetadataDetailView.as_view(), name='metadata-detail'),
    path('metadata/create/', views.SEOMetadataCreateView.as_view(), name='metadata-create'),
    path('metadata/<uuid:pk>/update/', views.SEOMetadataUpdateView.as_view(), name='metadata-update'),
    path('metadata/<uuid:pk>/delete/', views.SEOMetadataDeleteView.as_view(), name='metadata-delete'),
    
    # Anahtar Kelime Yönetimi
    path('keywords/', views.SEOKeywordListView.as_view(), name='keyword-list'),
    path('keywords/<uuid:pk>/', views.SEOKeywordDetailView.as_view(), name='keyword-detail'),
    path('keywords/create/', views.SEOKeywordCreateView.as_view(), name='keyword-create'),
    path('keywords/<uuid:pk>/update/', views.SEOKeywordUpdateView.as_view(), name='keyword-update'),
    path('keywords/<uuid:pk>/delete/', views.SEOKeywordDeleteView.as_view(), name='keyword-delete'),
    
    # SEO Analitikleri
    path('analytics/', views.SEOAnalyticsListView.as_view(), name='analytics-list'),
    path('analytics/<uuid:pk>/', views.SEOAnalyticsDetailView.as_view(), name='analytics-detail'),
    path('analytics/create/', views.SEOAnalyticsCreateView.as_view(), name='analytics-create'),
    path('analytics/<uuid:pk>/update/', views.SEOAnalyticsUpdateView.as_view(), name='analytics-update'),
    path('analytics/<uuid:pk>/delete/', views.SEOAnalyticsDeleteView.as_view(), name='analytics-delete'),
    
    # SEO Araçları
    path('tools/robots.txt', views.robots_txt, name='robots-txt'),
    path('tools/sitemap.xml', views.sitemap_xml, name='sitemap-xml'),
    path('tools/analyze/', views.AnalyzeView.as_view(), name='analyze'),
    path('tools/optimize/', views.OptimizeView.as_view(), name='optimize'),
] 