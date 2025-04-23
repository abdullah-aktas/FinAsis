from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'metadata', views.SEOMetadataViewSet, basename='metadata')
router.register(r'redirects', views.SEORedirectViewSet, basename='redirects')
router.register(r'keywords', views.SEOKeywordViewSet, basename='keywords')
router.register(r'analytics', views.SEOAnalyticsViewSet, basename='analytics')

app_name = 'seo'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Template URLs
    path('metadata/', views.SEOMetadataListView.as_view(), name='metadata_list'),
    path('metadata/<int:pk>/', views.SEOMetadataDetailView.as_view(), name='metadata_detail'),
    path('metadata/create/', views.SEOMetadataCreateView.as_view(), name='metadata_create'),
    path('metadata/<int:pk>/update/', views.SEOMetadataUpdateView.as_view(), name='metadata_update'),
    path('metadata/<int:pk>/delete/', views.SEOMetadataDeleteView.as_view(), name='metadata_delete'),
    
    # SEO Tools URLs
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
] 