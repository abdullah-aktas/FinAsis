# -*- coding: utf-8 -*-
"""
Rol tabanlı izin sınıfları.
"""
from rest_framework import permissions
from apps.permissions import ROLE_PERMISSIONS_MAP
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.conf import settings
import jwt
from datetime import datetime, timedelta
from functools import wraps
from django.http import JsonResponse
import logging
from .models import Role, UserRole, PermissionDelegation, IPWhitelist

logger = logging.getLogger(__name__)

class JWTAuthentication:
    @staticmethod
    def generate_token(user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = settings.RATE_LIMIT
        self.window = settings.RATE_LIMIT_WINDOW

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        key = f'rate_limit:{ip}'
        
        current = cache.get(key, 0)
        if current >= self.rate_limit:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': self.window
            }, status=429)
        
        cache.set(key, current + 1, self.window)
        return self.get_response(request)

class IPBasedAccessControl:
    def __init__(self, allowed_ips):
        self.allowed_ips = allowed_ips

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip not in self.allowed_ips:
            return JsonResponse({
                'error': 'Access denied',
                'message': 'Your IP address is not allowed'
            }, status=403)
        return None

class RBACPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Cache'den izinleri al
        cache_key = f'user_permissions:{request.user.id}'
        user_permissions = cache.get(cache_key)
        
        if user_permissions is None:
            # İzinleri veritabanından al ve cache'e kaydet
            user_permissions = self._get_user_permissions(request.user)
            cache.set(cache_key, user_permissions, 300)  # 5 dakika cache

        required_permission = f'{view.__class__.__name__}.{view.action}'
        return required_permission in user_permissions

    def _get_user_permissions(self, user):
        permissions = set()
        
        # Kullanıcının doğrudan izinleri
        permissions.update(user.user_permissions.values_list('codename', flat=True))
        
        # Grup izinleri
        for group in user.groups.all():
            permissions.update(group.permissions.values_list('codename', flat=True))
        
        return permissions

class ResourceBasedPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Kaynak sahibi kontrolü
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Özel izin kontrolü
        permission_name = f'{obj._meta.model_name}.{view.action}'
        return request.user.has_perm(permission_name)

class DynamicPermission:
    def __init__(self, permission_name):
        self.permission_name = permission_name

    def __call__(self, func):
        @wraps(func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(self.permission_name):
                return JsonResponse({
                    'error': 'Permission denied',
                    'message': f'Required permission: {self.permission_name}'
                }, status=403)
            return func(request, *args, **kwargs)
        return wrapped_view

class PermissionDelegation:
    @staticmethod
    def delegate_permission(user, permission, target_user, expires=None):
        if not user.has_perm('auth.delegate_permission'):
            return False

        delegation = {
            'from_user': user.id,
            'to_user': target_user.id,
            'permission': permission,
            'expires': expires.isoformat() if expires else None,
            'created_at': datetime.utcnow().isoformat()
        }

        # Delegasyonu cache'e kaydet
        cache_key = f'delegation:{target_user.id}:{permission}'
        cache.set(cache_key, delegation, 
                 (expires - datetime.utcnow()).total_seconds() if expires else None)
        
        logger.info(f'Permission delegated: {permission} from {user} to {target_user}')
        return True

    @staticmethod
    def revoke_delegation(user, permission, target_user):
        if not user.has_perm('auth.revoke_delegation'):
            return False

        cache_key = f'delegation:{target_user.id}:{permission}'
        cache.delete(cache_key)
        
        logger.info(f'Permission delegation revoked: {permission} from {user} to {target_user}')
        return True

class AuditLogging:
    @staticmethod
    def log_permission_change(user, action, target, details):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user': user.id,
            'action': action,
            'target': target,
            'details': details
        }
        
        # Log'u cache'e kaydet
        cache.lpush('audit_log', log_entry)
        # Son 1000 log'u tut
        cache.ltrim('audit_log', 0, 999)
        
        logger.info(f'Permission change logged: {action} by {user} on {target}')

class TwoFactorAuth:
    @staticmethod
    def generate_otp(user):
        # Basit bir OTP üretimi (gerçek uygulamada daha güvenli bir yöntem kullanılmalı)
        import random
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # OTP'yi cache'e kaydet
        cache_key = f'2fa_otp:{user.id}'
        cache.set(cache_key, otp, 300)  # 5 dakika geçerli
        
        return otp

    @staticmethod
    def verify_otp(user, otp):
        cache_key = f'2fa_otp:{user.id}'
        stored_otp = cache.get(cache_key)
        
        if stored_otp and stored_otp == otp:
            cache.delete(cache_key)
            return True
        return False

class IsAdmin(permissions.BasePermission):
    """
    Sadece admin rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için yönetici rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == 'admin'


class IsFinanceManager(permissions.BasePermission):
    """
    Finans sorumlusu rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için finans sorumlusu rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'finance_manager']
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'finance_manager']


class IsStockOperator(permissions.BasePermission):
    """
    Depo yetkilisi rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için depo yetkilisi rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'stock_operator']
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'stock_operator']


class IsAccountingStaff(permissions.BasePermission):
    """
    Muhasebe sorumlusu rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için muhasebe sorumlusu rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'accounting']
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'accounting']


class IsSalesStaff(permissions.BasePermission):
    """
    Satış sorumlusu rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için satış sorumlusu rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'sales']
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'sales']


class IsHRStaff(permissions.BasePermission):
    """
    İnsan kaynakları rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için insan kaynakları rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'hr']
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'hr']


class IsManager(permissions.BasePermission):
    """
    Genel müdür rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için genel müdür rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'manager']
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'manager']


class HasRolePermission(permissions.BasePermission):
    """
    Belirtilen rollere sahip kullanıcılara izin verir.
    
    Örnek Kullanım:
    
    class MyView(APIView):
        permission_classes = [HasRolePermission]
        required_roles = ['admin', 'finance_manager']
    """
    message = "Bu işlem için yeterli yetkiye sahip değilsiniz."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Admin her zaman erişebilir
        if request.user.is_superuser:
            return True
            
        # View'da tanımlanan roller
        required_roles = getattr(view, 'required_roles', [])
        
        # Rol kontrolü
        return request.user.role in required_roles
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde izin kontrolü
        if not request.user.is_authenticated:
            return False
            
        # Admin her zaman erişebilir
        if request.user.is_superuser:
            return True
            
        # View'da tanımlanan roller
        required_roles = getattr(view, 'required_roles', [])
        
        # Rol kontrolü
        return request.user.role in required_roles


class ModulePermission(permissions.BasePermission):
    """
    Modül bazlı yetkilendirme sınıfı.
    
    Örnek Kullanım:
    
    class InvoiceViewSet(viewsets.ModelViewSet):
        permission_classes = [ModulePermission]
        module_name = 'finance'
    """
    message = "Bu modül için yeterli yetkiye sahip değilsiniz."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Admin her zaman erişebilir
        if request.user.is_superuser:
            return True
            
        # View'da tanımlanan modül
        module_name = getattr(view, 'module_name', None)
        if not module_name:
            return False
            
        # Kullanıcının rolü
        role = request.user.role
        
        # Rol izin haritasını kontrol et
        role_perms = ROLE_PERMISSIONS_MAP.get(role, {})
        
        # 'all' modülü varsa erişim izni ver
        if 'all' in role_perms:
            # HTTP metodu ile ilgili izin kontrolü
            if request.method in permissions.SAFE_METHODS:
                return 'view' in role_perms['all']
            elif request.method == 'POST':
                return 'create' in role_perms['all']
            elif request.method in ['PUT', 'PATCH']:
                return 'update' in role_perms['all']
            elif request.method == 'DELETE':
                return 'delete' in role_perms['all']
        
        # Modül izinlerini kontrol et
        module_perms = role_perms.get(module_name, [])
        
        # HTTP metodu ile ilgili izin kontrolü
        if request.method in permissions.SAFE_METHODS:
            return 'view' in module_perms
        elif request.method == 'POST':
            return 'create' in module_perms
        elif request.method in ['PUT', 'PATCH']:
            return 'update' in module_perms
        elif request.method == 'DELETE':
            return 'delete' in module_perms
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde aynı izin kontrollerini uygula
        return self.has_permission(request, view)


class ActionBasedPermission(permissions.BasePermission):
    """
    ViewSet'in action'larına göre yetkilendirme yapan izin sınıfı.
    
    Örnek Kullanım:
    
    class ProductViewSet(viewsets.ModelViewSet):
        permission_classes = [ActionBasedPermission]
        action_permissions = {
            'list': ['admin', 'finance_manager', 'stock_operator'],
            'create': ['admin', 'stock_operator'],
            'retrieve': ['admin', 'finance_manager', 'stock_operator'],
            'update': ['admin', 'stock_operator'],
            'destroy': ['admin'],
        }
    """
    message = "Bu işlem için yeterli yetkiye sahip değilsiniz."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Admin her zaman erişebilir
        if request.user.is_superuser:
            return True
            
        # View'in action'ını belirle
        action = getattr(view, 'action', None)
        if not action:
            return False
            
        # Action için tanımlanan izinleri al
        action_permissions = getattr(view, 'action_permissions', {})
        allowed_roles = action_permissions.get(action, [])
        
        # Rol kontrolü
        return request.user.role in allowed_roles
    
    def has_object_permission(self, request, view, obj):
        # Nesne seviyesinde aynı izin kontrollerini uygula
        return self.has_permission(request, view)


class ReadOnly(permissions.BasePermission):
    """
    Sadece GET, HEAD veya OPTIONS isteklerine izin verir.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 