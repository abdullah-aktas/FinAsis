from rest_framework import serializers
from .models import Permission, Role, UserRole, UserPermission
from django.contrib.auth import get_user_model

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    parent = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Role
        fields = "__all__"


class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True, 
        required=False
    )
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.active.all(),
        source='role',
        write_only=True,
        required=True
    )

    class Meta:
        model = UserRole
        fields = "__all__"


class UserPermissionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    permission = serializers.PrimaryKeyRelatedField(queryset=Permission.active.all())
    user_display = serializers.StringRelatedField(source="user", read_only=True)
    permission_display = PermissionSerializer(source="permission", read_only=True)

    class Meta:
        model = UserPermission
        fields = [
            "id",
            "user",
            "user_display",
            "permission",
            "permission_display",
            "is_active",
            "created_at",
            "updated_at",
        ]
