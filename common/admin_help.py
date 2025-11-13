# -*- coding: utf-8 -*-
"""
Help System Admin
Destek talepleri için admin interface
"""

from django.contrib import admin
from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    """Destek Talepleri Admin"""
    
    list_display = [
        'id',
        'subject',
        'user',
        'priority_badge',
        'status_badge',
        'assigned_to',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'priority',
        'created_at',
    ]
    
    search_fields = [
        'subject',
        'message',
        'user__username',
        'user__email',
    ]
    
    readonly_fields = [
        'user',
        'ip_address',
        'user_agent',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Talep Bilgileri', {
            'fields': ('user', 'subject', 'message', 'priority')
        }),
        ('Durum', {
            'fields': ('status', 'assigned_to', 'resolution', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_in_progress', 'mark_resolved', 'mark_closed']
    
    def priority_badge(self, obj):
        """Öncelik badge"""
        badge_class = obj.get_priority_badge_class()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            badge_class,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Öncelik'
    
    def status_badge(self, obj):
        """Durum badge"""
        badge_class = obj.get_status_badge_class()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            badge_class,
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    @admin.action(description='İşleniyor olarak işaretle')
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} talep "İşleniyor" olarak işaretlendi.')
    
    @admin.action(description='Çözüldü olarak işaretle')
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} talep "Çözüldü" olarak işaretlendi.')
    
    @admin.action(description='Kapatıldı olarak işaretle')
    def mark_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} talep kapatıldı.')


# Format HTML için import
from django.utils.html import format_html

