# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'asset_management'

urlpatterns = [
    path('', views.asset_dashboard, name='dashboard'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/update/', views.asset_update, name='asset_update'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path('assets/<int:asset_pk>/depreciation/create/', views.depreciation_create, name='depreciation_create'),
    path('assets/<int:asset_pk>/maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('assets/<int:asset_pk>/transfer/create/', views.asset_transfer_create, name='asset_transfer_create'),
    path('assets/<int:asset_pk>/disposal/create/', views.asset_disposal_create, name='asset_disposal_create'),
] 