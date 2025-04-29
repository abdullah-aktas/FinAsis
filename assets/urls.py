# -*- coding: utf-8 -*-
from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'assets'

# API Router
router = DefaultRouter()
router.register(r'api/assets', views.AssetViewSet, basename='asset')
router.register(r'api/categories', views.AssetCategoryViewSet, basename='category')
router.register(r'api/maintenances', views.MaintenanceViewSet, basename='maintenance')
router.register(r'api/rentals', views.AssetRentalViewSet, basename='rental')

urlpatterns = [
    # Web Views
    path('', views.AssetListView.as_view(), name='asset_list'),
    path('dashboard/', views.AssetDashboardView.as_view(), name='dashboard'),
    path('asset/<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('asset/create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('asset/<int:pk>/update/', views.AssetUpdateView.as_view(), name='asset_update'),
    path('asset/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
    
    # API URLs
    *router.urls,
] 