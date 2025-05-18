# -*- coding: utf-8 -*-
from rest_framework import permissions
from django.utils.translation import gettext_lazy as _

class CanCreateDocument(permissions.BasePermission):
    """Belge oluşturma yetkisi"""
    message = _('Belge oluşturma yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('edocument.add_edocument') or \
               request.user.has_perm('edocument.add_edespatchadvice')

class CanUpdateDocument(permissions.BasePermission):
    """Belge güncelleme yetkisi"""
    message = _('Belge güncelleme yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Belge sahibi veya alıcı firma yetkilisi
        return obj.sender == request.user or \
               obj.receiver_vkn == request.user.company.vkn

class CanDeleteDocument(permissions.BasePermission):
    """Belge silme yetkisi"""
    message = _('Belge silme yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Sadece belge sahibi silebilir
        return obj.sender == request.user and obj.status == 'DRAFT'

class CanViewDocument(permissions.BasePermission):
    """Belge görüntüleme yetkisi"""
    message = _('Belge görüntüleme yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Belge sahibi veya alıcı firma yetkilisi
        return obj.sender == request.user or \
               obj.receiver_vkn == request.user.company.vkn

class CanSendDocument(permissions.BasePermission):
    """Belge gönderme yetkisi"""
    message = _('Belge gönderme yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Sadece belge sahibi gönderebilir
        return obj.sender == request.user and obj.status == 'DRAFT'

class CanCancelDocument(permissions.BasePermission):
    """Belge iptal yetkisi"""
    message = _('Belge iptal yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Sadece belge sahibi iptal edebilir
        return obj.sender == request.user and obj.status == 'SENT'

class CanAcceptDespatch(permissions.BasePermission):
    """İrsaliye kabul yetkisi"""
    message = _('İrsaliye kabul yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Sadece alıcı firma yetkilisi kabul edebilir
        return obj.receiver_vkn == request.user.company.vkn and \
               obj.status == 'SENT'

class CanRejectDespatch(permissions.BasePermission):
    """İrsaliye red yetkisi"""
    message = _('İrsaliye red yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Sadece alıcı firma yetkilisi reddedebilir
        return obj.receiver_vkn == request.user.company.vkn and \
               obj.status == 'SENT'

class CanPartiallyAcceptDespatch(permissions.BasePermission):
    """İrsaliye kısmi kabul yetkisi"""
    message = _('İrsaliye kısmi kabul yetkiniz bulunmamaktadır.')

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Sadece alıcı firma yetkilisi kısmi kabul edebilir
        return obj.receiver_vkn == request.user.company.vkn and \
               obj.status == 'SENT' 