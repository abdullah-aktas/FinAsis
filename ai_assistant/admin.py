# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AIModel, UserInteraction, FinancialPrediction, AIFeedback

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'version', 'accuracy', 'is_active', 'last_trained')
    list_filter = ('model_type', 'is_active', 'last_trained')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'model_type', 'version', 'description')
        }),
        (_('Performans'), {
            'fields': ('accuracy', 'parameters', 'last_trained')
        }),
        (_('Durum'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'feedback', 'processing_time', 'created_at')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__username', 'query', 'response')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'interaction_type', 'query', 'response')
        }),
        (_('Geri Bildirim'), {
            'fields': ('feedback', 'feedback_text', 'processing_time')
        }),
        (_('Zaman Bilgisi'), {
            'fields': ('created_at',)
        }),
    )

@admin.register(FinancialPrediction)
class FinancialPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'prediction_type', 'confidence', 'is_validated', 'created_at')
    list_filter = ('prediction_type', 'is_validated', 'created_at')
    search_fields = ('user__username', 'validation_notes')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'prediction_type', 'model_version')
        }),
        (_('Veri'), {
            'fields': ('input_data', 'output_data', 'confidence')
        }),
        (_('DoÄŸrulama'), {
            'fields': ('is_validated', 'validation_notes')
        }),
        (_('Zaman Bilgisi'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'model', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'model', 'rating')
        }),
        (_('Detaylar'), {
            'fields': ('comment', 'created_at')
        }),
    )
