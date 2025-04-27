"""
Users Modülü - İzin Sınıfları
---------------------
Bu dosya, Users modülünün özel izin sınıflarını içerir.
"""

from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Sadece nesnenin sahibi veya admin kullanıcıların erişimine izin verir.
    """
    def has_object_permission(self, request, view, obj):
        # Admin kullanıcılar her zaman erişebilir
        if request.user and request.user.is_staff:
            return True
            
        # Nesnenin sahibi erişebilir
        return obj.user == request.user

class IsAdminUser(permissions.BasePermission):
    """
    Sadece admin kullanıcıların erişimine izin verir.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
        
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff 