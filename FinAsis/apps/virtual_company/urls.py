# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VirtualCompanyViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'companies', VirtualCompanyViewSet, basename='company')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),

    path('virtual_company/', views.VirtualCompanyListView.as_view(), name='virtual_company_list'),
    path('virtual_company/<int:pk>/', views.VirtualCompanyDetailView.as_view(), name='virtual_company_detail'),
    path('virtual_company/create/', views.VirtualCompanyCreateView.as_view(), name='virtual_company_create'),
    path('virtual_company/<int:pk>/update/', views.VirtualCompanyUpdateView.as_view(), name='virtual_company_update'),
    path('virtual_company/<int:pk>/delete/', views.VirtualCompanyDeleteView.as_view(), name='virtual_company_delete'),
    path('product/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),] 