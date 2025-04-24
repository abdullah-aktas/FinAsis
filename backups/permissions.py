from rest_framework import permissions

class IsBackupAdmin(permissions.BasePermission):
    """
    Yedekleme yöneticisi izinleri.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsBackupOwner(permissions.BasePermission):
    """
    Yedekleme sahibi izinleri.
    """
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or obj.created_by == request.user
        )

class CanManageBackup(permissions.BasePermission):
    """
    Yedekleme yönetimi izinleri.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.has_perm('backups.manage_backup')
        )

class CanViewBackup(permissions.BasePermission):
    """
    Yedekleme görüntüleme izinleri.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.has_perm('backups.view_backup')
        )

class CanRestoreBackup(permissions.BasePermission):
    """
    Yedekten geri yükleme izinleri.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.has_perm('backups.restore_backup')
        ) 