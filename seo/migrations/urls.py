from django.urls import path
from . import views

app_name = 'seo'

urlpatterns = [
    # SEO Metadata URLs
    path('metadata/', views.SEOMetadataListView.as_view(), name='metadata_list'),
    path('metadata/<int:pk>/', views.SEOMetadataDetailView.as_view(), name='metadata_detail'),
    path('metadata/create/', views.SEOMetadataCreateView.as_view(), name='metadata_create'),
    path('metadata/<int:pk>/update/', views.SEOMetadataUpdateView.as_view(), name='metadata_update'),
    path('metadata/<int:pk>/delete/', views.SEOMetadataDeleteView.as_view(), name='metadata_delete'),

    # SEO Analysis URLs
    path('analysis/', views.SEOAnalysisListView.as_view(), name='analysis_list'),
    path('analysis/<int:pk>/', views.SEOAnalysisDetailView.as_view(), name='analysis_detail'),
    path('analysis/create/', views.SEOAnalysisCreateView.as_view(), name='analysis_create'),
    path('analysis/<int:pk>/update/', views.SEOAnalysisUpdateView.as_view(), name='analysis_update'),
    path('analysis/<int:pk>/delete/', views.SEOAnalysisDeleteView.as_view(), name='analysis_delete'),

    # Keyword Ranking URLs
    path('keywords/', views.KeywordRankingListView.as_view(), name='keyword_list'),
    path('keywords/<int:pk>/', views.KeywordRankingDetailView.as_view(), name='keyword_detail'),
    path('keywords/create/', views.KeywordRankingCreateView.as_view(), name='keyword_create'),
    path('keywords/<int:pk>/update/', views.KeywordRankingUpdateView.as_view(), name='keyword_update'),
    path('keywords/<int:pk>/delete/', views.KeywordRankingDeleteView.as_view(), name='keyword_delete'),

    # Competitor Analysis URLs
    path('competitors/', views.CompetitorAnalysisListView.as_view(), name='competitor_list'),
    path('competitors/<int:pk>/', views.CompetitorAnalysisDetailView.as_view(), name='competitor_detail'),
    path('competitors/create/', views.CompetitorAnalysisCreateView.as_view(), name='competitor_create'),
    path('competitors/<int:pk>/update/', views.CompetitorAnalysisUpdateView.as_view(), name='competitor_update'),
    path('competitors/<int:pk>/delete/', views.CompetitorAnalysisDeleteView.as_view(), name='competitor_delete'),

    # API URLs
    path('api/analyze-url/', views.analyze_url, name='analyze_url'),
    path('api/check-keyword-ranking/', views.check_keyword_ranking, name='check_keyword_ranking'),
] 