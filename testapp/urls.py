# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'testapp'

urlpatterns = [
    # Ana sayfa
    path('', views.home, name='home'),
    
    # Temel test endpoint'leri
    path('test/', views.TestView.as_view(), name='test'),
    path('protected-test/', views.ProtectedTestView.as_view(), name='protected_test'),
    path('api-test/', views.api_test, name='api_test'),
    
    # Sistem kontrol endpoint'leri
    path('health/', views.health_check, name='health_check'),
    path('performance/', views.performance_test, name='performance_test'),
    
    # API versiyonlama
    path('api/v1/test/', views.TestView.as_view(), name='api_v1_test'),
    path('api/v2/test/', views.TestView.as_view(), name='api_v2_test'),
] 