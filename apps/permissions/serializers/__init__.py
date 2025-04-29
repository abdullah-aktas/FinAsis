# -*- coding: utf-8 -*-
"""
permissions uygulaması için serializers modülü
"""

from rest_framework import serializers
from ..models import (
    Role, Permission, UserRole, AuditLog, Resource,
    ResourcePermission, PermissionDelegation, TwoFactorAuth, IPWhitelist
)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class ResourcePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcePermission
        fields = '__all__'

class PermissionDelegationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionDelegation
        fields = '__all__'

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactorAuth
        fields = '__all__'

class IPWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPWhitelist
        fields = '__all__'

__all__ = [
    'RoleSerializer',
    'PermissionSerializer',
    'UserRoleSerializer',
    'AuditLogSerializer',
    'ResourceSerializer',
    'ResourcePermissionSerializer',
    'PermissionDelegationSerializer',
    'TwoFactorAuthSerializer',
    'IPWhitelistSerializer',
]

