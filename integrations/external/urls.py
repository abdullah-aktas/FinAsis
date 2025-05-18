# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'external_integrations'

urlpatterns = [
    path('', views.IntegrationProviderListView.as_view(), name='integration_provider_list'),
    path('create/', views.IntegrationProviderCreateView.as_view(), name='integration_provider_create'),
    path('<int:pk>/', views.IntegrationProviderDetailView.as_view(), name='integration_provider_detail'),
    path('<int:pk>/update/', views.IntegrationProviderUpdateView.as_view(), name='integration_provider_update'),
    path('<int:pk>/delete/', views.IntegrationProviderDeleteView.as_view(), name='integration_provider_delete'),
    path('integrations/', views.IntegrationListView.as_view(), name='integration_list'),
    path('integrations/create/', views.IntegrationCreateView.as_view(), name='integration_create'),
    path('integrations/<int:pk>/', views.IntegrationDetailView.as_view(), name='integration_detail'),
    path('integrations/<int:pk>/update/', views.IntegrationUpdateView.as_view(), name='integration_update'),
    path('integrations/<int:pk>/delete/', views.IntegrationDeleteView.as_view(), name='integration_delete'),
    path('webhooks/', views.WebhookEndpointListView.as_view(), name='webhook_endpoint_list'),
    path('webhooks/create/', views.WebhookEndpointCreateView.as_view(), name='webhook_endpoint_create'),
    path('webhooks/<int:pk>/', views.WebhookEndpointDetailView.as_view(), name='webhook_endpoint_detail'),
    path('webhooks/<int:pk>/update/', views.WebhookEndpointUpdateView.as_view(), name='webhook_endpoint_update'),
    path('webhooks/<int:pk>/delete/', views.WebhookEndpointDeleteView.as_view(), name='webhook_endpoint_delete'),
    path('templates/', views.IntegrationTemplateListView.as_view(), name='integration_template_list'),
    path('templates/create/', views.IntegrationTemplateCreateView.as_view(), name='integration_template_create'),
    path('templates/<int:pk>/', views.IntegrationTemplateDetailView.as_view(), name='integration_template_detail'),
    path('templates/<int:pk>/update/', views.IntegrationTemplateUpdateView.as_view(), name='integration_template_update'),
    path('templates/<int:pk>/delete/', views.IntegrationTemplateDeleteView.as_view(), name='integration_template_delete'),
] 