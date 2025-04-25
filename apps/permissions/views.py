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
    TwoFactorAuthSerializer, IPWhitelistSerializer, UserRoleSerializer,
    ResourcePermissionSerializer
)
from .permissions import IsAdminOrHasPermission
import pyotp
import qrcode
import io
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import PermissionForm, RoleForm

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

class ResourcePermissionViewSet(viewsets.ModelViewSet):
    queryset = ResourcePermission.objects.all()
    serializer_class = ResourcePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PermissionDelegationViewSet(viewsets.ModelViewSet):
    queryset = PermissionDelegation.objects.all()
    serializer_class = PermissionDelegationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(delegator=self.request.user)

class TwoFactorAuthViewSet(viewsets.ModelViewSet):
    queryset = TwoFactorAuth.objects.all()
    serializer_class = TwoFactorAuthSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class IPWhitelistViewSet(viewsets.ModelViewSet):
    queryset = IPWhitelist.objects.all()
    serializer_class = IPWhitelistSerializer
    permission_classes = [permissions.IsAuthenticated]

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

@login_required
@permission_required('permissions.view_permission')
def permission_list(request):
    """İzin listesi görünümü"""
    permissions = Permission.objects.all()
    
    # Arama filtresi
    search_query = request.GET.get('search', '')
    if search_query:
        permissions = permissions.filter(
            Q(name__icontains=search_query) |
            Q(codename__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(permissions, 10)
    page = request.GET.get('page')
    permissions = paginator.get_page(page)
    
    context = {
        'permissions': permissions,
    }
    return render(request, 'permissions/list.html', context)

@login_required
@permission_required('permissions.add_permission')
def permission_create(request):
    """Yeni izin oluşturma görünümü"""
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'İzin başarıyla oluşturuldu.')
            return redirect('permissions:list')
    else:
        form = PermissionForm()
    
    context = {
        'form': form,
    }
    return render(request, 'permissions/form.html', context)

@login_required
@permission_required('permissions.view_role')
def role_list(request):
    """Rol listesi görünümü"""
    roles = Role.objects.all()
    
    # Arama filtresi
    search_query = request.GET.get('search', '')
    if search_query:
        roles = roles.filter(name__icontains=search_query)
    
    # Sayfalama
    paginator = Paginator(roles, 10)
    page = request.GET.get('page')
    roles = paginator.get_page(page)
    
    context = {
        'roles': roles,
    }
    return render(request, 'permissions/roles.html', context)

@login_required
@permission_required('permissions.add_role')
def role_create(request):
    """Yeni rol oluşturma görünümü"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, 'Rol başarıyla oluşturuldu.')
            return redirect('permissions:roles')
    else:
        form = RoleForm()
    
    context = {
        'form': form,
    }
    return render(request, 'permissions/role_form.html', context)

@login_required
@permission_required('permissions.view_userrole')
def user_roles(request):
    """Kullanıcı rolleri görünümü"""
    user_roles = UserRole.objects.all()
    
    # Arama filtresi
    search_query = request.GET.get('search', '')
    if search_query:
        user_roles = user_roles.filter(
            Q(user__username__icontains=search_query) |
            Q(role__name__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(user_roles, 10)
    page = request.GET.get('page')
    user_roles = paginator.get_page(page)
    
    context = {
        'user_roles': user_roles,
    }
    return render(request, 'permissions/user_roles.html', context)

@login_required
@permission_required('permissions.add_userrole')
def assign_role(request):
    """Rol atama görünümü"""
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role_id = request.POST.get('role')
        
        user_role = UserRole.objects.create(
            user_id=user_id,
            role_id=role_id
        )
        messages.success(request, 'Rol başarıyla atandı.')
        return redirect('permissions:user_roles')
    
    context = {
        'users': User.objects.all(),
        'roles': Role.objects.all(),
    }
    return render(request, 'permissions/assign_role.html', context) 