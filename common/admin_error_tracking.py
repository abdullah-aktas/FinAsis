"""
Django Admin for Error Tracking
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .error_tracking import ErrorLog


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'severity_badge',
        'status_badge',
        'error_type',
        'error_message_short',
        'occurrence_badge',
        'user_info',
        'last_seen_relative',
        'admin_notified_icon',
    ]
    
    list_filter = [
        'severity',
        'status',
        'admin_notified',
        ('first_seen', admin.DateFieldListFilter),
        'error_type',
    ]
    
    search_fields = [
        'error_type',
        'error_message',
        'url',
        'user__email',
        'ip_address',
    ]
    
    readonly_fields = [
        'error_type',
        'error_message',
        'traceback_formatted',
        'request_info',
        'system_info',
        'first_seen',
        'last_seen',
        'occurrence_count',
        'admin_notified',
        'notification_sent_at',
    ]
    
    fieldsets = (
        ('Error Details', {
            'fields': (
                'severity',
                'status',
                'error_type',
                'error_message',
                'traceback_formatted',
            )
        }),
        ('Request Context', {
            'fields': (
                'url',
                'method',
                'user',
                'ip_address',
                'request_info',
            )
        }),
        ('System Info', {
            'fields': (
                'system_info',
            )
        }),
        ('Occurrence', {
            'fields': (
                'occurrence_count',
                'first_seen',
                'last_seen',
            )
        }),
        ('Notification', {
            'fields': (
                'admin_notified',
                'notification_sent_at',
            )
        }),
        ('Resolution', {
            'fields': (
                'resolved_by',
                'resolved_at',
                'resolution_notes',
            )
        }),
    )
    
    actions = [
        'mark_as_investigating',
        'mark_as_resolved',
        'mark_as_ignored',
        'resend_notification',
    ]
    
    def severity_badge(self, obj):
        colors = {
            'CRITICAL': '#dc2626',
            'ERROR': '#ef4444',
            'WARNING': '#f59e0b',
            'INFO': '#3b82f6',
            'DEBUG': '#6b7280',
        }
        color = colors.get(obj.severity, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.severity
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        colors = {
            'NEW': '#f59e0b',
            'INVESTIGATING': '#3b82f6',
            'RESOLVED': '#10b981',
            'IGNORED': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def error_message_short(self, obj):
        msg = obj.error_message[:100]
        if len(obj.error_message) > 100:
            msg += '...'
        return msg
    error_message_short.short_description = 'Message'
    
    def occurrence_badge(self, obj):
        if obj.occurrence_count > 10:
            color = '#dc2626'
        elif obj.occurrence_count > 5:
            color = '#f59e0b'
        else:
            color = '#10b981'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 50%; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.occurrence_count
        )
    occurrence_badge.short_description = 'Count'
    
    def user_info(self, obj):
        if obj.user:
            url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return 'Anonymous'
    user_info.short_description = 'User'
    
    def last_seen_relative(self, obj):
        diff = timezone.now() - obj.last_seen
        
        if diff.total_seconds() < 60:
            return format_html('<span style="color: #dc2626; font-weight: bold;">Just now</span>')
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return format_html('<span style="color: #f59e0b;">{} min ago</span>', minutes)
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return format_html('<span>{} hours ago</span>', hours)
        else:
            days = int(diff.total_seconds() / 86400)
            return f'{days} days ago'
    last_seen_relative.short_description = 'Last Seen'
    
    def admin_notified_icon(self, obj):
        if obj.admin_notified:
            return format_html('<span style="color: #10b981;">✓ Notified</span>')
        return format_html('<span style="color: #6b7280;">✗ Not notified</span>')
    admin_notified_icon.short_description = 'Notified'
    
    def traceback_formatted(self, obj):
        return format_html('<pre style="background: #f3f4f6; padding: 10px; border-radius: 5px;">{}</pre>', obj.traceback)
    traceback_formatted.short_description = 'Stack Trace'
    
    def request_info(self, obj):
        import json
        info = f"""
        <div style="font-family: monospace; font-size: 12px;">
            <strong>URL:</strong> {obj.url}<br>
            <strong>Method:</strong> {obj.method}<br>
            <strong>IP:</strong> {obj.ip_address}<br>
            <strong>User Agent:</strong> {obj.user_agent[:100]}<br>
            <br>
            <strong>Request Data:</strong>
            <pre style="background: #f3f4f6; padding: 10px; border-radius: 5px;">{json.dumps(obj.request_data, indent=2)}</pre>
        </div>
        """
        return format_html(info)
    request_info.short_description = 'Request Info'
    
    def system_info(self, obj):
        info = f"""
        <div style="font-family: monospace; font-size: 12px;">
            <strong>Server:</strong> {obj.server_name}<br>
            <strong>Python:</strong> {obj.python_version}<br>
            <strong>Django:</strong> {obj.django_version}<br>
        </div>
        """
        return format_html(info)
    system_info.short_description = 'System Info'
    
    # Actions
    
    def mark_as_investigating(self, request, queryset):
        count = queryset.update(status='INVESTIGATING')
        self.message_user(request, f'{count} error(s) marked as investigating.')
    mark_as_investigating.short_description = 'Mark as Investigating'
    
    def mark_as_resolved(self, request, queryset):
        count = queryset.update(
            status='RESOLVED',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{count} error(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark as Resolved'
    
    def mark_as_ignored(self, request, queryset):
        count = queryset.update(status='IGNORED')
        self.message_user(request, f'{count} error(s) marked as ignored.')
    mark_as_ignored.short_description = 'Mark as Ignored'
    
    def resend_notification(self, request, queryset):
        from .error_tracking import error_tracker
        for error_log in queryset:
            error_tracker._send_notifications(error_log)
        self.message_user(request, f'Notifications resent for {queryset.count()} error(s).')
    resend_notification.short_description = 'Resend Notification'

