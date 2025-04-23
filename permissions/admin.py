"""
Admin panel registrations for permissions app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission
from django.utils.translation import gettext_lazy as _

from permissions.models import (
    Role, UserRole, Resource, ResourcePermission,
    PermissionDelegation, AuditLog, TwoFactorAuth, IPWhitelist
)


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
    list_display = ('name', 'code', 'role_type', 'is_active', 'created_at')
    list_filter = ('role_type', 'is_active')
    search_fields = ('name', 'code', 'description')
    filter_horizontal = ('permissions',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Admin olmayan kullanıcılar sadece kendi oluşturdukları rolleri görebilir
            return qs.filter(created_by=request.user)
        return qs


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Kullanıcı-Rol ilişkisi için admin paneli yapılandırması.
    """
    list_display = ('user', 'role', 'is_primary', 'assigned_at', 'expires_at')
    list_filter = ('is_primary', 'role')
    search_fields = ('user__username', 'role__name')
    readonly_fields = ('assigned_at',)
    ordering = ('-is_primary', '-assigned_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Admin olmayan kullanıcılar sadece kendi atadıkları rolleri görebilir
            return qs.filter(assigned_by=request.user)
        return qs


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)


@admin.register(ResourcePermission)
class ResourcePermissionAdmin(admin.ModelAdmin):
    list_display = ('resource', 'permission', 'created_at')
    list_filter = ('resource', 'permission')
    search_fields = ('resource__name', 'permission__name')
    readonly_fields = ('created_at',)
    ordering = ('resource', 'permission')


@admin.register(PermissionDelegation)
class PermissionDelegationAdmin(admin.ModelAdmin):
    list_display = ('delegator', 'delegatee', 'permission', 'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'permission')
    search_fields = ('delegator__username', 'delegatee__username', 'permission__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Admin olmayan kullanıcılar sadece kendi devrettikleri izinleri görebilir
            return qs.filter(delegator=request.user)
        return qs


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Denetim günlüğü için admin paneli yapılandırması.
    """
    list_display = ('user', 'action', 'model', 'object_id', 'created_at')
    list_filter = ('action', 'model', 'created_at')
    search_fields = ('user__username', 'model', 'object_id', 'details')
    readonly_fields = ('user', 'action', 'model', 'object_id', 'details', 'ip_address', 'user_agent', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_enabled', 'last_used', 'created_at')
    list_filter = ('is_enabled',)
    search_fields = ('user__username',)
    readonly_fields = ('secret', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.user == request.user:
            return True
        return request.user.is_superuser


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description', 'created_at', 'created_by')
    list_filter = ('created_at',)
    search_fields = ('ip_address', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Admin olmayan kullanıcılar sadece kendi ekledikleri IP'leri görebilir
            return qs.filter(created_by=request.user)
        return qs


# Kullanıcı admin panelini özelleştir
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Admin olmayan kullanıcılar sadece kendi oluşturdukları kullanıcıları görebilir
            return qs.filter(created_by=request.user)
        return qs


# Mevcut UserAdmin'i kaldır ve özelleştirilmiş olanı ekle
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 