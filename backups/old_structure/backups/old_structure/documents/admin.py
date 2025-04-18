from django.contrib import admin
from .models import Document, DocumentProcessingLog

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'status', 'created_at')
    list_filter = ('document_type', 'status', 'created_at')
    search_fields = ('title', 'notes')
    readonly_fields = ('extracted_data',)
    ordering = ('-created_at',)

@admin.register(DocumentProcessingLog)
class DocumentProcessingLogAdmin(admin.ModelAdmin):
    list_display = ('document', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('document__title', 'message', 'error')
    readonly_fields = ('document', 'status', 'message', 'error')
    ordering = ('-created_at',)
