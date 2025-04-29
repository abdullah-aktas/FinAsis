# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import AnalyticsDashboard, DashboardWidget, AnalyticsReport, DataSource

@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'dashboard', 'widget_type', 'created_at')
    list_filter = ('widget_type', 'created_at')
    search_fields = ('title', 'data_source')
    date_hierarchy = 'created_at'

@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_by', 'is_scheduled', 'created_at')
    list_filter = ('report_type', 'is_scheduled', 'created_at')
    search_fields = ('title', 'description', 'query')
    date_hierarchy = 'created_at'

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'is_active', 'last_sync')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
