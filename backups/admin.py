from django.contrib import admin
from .models import BackupConfig, BackupStorage, BackupRecord, BackupLog

@admin.register(BackupConfig)
class BackupConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'backup_type', 'storage_type', 'schedule', 'retention_days', 'is_active')
    list_filter = ('backup_type', 'storage_type', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'description', 'backup_type', 'storage_type')
        }),
        ('Zamanlama', {
            'fields': ('schedule', 'retention_days')
        }),
        ('Durum', {
            'fields': ('is_active',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BackupStorage)
class BackupStorageAdmin(admin.ModelAdmin):
    list_display = ('config', 'storage_path', 'is_encrypted')
    list_filter = ('is_encrypted',)
    search_fields = ('storage_path',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('config', 'storage_path')
        }),
        ('Güvenlik', {
            'fields': ('is_encrypted', 'credentials')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ('config', 'storage', 'status', 'size_bytes', 'started_at', 'completed_at')
    list_filter = ('status', 'config', 'storage')
    search_fields = ('backup_path', 'error_message')
    readonly_fields = ('started_at', 'completed_at', 'created_at', 'updated_at')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('config', 'storage', 'backup_path')
        }),
        ('Durum', {
            'fields': ('status', 'error_message')
        }),
        ('Boyut', {
            'fields': ('size_bytes', 'checksum')
        }),
        ('Zaman Bilgileri', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ('record', 'level', 'message', 'created_at')
    list_filter = ('level',)
    search_fields = ('message',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('record', 'level', 'message')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    ) 