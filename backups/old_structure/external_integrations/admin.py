# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    IntegrationProvider, IntegrationTemplate, Integration,
    IntegrationLog, WebhookEndpoint, WebhookRequest
)

@admin.register(IntegrationProvider)
class IntegrationProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_version', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(IntegrationTemplate)
class IntegrationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'provider', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'template', 'integration_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('integration_type', 'provider', 'template', 'is_active', 'created_at')
    search_fields = ('name', 'provider__name', 'template__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'provider', 'template', 'integration_type', 'is_active')
        }),
        (_('API Bilgileri'), {
            'fields': ('api_key', 'api_secret', 'webhook_url'),
            'classes': ('collapse',)
        }),
        (_('Ayarlar'), {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        (_('Meta Bilgiler'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ('integration', 'log_level', 'created_at')
    list_filter = ('log_level', 'integration', 'created_at')
    search_fields = ('message', 'integration__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'integration', 'is_active', 'created_at')
    list_filter = ('is_active', 'integration', 'created_at')
    search_fields = ('name', 'endpoint_url', 'integration__name')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(WebhookRequest)
class WebhookRequestAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'status_code', 'created_at')
    list_filter = ('method', 'status_code', 'endpoint', 'created_at')
    search_fields = ('endpoint__name', 'endpoint__integration__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('endpoint', 'method', 'status_code')
        }),
        (_('İstek Detayları'), {
            'fields': ('headers', 'body'),
            'classes': ('collapse',)
        }),
        (_('Yanıt Detayları'), {
            'fields': ('response',),
            'classes': ('collapse',)
        }),
        (_('Meta Bilgiler'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
