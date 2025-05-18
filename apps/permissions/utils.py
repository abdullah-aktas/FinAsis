# -*- coding: utf-8 -*-
"""
Rol tabanlı izin kontrolü için yardımcı fonksiyonlar.
"""
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Role, UserRole, PermissionDelegation, IPWhitelist, TwoFactorAuth
from .apps import get_setting
import logging
import ipaddress
import pyotp
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

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
    Kullanıcının tüm izinlerini döndürür (roller, gruplar ve devredilen izinler dahil)
    """
    cache_key = f'user_permissions:{user.id}'
    permissions = cache.get(cache_key)
    
    if permissions is None:
        # Rol bazlı izinler
        role_permissions = Permission.objects.filter(
            role__userrole__user=user,
            role__userrole__is_active=True
        )
        
        # Grup bazlı izinler
        group_permissions = Permission.objects.filter(
            group__user=user
        )
        
        # Devredilen izinler
        delegated_permissions = Permission.objects.filter(
            permissiondelegation__delegatee=user,
            permissiondelegation__is_active=True,
            permissiondelegation__expires_at__gt=timezone.now()
        )
        
        # Tüm izinleri birleştir
        permissions = (role_permissions | group_permissions | delegated_permissions).distinct()
        
        # Cache'e kaydet
        cache.set(cache_key, permissions, get_setting('CACHE_TIMEOUT'))
    
    return permissions


def has_permission(user, permission_codename):
    """
    Kullanıcının belirli bir izne sahip olup olmadığını kontrol eder
    """
    return get_user_permissions(user).filter(codename=permission_codename).exists()


def get_user_roles(user):
    """
    Kullanıcının aktif rollerini döndürür
    """
    cache_key = f'user_roles:{user.id}'
    roles = cache.get(cache_key)
    
    if roles is None:
        roles = Role.objects.filter(
            userrole__user=user,
            userrole__is_active=True
        ).distinct()
        cache.set(cache_key, roles, get_setting('CACHE_TIMEOUT'))
    
    return roles


def is_ip_whitelisted(ip_address):
    """
    IP adresinin beyaz listede olup olmadığını kontrol eder
    """
    if not get_setting('IP_WHITELIST_ENABLED'):
        return True
    
    cache_key = f'ip_whitelist:{ip_address}'
    is_whitelisted = cache.get(cache_key)
    
    if is_whitelisted is None:
        try:
            ip = ipaddress.ip_address(ip_address)
            is_whitelisted = IPWhitelist.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).exists()
            cache.set(cache_key, is_whitelisted, get_setting('CACHE_TIMEOUT'))
        except ValueError:
            is_whitelisted = False
    
    return is_whitelisted


def setup_2fa(user):
    """
    İki faktörlü kimlik doğrulama için gerekli ayarları yapar
    """
    if not get_setting('TWO_FACTOR_ENABLED'):
        return None
    
    # Mevcut 2FA ayarlarını kontrol et
    existing_2fa = TwoFactorAuth.objects.filter(user=user).first()
    if existing_2fa and existing_2fa.is_active:
        return existing_2fa
    
    # Yeni 2FA ayarları oluştur
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # QR kod oluştur
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp.provisioning_uri(user.email, issuer_name=get_setting('APP_NAME')))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    # 2FA kaydını oluştur
    two_factor = TwoFactorAuth.objects.create(
        user=user,
        secret=secret,
        is_active=False
    )
    
    return {
        'secret': secret,
        'qr_code': qr_code,
        'two_factor': two_factor
    }


def verify_2fa(user, code):
    """
    İki faktörlü kimlik doğrulama kodunu doğrular
    """
    two_factor = TwoFactorAuth.objects.filter(user=user, is_active=True).first()
    if not two_factor:
        return False
    
    totp = pyotp.TOTP(two_factor.secret)
    return totp.verify(code)


def delegate_permission(delegator, delegatee, permission, expires_at=None):
    """
    İzin devri oluşturur
    """
    if not get_setting('PERMISSION_DELEGATION_ENABLED'):
        return None
    
    # Devir yetkisini kontrol et
    if not has_permission(delegator, 'permissions.delegate_permission'):
        logger.warning(f"İzin devri başarısız: {delegator.username} yetkisiz")
        return None
    
    # İzin devrini oluştur
    delegation = PermissionDelegation.objects.create(
        delegator=delegator,
        delegatee=delegatee,
        permission=permission,
        expires_at=expires_at
    )
    
    # Cache'i temizle
    cache.delete_pattern(f'user_permissions:{delegatee.id}:*')
    
    logger.info(f"İzin devri oluşturuldu: {delegator.username} -> {delegatee.username}")
    return delegation


def revoke_permission(delegation_id):
    """
    İzin devrini iptal eder
    """
    try:
        delegation = PermissionDelegation.objects.get(id=delegation_id)
        delegation.is_active = False
        delegation.save()
        
        # Cache'i temizle
        cache.delete_pattern(f'user_permissions:{delegation.delegatee.id}:*')
        
        logger.info(f"İzin devri iptal edildi: {delegation.delegator.username} -> {delegation.delegatee.username}")
        return True
    except PermissionDelegation.DoesNotExist:
        logger.error(f"İzin devri bulunamadı: {delegation_id}")
        return False


def check_permission_expiry():
    """
    Süresi dolmuş izin devirlerini kontrol eder ve devre dışı bırakır
    """
    expired_delegations = PermissionDelegation.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now()
    )
    
    for delegation in expired_delegations:
        delegation.is_active = False
        delegation.save()
        
        # Cache'i temizle
        cache.delete_pattern(f'user_permissions:{delegation.delegatee.id}:*')
        
        logger.info(f"İzin devri süresi doldu: {delegation.delegator.username} -> {delegation.delegatee.username}")


def get_audit_logs(user=None, action=None, model=None, start_date=None, end_date=None):
    """
    Denetim kayıtlarını filtreler ve döndürür
    """
    from .models import AuditLog
    
    queryset = AuditLog.objects.all()
    
    if user:
        queryset = queryset.filter(user=user)
    if action:
        queryset = queryset.filter(action=action)
    if model:
        queryset = queryset.filter(model=model)
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    
    return queryset.order_by('-created_at')


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