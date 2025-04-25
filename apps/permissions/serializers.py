from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import (
    Role, Resource, ResourcePermission, UserRole,
    PermissionDelegation, AuditLog, TwoFactorAuth, IPWhitelist
)

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class ResourcePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcePermission
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class PermissionDelegationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionDelegation
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactorAuth
        fields = '__all__'

class IPWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPWhitelist
        fields = '__all__'

class TwoFactorSetupSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)

class TwoFactorVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)

class CheckPermissionSerializer(serializers.Serializer):
    permission = serializers.CharField(max_length=100, required=True)
    resource = serializers.CharField(max_length=100, required=True)

class DelegatePermissionSerializer(serializers.Serializer):
    delegatee = serializers.CharField(max_length=150, required=True)
    permission = serializers.CharField(max_length=100, required=True)
    resource = serializers.CharField(max_length=100, required=True)
    expires_at = serializers.DateTimeField(required=False)

class RevokePermissionSerializer(serializers.Serializer):
    delegation_id = serializers.UUIDField(required=True) 