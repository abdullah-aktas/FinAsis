from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import (
    Role, Resource, ResourcePermission, UserRole,
    PermissionDelegation, AuditLog, TwoFactorAuth, IPWhitelist
)

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']
        read_only_fields = ['id']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ResourcePermissionSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)
    permission = PermissionSerializer(read_only=True)
    
    class Meta:
        model = ResourcePermission
        fields = ['id', 'resource', 'permission', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'is_primary', 'assigned_at', 'assigned_by', 'expires_at']
        read_only_fields = ['id', 'assigned_at']

class PermissionDelegationSerializer(serializers.ModelSerializer):
    delegator = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    delegatee = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    permission = PermissionSerializer(read_only=True)
    
    class Meta:
        model = PermissionDelegation
        fields = ['id', 'delegator', 'delegatee', 'permission', 'created_at', 'expires_at', 'is_active']
        read_only_fields = ['id', 'created_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'model', 'object_id', 'details', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    
    class Meta:
        model = TwoFactorAuth
        fields = ['id', 'user', 'is_enabled', 'last_used', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class IPWhitelistSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    
    class Meta:
        model = IPWhitelist
        fields = ['id', 'ip_address', 'description', 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at']

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