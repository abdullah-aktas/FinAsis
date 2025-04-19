"""
Rol tabanlı izin sınıfları.
"""
from rest_framework import permissions
from apps.permissions import ROLE_PERMISSIONS_MAP


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