"""
Özel izin sınıfları.
Bu modül, proje genelinde kullanılacak özel izin sınıflarını içerir.
"""

from rest_framework import permissions
from .exceptions import AuthorizationError

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Nesnenin sahibi veya salt okunur izinleri.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Yönetici veya salt okunur izinleri.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsSuperUser(permissions.BasePermission):
    """
    Süper kullanıcı izinleri.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class HasAPIAccess(permissions.BasePermission):
    """
    API erişim izinleri.
    """
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('api.access_api')

class HasModulePermission(permissions.BasePermission):
    """
    Modül bazlı izinler.
    """
    def __init__(self, module_name):
        self.module_name = module_name

    def has_permission(self, request, view):
        if not request.user:
            return False
        
        permission_name = f'{self.module_name}.access'
        return request.user.has_perm(permission_name)

class HasObjectPermission(permissions.BasePermission):
    """
    Nesne bazlı izinler.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False
        
        # Nesne izinlerini kontrol et
        if hasattr(obj, 'check_permission'):
            return obj.check_permission(request.user)
        
        # Varsayılan olarak sahiplik kontrolü
        return obj.user == request.user

class CustomPermissionMixin:
    """
    Özel izin karışımı.
    """
    def check_permissions(self, request):
        """
        İzinleri kontrol eden metod.
        """
        try:
            super().check_permissions(request)
        except AuthorizationError as e:
            # Özel hata işleme
            self.permission_denied(
                request,
                message=e.message,
                code=e.code
            )

    def get_permissions(self):
        """
        İzin sınıflarını döndüren metod.
        """
        return [permission() for permission in self.permission_classes]

class RoleBasedPermission(permissions.BasePermission):
    """
    Rol bazlı izinler.
    """
    def __init__(self, roles):
        self.roles = roles

    def has_permission(self, request, view):
        if not request.user:
            return False
        
        return request.user.role in self.roles

class TimeBasedPermission(permissions.BasePermission):
    """
    Zaman bazlı izinler.
    """
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def has_permission(self, request, view):
        from datetime import datetime, time
        current_time = datetime.now().time()
        
        return self.start_time <= current_time <= self.end_time 