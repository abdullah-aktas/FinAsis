# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Category, Document, DocumentVersion, DocumentLog

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'category', 'created_at')
    filter_horizontal = ('shared_users',)
    ordering = ('-created_at',)

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_by', 'created_at')
    search_fields = ('document__title',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(DocumentLog)
class DocumentLogAdmin(admin.ModelAdmin):
    list_display = ('document', 'action', 'user', 'created_at')
    search_fields = ('document__title', 'user__username')
    list_filter = ('action', 'created_at')
    ordering = ('-created_at',)
