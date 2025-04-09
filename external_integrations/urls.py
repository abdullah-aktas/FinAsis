from django.urls import path
from . import views

app_name = 'external_integrations'

urlpatterns = [
    # Entegrasyon Şablonları
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),
    path('templates/create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/update/', views.TemplateUpdateView.as_view(), name='template_update'),
    path('templates/<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
    
    # Entegrasyon Sihirbazı
    path('wizard/', views.integration_wizard, name='integration_wizard'),
    
    # API Endpoints
    path('api/templates/', views.api_templates, name='api_templates'),
    path('api/templates/<int:pk>/', views.api_template_detail, name='api_template_detail'),
    path('api/integrations/<int:pk>/test/', views.api_test_integration, name='api_test_integration'),
    path('api/webhooks/<int:pk>/test/', views.api_test_webhook, name='api_test_webhook'),
    
    # Entegrasyon Sağlayıcıları
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('providers/<int:pk>/', views.ProviderDetailView.as_view(), name='provider_detail'),
    path('providers/create/', views.ProviderCreateView.as_view(), name='provider_create'),
    path('providers/<int:pk>/update/', views.ProviderUpdateView.as_view(), name='provider_update'),
    path('providers/<int:pk>/delete/', views.ProviderDeleteView.as_view(), name='provider_delete'),
    
    # Entegrasyonlar
    path('integrations/', views.IntegrationListView.as_view(), name='integration_list'),
    path('integrations/<int:pk>/', views.IntegrationDetailView.as_view(), name='integration_detail'),
    path('integrations/create/', views.IntegrationCreateView.as_view(), name='integration_create'),
    path('integrations/<int:pk>/update/', views.IntegrationUpdateView.as_view(), name='integration_update'),
    path('integrations/<int:pk>/delete/', views.IntegrationDeleteView.as_view(), name='integration_delete'),
    
    # Webhook Endpoint'leri
    path('webhooks/', views.WebhookListView.as_view(), name='webhook_list'),
    path('webhooks/<int:pk>/', views.WebhookDetailView.as_view(), name='webhook_detail'),
    path('webhooks/create/', views.WebhookCreateView.as_view(), name='webhook_create'),
    path('webhooks/<int:pk>/update/', views.WebhookUpdateView.as_view(), name='webhook_update'),
    path('webhooks/<int:pk>/delete/', views.WebhookDeleteView.as_view(), name='webhook_delete'),
] 