# -*- coding: utf-8 -*-
"""
Advisors URLs
Mali Müşavir ve Vergi Danışmanlığı URL Yapılandırması
"""
from django.urls import path, include
from . import views

app_name = 'advisors'

urlpatterns = [
    # Ana dashboard
    path('', views.advisor_dashboard, name='dashboard'),
    
    # Müşteri yönetimi
    path('clients/', views.client_list, name='client_list'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    
    # Beyanname yönetimi
    path('declarations/', views.declaration_list, name='declaration_list'),
    path('declarations/create/', views.declaration_create, name='declaration_create'),
    
    # Danışmanlık oturumları
    path('consultations/', views.consultation_list, name='consultation_list'),
    
    # Doküman yönetimi
    path('documents/', views.document_list, name='document_list'),
    
    # Uyarılar
    path('alerts/', views.alert_list, name='alert_list'),
    
    # Faturalar
    path('invoices/', views.invoice_list, name='invoice_list'),
    
    # AJAX endpoints
    path('ajax/client-compliance/<int:client_id>/', views.ajax_client_compliance, name='ajax_client_compliance'),
    path('ajax/dashboard-stats/', views.ajax_dashboard_stats, name='ajax_dashboard_stats'),
    
    # Mali Müşavir Marketplace
    path('marketplace/', include('advisors.urls.marketplace_urls')),
]

