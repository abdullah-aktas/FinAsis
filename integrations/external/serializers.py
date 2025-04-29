# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    IntegrationProvider, IntegrationTemplate, Integration,
    IntegrationLog, WebhookEndpoint, WebhookRequest
)

class IntegrationProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationProvider
        fields = ['id', 'name', 'description', 'api_base_url', 'api_version', 'documentation_url', 'is_active']
        read_only_fields = ['created_at', 'updated_at']

class IntegrationTemplateSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = IntegrationTemplate
        fields = [
            'id', 'name', 'provider', 'provider_name', 'category', 'category_display',
            'description', 'icon', 'configuration_schema', 'default_settings', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

class IntegrationSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    integration_type_display = serializers.CharField(source='get_integration_type_display', read_only=True)

    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'provider', 'provider_name', 'template', 'template_name',
            'integration_type', 'integration_type_display', 'api_key', 'api_secret',
            'webhook_url', 'settings', 'is_active', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
        }

class IntegrationLogSerializer(serializers.ModelSerializer):
    log_level_display = serializers.CharField(source='get_log_level_display', read_only=True)

    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'integration', 'log_level', 'log_level_display', 'message',
            'request_data', 'response_data', 'error_traceback', 'created_at'
        ]
        read_only_fields = ['created_at']

class WebhookEndpointSerializer(serializers.ModelSerializer):
    integration_name = serializers.CharField(source='integration.name', read_only=True)

    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'name', 'integration', 'integration_name', 'endpoint_url',
            'secret_key', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'secret_key': {'write_only': True},
        }

class WebhookRequestSerializer(serializers.ModelSerializer):
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)

    class Meta:
        model = WebhookRequest
        fields = [
            'id', 'endpoint', 'endpoint_name', 'method', 'headers',
            'body', 'status_code', 'response', 'created_at'
        ]
        read_only_fields = ['created_at'] 