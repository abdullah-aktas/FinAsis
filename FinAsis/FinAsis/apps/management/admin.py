from django.contrib import admin
from .models import ActionLog, Notification, HelpContent

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action', 'detail')
    list_filter = ('action', 'timestamp')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'created_at')

@admin.register(HelpContent)
class HelpContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'role', 'page_key', 'updated_at')
    search_fields = ('title', 'content', 'role', 'page_key')
    list_filter = ('role', 'updated_at') 