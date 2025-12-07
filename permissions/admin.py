from django.contrib import admin
from .models import Permission, Role, UserRole, UserPermission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "codename", "content_type", "is_active", "created_at")
    list_filter = ("is_active", "content_type")
    search_fields = ("name", "codename", "description")
    readonly_fields = ("django_permission",)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "parent", "is_active", "created_at")
    list_filter = ("is_active", "type")
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "is_active", "created_at")
    list_filter = ("is_active", "role")
    search_fields = ("user__username", "role__name")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "permission", "is_active", "created_at")
    list_filter = ("is_active", "permission")
    search_fields = ("user__username", "permission__codename")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)
