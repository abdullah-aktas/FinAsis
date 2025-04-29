# -*- coding: utf-8 -*-
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Özel izin sınıfı - nesnenin sahibi düzenleyebilir, diğerleri sadece okuyabilir.
    """
    def has_object_permission(self, request, view, obj):
        # Okuma izinleri herkese açık
        if request.method in permissions.SAFE_METHODS:
            return True

        # Yazma izinleri sadece nesnenin sahibine açık
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Özel izin sınıfı - sadece admin kullanıcılar düzenleyebilir, diğerleri sadece okuyabilir.
    """
    def has_permission(self, request, view):
        # Okuma izinleri herkese açık
        if request.method in permissions.SAFE_METHODS:
            return True

        # Yazma izinleri sadece admin kullanıcılara açık
        return request.user and request.user.is_staff

class IsOwner(permissions.BasePermission):
    """
    Özel izin sınıfı - sadece nesnenin sahibi erişebilir.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsPublicOrOwner(permissions.BasePermission):
    """
    Özel izin sınıfı - nesne public ise herkes okuyabilir, değilse sadece sahibi erişebilir.
    """
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        return obj.user == request.user 