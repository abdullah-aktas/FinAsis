from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Konfigürasyon
    path('config/<str:integration_type>/', views.save_config, name='save_config'),
    
    # Senkronizasyon
    path('sync/<int:integration_id>/', views.run_sync, name='run_sync'),
    
    # Loglar
    path('logs/<int:integration_id>/', views.get_logs, name='get_logs'),
    
    # Webhook
    path('webhook/<str:integration_type>/', views.handle_webhook, name='handle_webhook'),
] 