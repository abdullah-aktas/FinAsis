"""
Rol tabanlı izin sınıfları.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Sadece admin rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için yönetici rolü gereklidir."

    def has_permission(self, request, view):
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


class IsStockOperator(permissions.BasePermission):
    """
    Depo yetkilisi rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için depo yetkilisi rolü gereklidir."

    def has_permission(self, request, view):
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


class IsSalesStaff(permissions.BasePermission):
    """
    Satış sorumlusu rolündeki kullanıcılara izin verir.
    """
    message = "Bu işlem için satış sorumlusu rolü gereklidir."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'sales']


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


class ReadOnly(permissions.BasePermission):
    """
    Sadece GET, HEAD veya OPTIONS isteklerine izin verir.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 