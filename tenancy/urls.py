# -*- coding: utf-8 -*-
"""
Tenancy URLs
Multi-Tenant Yönetim URL Yapılandırması
"""
from django.urls import path
from . import views

app_name = 'tenancy'

urlpatterns = [
    # Ana dashboard
    path('', views.tenant_dashboard, name='dashboard'),
    
    # Tenant yönetimi
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/create/', views.tenant_create, name='tenant_create'),
    path('tenants/<int:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    path('tenants/<int:tenant_id>/settings/', views.tenant_settings, name='tenant_settings'),
    
    # AJAX endpoints
    path('ajax/tenant-stats/<int:tenant_id>/', views.ajax_tenant_stats, name='ajax_tenant_stats'),
    path('ajax/toggle-status/<int:tenant_id>/', views.ajax_toggle_tenant_status, name='ajax_toggle_tenant_status'),
]

