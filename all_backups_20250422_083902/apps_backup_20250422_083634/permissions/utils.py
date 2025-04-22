"""
Rol tabanlı izin kontrolü için yardımcı fonksiyonlar.
"""
from django.http import Http404
from django.core.exceptions import PermissionDenied

from apps.permissions import ROLE_PERMISSIONS_MAP, MODULE_DEPENDENCIES


def check_user_role(user, required_roles):
    """
    Kullanıcının belirtilen rollerden birine sahip olup olmadığını kontrol eder.
    
    Parameters:
    -----------
    user : User
        Kontrol edilecek kullanıcı.
    required_roles : str or list
        Gerekli rol veya roller.
    
    Returns:
    --------
    bool
        Kullanıcının belirtilen rollerden birine sahip olup olmadığı.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    
    # required_roles bir string ise listeye çevir
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    # Kullanıcının has_perm_role metodunu kullan
    if hasattr(user, 'has_perm_role'):
        return user.has_perm_role(required_roles)
    
    # Veya doğrudan role alanını kontrol et
    return user.role in required_roles


def check_module_permission(user, module, permission_type='view', check_dependencies=True):
    """
    Kullanıcının belirli bir modül için belirli bir izne sahip olup olmadığını kontrol eder.
    
    Parameters:
    -----------
    user : User
        Kontrol edilecek kullanıcı.
    module : str
        İzin kontrolü yapılacak modül adı.
    permission_type : str, default 'view'
        İzin türü ('create', 'view', 'update', 'delete').
    check_dependencies : bool, default True
        Modül bağımlılıklarını kontrol edip etmeme.
    
    Returns:
    --------
    bool
        Kullanıcının belirtilen modül ve izin türü için yetkisi olup olmadığı.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    
    # Kullanıcının rolü
    role = user.role
    
    # Rol izin haritasını kontrol et
    role_perms = ROLE_PERMISSIONS_MAP.get(role, {})
    
    # 'all' modülü varsa ve bu izin türünü içeriyorsa izin ver
    if 'all' in role_perms and permission_type in role_perms['all']:
        return True
    
    # Ana modülü kontrol et
    module_perms = role_perms.get(module, [])
    has_permission = permission_type in module_perms
    
    # Eğer ana modül izni yoksa ve bağımlılıkları kontrol etmek isteniyorsa
    if not has_permission and check_dependencies:
        # Modülün bağımlı olduğu diğer modülleri kontrol et
        dependencies = MODULE_DEPENDENCIES.get(module, [])
        for dep_module in dependencies:
            dep_perms = role_perms.get(dep_module, [])
            if permission_type in dep_perms:
                has_permission = True
                break
    
    return has_permission


def get_user_permissions(user):
    """
    Kullanıcının tüm izinlerini döndürür.
    
    Parameters:
    -----------
    user : User
        İzinleri alınacak kullanıcı.
    
    Returns:
    --------
    dict
        Kullanıcının tüm izinleri.
    """
    if not user.is_authenticated:
        return {}
    
    # Süper kullanıcılar için tüm izinleri döndür
    if user.is_superuser:
        all_modules = set()
        all_permissions = {'create', 'view', 'update', 'delete'}
        
        # Tüm modülleri topla
        for role_perms in ROLE_PERMISSIONS_MAP.values():
            for module in role_perms:
                if module != 'all':
                    all_modules.add(module)
        
        # Tüm modüller için tüm izinleri ver
        return {'all': list(all_permissions), **{module: list(all_permissions) for module in all_modules}}
    
    # Normal kullanıcılar için rol bazlı izinleri döndür
    return ROLE_PERMISSIONS_MAP.get(user.role, {})


def assert_module_permission(user, module, permission_type='view', check_dependencies=True,
                             error_message=None, raise_exception=True):
    """
    Kullanıcının belirli bir modül için izni olup olmadığını kontrol eder 
    ve yoksa istisna fırlatır.
    
    Parameters:
    -----------
    user : User
        Kontrol edilecek kullanıcı.
    module : str
        İzin kontrolü yapılacak modül adı.
    permission_type : str, default 'view'
        İzin türü ('create', 'view', 'update', 'delete').
    check_dependencies : bool, default True
        Modül bağımlılıklarını kontrol edip etmeme.
    error_message : str, optional
        İzin yoksa gösterilecek hata mesajı.
    raise_exception : bool, default True
        İzin yoksa istisna fırlatıp fırlatmayacağı.
    
    Returns:
    --------
    bool
        Kullanıcının izni olup olmadığı. raise_exception=True ise ve izin yoksa 
        istisna fırlatılır.
    
    Raises:
    -------
    PermissionDenied
        Kullanıcının izni yoksa ve raise_exception=True ise.
    """
    has_permission = check_module_permission(
        user, module, permission_type, check_dependencies
    )
    
    if not has_permission and raise_exception:
        message = error_message or f"Bu modül için {permission_type} izniniz yok: {module}"
        raise PermissionDenied(message)
    
    return has_permission


def filter_by_permission(queryset, user, module, permission_type='view'):
    """
    Kullanıcının izinlerine göre queryset'i filtreler. İzni yoksa boş queryset döndürür.
    
    Parameters:
    -----------
    queryset : QuerySet
        Filtrelenecek queryset.
    user : User
        İzinleri kontrol edilecek kullanıcı.
    module : str
        İzin kontrolü yapılacak modül adı.
    permission_type : str, default 'view'
        İzin türü ('create', 'view', 'update', 'delete').
    
    Returns:
    --------
    QuerySet
        Filtrelenmiş queryset. Kullanıcının izni yoksa boş queryset.
    """
    if not check_module_permission(user, module, permission_type):
        return queryset.none()
    
    return queryset 