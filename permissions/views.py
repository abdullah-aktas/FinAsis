from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.core.cache import cache
from .models import (
    Role, Resource, ResourcePermission, UserRole,
    PermissionDelegation, AuditLog, TwoFactorAuth, IPWhitelist
)
from .serializers import (
    RoleSerializer, ResourceSerializer, PermissionSerializer,
    PermissionDelegationSerializer, AuditLogSerializer,
    TwoFactorAuthSerializer, IPWhitelistSerializer
)
from .permissions import IsAdminOrHasPermission
import pyotp
import qrcode
import io
from django.conf import settings

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrHasPermission]

    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete_pattern('role:*')
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE',
            model='Role',
            object_id=instance.id,
            details=f'Created role: {instance.name}'
        )

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminOrHasPermission]

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminOrHasPermission]

class PermissionDelegationViewSet(viewsets.ModelViewSet):
    queryset = PermissionDelegation.objects.all()
    serializer_class = PermissionDelegationSerializer
    permission_classes = [IsAdminOrHasPermission]

    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete_pattern('delegation:*')
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE',
            model='PermissionDelegation',
            object_id=instance.id,
            details=f'Delegated permission from {instance.delegator} to {instance.delegatee}'
        )

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrHasPermission]

class IPWhitelistViewSet(viewsets.ModelViewSet):
    queryset = IPWhitelist.objects.all()
    serializer_class = IPWhitelistSerializer
    permission_classes = [IsAdminOrHasPermission]

    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete_pattern('ip_whitelist:*')
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE',
            model='IPWhitelist',
            object_id=instance.id,
            details=f'Added IP to whitelist: {instance.ip_address}'
        )

class TwoFactorSetupView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user = request.user
        if TwoFactorAuth.objects.filter(user=user).exists():
            return Response(
                {'error': '2FA already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            user.email,
            issuer_name=settings.SITE_NAME
        )

        # QR kod oluştur
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # QR kodu byte dizisine dönüştür
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = buffer.getvalue()

        # Geçici olarak secret'ı kaydet
        TwoFactorAuth.objects.create(
            user=user,
            secret=secret,
            is_enabled=False
        )

        return Response({
            'secret': secret,
            'qr_code': qr_code,
            'message': 'Please scan the QR code with your authenticator app'
        })

class TwoFactorVerifyView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user = request.user
        code = request.data.get('code')
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            totp = pyotp.TOTP(two_factor.secret)
            
            if totp.verify(code):
                two_factor.is_enabled = True
                two_factor.save()
                
                AuditLog.objects.create(
                    user=user,
                    action='UPDATE',
                    model='TwoFactorAuth',
                    object_id=two_factor.id,
                    details='2FA enabled successfully'
                )
                
                return Response({'message': '2FA enabled successfully'})
            else:
                return Response(
                    {'error': 'Invalid code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {'error': '2FA not set up'},
                status=status.HTTP_400_BAD_REQUEST
            )

class TwoFactorDisableView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user = request.user
        code = request.data.get('code')
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            totp = pyotp.TOTP(two_factor.secret)
            
            if totp.verify(code):
                two_factor.delete()
                
                AuditLog.objects.create(
                    user=user,
                    action='DELETE',
                    model='TwoFactorAuth',
                    object_id=two_factor.id,
                    details='2FA disabled successfully'
                )
                
                return Response({'message': '2FA disabled successfully'})
            else:
                return Response(
                    {'error': 'Invalid code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {'error': '2FA not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

class CheckPermissionView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        permission = request.data.get('permission')
        resource = request.data.get('resource')
        
        has_permission = request.user.has_perm(permission)
        
        return Response({
            'has_permission': has_permission,
            'permission': permission,
            'resource': resource
        })

class UserPermissionsView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        permissions = user.get_all_permissions()
        roles = UserRole.objects.filter(user=user)
        
        return Response({
            'permissions': list(permissions),
            'roles': [role.role.name for role in roles]
        })

class DelegatePermissionView(viewsets.ViewSet):
    permission_classes = [IsAdminOrHasPermission]

    def create(self, request):
        delegatee = request.data.get('delegatee')
        permission = request.data.get('permission')
        resource = request.data.get('resource')
        expires_at = request.data.get('expires_at')
        
        delegation = PermissionDelegation.objects.create(
            delegator=request.user,
            delegatee=delegatee,
            permission=permission,
            resource=resource,
            expires_at=expires_at
        )
        
        return Response({
            'message': 'Permission delegated successfully',
            'delegation_id': delegation.id
        })

class RevokePermissionView(viewsets.ViewSet):
    permission_classes = [IsAdminOrHasPermission]

    def create(self, request):
        delegation_id = request.data.get('delegation_id')
        
        try:
            delegation = PermissionDelegation.objects.get(id=delegation_id)
            delegation.delete()
            
            return Response({
                'message': 'Permission revoked successfully'
            })
        except PermissionDelegation.DoesNotExist:
            return Response(
                {'error': 'Delegation not found'},
                status=status.HTTP_404_NOT_FOUND
            ) 