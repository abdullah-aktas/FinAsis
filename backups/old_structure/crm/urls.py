# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Müşteri URL'leri
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # İletişim Kişisi URL'leri
    path('customers/<int:customer_id>/contacts/create/', views.contact_create, name='contact_create'),
    path('contacts/<int:pk>/update/', views.contact_update, name='contact_update'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    
    # Fırsat URL'leri
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/create/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:pk>/update/', views.opportunity_update, name='opportunity_update'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity_delete'),
    
    # Aktivite URL'leri
    path('customers/<int:customer_id>/activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/update/', views.activity_update, name='activity_update'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    
    # Belge URL'leri
    path('customers/<int:customer_id>/documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/update/', views.document_update, name='document_update'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    
    # Satış URL'leri
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/create/<int:customer_id>/', views.sale_create, name='sale_create_for_customer'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/update/', views.sale_update, name='sale_update'),
    path('sales/<int:pk>/confirm/', views.sale_confirm, name='sale_confirm'),
    path('sales/<int:pk>/cancel/', views.sale_cancel, name='sale_cancel'),
    path('sales/<int:pk>/create-invoice/', views.create_invoice, name='create_invoice'),
    path('sales/<int:pk>/sync-accounting/', views.sync_accounting, name='sync_accounting'),
    path('e-documents/<int:pk>/update-status/', views.update_document_status, name='update_document_status'),
    
    # E-fatura ve muhasebe entegrasyonu
    path('customers/<int:pk>/check-einvoice/', views.check_customer_einvoice, name='check_customer_einvoice'),
    path('customers/<int:pk>/sync-accounting/', views.sync_customer_accounting, name='sync_customer_accounting'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Kampanya URL'leri
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/create/', views.campaign_create, name='campaign_create'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:pk>/update/', views.campaign_update, name='campaign_update'),
    path('campaigns/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('campaigns/<int:pk>/performance/', views.campaign_performance, name='campaign_performance'),
] 