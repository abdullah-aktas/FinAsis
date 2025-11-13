# -*- coding: utf-8 -*-
"""
GIB Integrator URLs
Gelir İdaresi Başkanlığı Entegrasyon URL Yapılandırması
"""
from django.urls import path
from . import views

app_name = 'integrator_gib'

urlpatterns = [
    # Ana dashboard
    path('', views.gib_dashboard, name='dashboard'),
    
    # Yapılandırma
    path('config/', views.config_edit, name='config_edit'),
    
    # Gönderim yönetimi
    path('submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    
    # Sertifika yönetimi
    path('certificates/', views.certificate_list, name='certificate_list'),
    
    # AJAX endpoints
    path('ajax/test-connection/', views.ajax_test_connection, name='ajax_test_connection'),
    path('ajax/retry-submission/<int:submission_id>/', views.ajax_retry_submission, name='ajax_retry_submission'),
    path('ajax/dashboard-stats/', views.ajax_dashboard_stats, name='ajax_dashboard_stats'),
]

