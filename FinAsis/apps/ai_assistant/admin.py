# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AIModel, UserInteraction, FinancialPrediction, AIFeedback, FinancialReport, AnomalyDetection, TrendAnalysis
from django.utils.html import format_html

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'version', 'accuracy', 'is_active', 'last_trained', 'created_at', 'show_params')
    list_filter = ('model_type', 'is_active', 'last_trained', 'created_at')
    search_fields = ('name', 'description', 'version')
    readonly_fields = ('created_at', 'updated_at', 'last_trained', 'show_params')
    fieldsets = (
        (None, {
            'fields': ('name', 'model_type', 'version', 'description')
        }),
        (_('Performans'), {
            'fields': ('accuracy', 'parameters', 'show_params', 'last_trained')
        }),
        (_('Durum'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    ordering = ('-created_at',)

    def show_params(self, obj):
        return format_html('<pre style="max-width:400px;white-space:pre-wrap;">{}</pre>', obj.parameters)
    show_params.short_description = 'Model Parametreleri'

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'created_at', 'content_short', 'ai_response_short')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__username', 'content', 'ai_response')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def content_short(self, obj):
        return (obj.content[:60] + '...') if len(obj.content) > 60 else obj.content
    content_short.short_description = 'İçerik'

    def ai_response_short(self, obj):
        return (obj.ai_response[:60] + '...') if len(obj.ai_response) > 60 else obj.ai_response
    ai_response_short.short_description = 'AI Yanıtı'

@admin.register(FinancialPrediction)
class FinancialPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'prediction_type', 'confidence', 'is_validated', 'created_at')
    list_filter = ('prediction_type', 'is_validated', 'created_at')
    search_fields = ('user__username', 'prediction_type', 'validation_notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'prediction_type', 'model_version')
        }),
        (_('Veri'), {
            'fields': ('input_data', 'output_data', 'confidence')
        }),
        (_('Doğrulama'), {
            'fields': ('is_validated', 'validation_notes')
        }),
        (_('Zaman Bilgisi'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_at', 'generated_by')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'model', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'model', 'rating')
        }),
        (_('Detaylar'), {
            'fields': ('comment', 'created_at')
        }),
    )

@admin.register(AnomalyDetection)
class AnomalyDetectionAdmin(admin.ModelAdmin):
    list_display = ('detected_by', 'detection_type', 'anomaly_score', 'is_resolved', 'created_at')
    list_filter = ('detection_type', 'is_resolved', 'created_at')
    search_fields = ('description',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(TrendAnalysis)
class TrendAnalysisAdmin(admin.ModelAdmin):
    list_display = ('analyzed_by', 'analysis_type', 'confidence_score', 'created_at')
    list_filter = ('analysis_type', 'created_at')
    search_fields = ('insights',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
