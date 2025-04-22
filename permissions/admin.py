"""
Admin panel registrations for permissions app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from permissions.models import Role, Permission, UserRole, AuditLog


class PermissionInline(admin.TabularInline):
    """
    Rol düzenleme sayfasında izinleri göstermek için inline.
    """
    model = Role.permissions.through
    extra = 0
    verbose_name = _("İzin")
    verbose_name_plural = _("İzinler")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    İzin modeli için admin paneli yapılandırması.
    """
    list_display = ('name', 'module', 'permission_type', 'codename')
    list_filter = ('module', 'permission_type')
    search_fields = ('name', 'codename', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('İzin Bilgileri'), {
            'fields': ('name', 'codename', 'description')
        }),
        (_('Modül ve İzin Türü'), {
            'fields': ('module', 'permission_type')
        }),
        (_('Zamanlama'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Rol modeli için admin paneli yapılandırması.
    """
    list_display = ('name', 'code', 'role_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'role_type')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('permissions',)
    fieldsets = (
        (_('Rol Bilgileri'), {
            'fields': ('name', 'code', 'description', 'is_active', 'role_type')
        }),
        (_('İzinler'), {
            'fields': ('permissions',)
        }),
        (_('Oluşturma Bilgileri'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Kullanıcı-Rol ilişkisi için admin paneli yapılandırması.
    """
    list_display = ('user', 'role', 'is_primary', 'assigned_at', 'assigned_by', 'expires_at')
    list_filter = ('is_primary', 'role')
    search_fields = ('user__username', 'user__email', 'role__name')
    readonly_fields = ('assigned_at',)
    raw_id_fields = ('user', 'assigned_by')
    fieldsets = (
        (_('Kullanıcı ve Rol'), {
            'fields': ('user', 'role', 'is_primary')
        }),
        (_('Atama Bilgileri'), {
            'fields': ('assigned_by', 'assigned_at', 'expires_at')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Denetim günlüğü için admin paneli yapılandırması.
    """
    list_display = ('user', 'action', 'model', 'object_id', 'ip_address', 'created_at')
    list_filter = ('action', 'model', 'created_at')
    search_fields = ('user__username', 'object_id', 'ip_address')
    readonly_fields = ('user', 'action', 'model', 'object_id', 'details', 'ip_address', 'user_agent', 'created_at')
    fieldsets = (
        (_('İşlem Bilgileri'), {
            'fields': ('user', 'action', 'model', 'object_id')
        }),
        (_('Detaylar'), {
            'fields': ('details',)
        }),
        (_('İstemci Bilgileri'), {
            'fields': ('ip_address', 'user_agent')
        }),
        (_('Zamanlama'), {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 