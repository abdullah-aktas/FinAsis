"""
Rol ve izin kontrolleri için kullanılabilecek decorator fonksiyonları.
"""
import functools
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs
from .utils import (
    has_permission, is_ip_whitelisted, verify_2fa,
    get_user_permissions, get_user_roles
)
from .apps import get_setting
import logging

from apps.permissions import ROLE_PERMISSIONS_MAP, MODULE_DEPENDENCIES

logger = logging.getLogger(__name__)

def check_role(required_roles, redirect_to=None, message=None):
    """
    Kullanıcının belirtilen rollerden birine sahip olup olmadığını kontrol eden decorator.
    
    Parameters:
    -----------
    required_roles : str or list
        Gerekli rol veya roller.
    redirect_to : str, optional
        Erişim reddedildiğinde yönlendirilecek URL. Belirtilmezse, 403 hata sayfası döndürülür.
    message : str, optional
        Erişim reddedildiğinde gösterilecek hata mesajı.
    
    Returns:
    --------
    function
        Decorated view function.
    
    Examples:
    ---------
    @check_role('admin')
    def admin_view(request):
        ...
    
    @check_role(['admin', 'finance_manager'], redirect_to='home', message='Bu sayfaya erişim izniniz yok.')
    def finance_view(request):
        ...
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def check_user_role(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        
        # Kullanıcının has_perm_role metodunu kullan
        if hasattr(user, 'has_perm_role'):
            return user.has_perm_role(required_roles)
        
        # Veya doğrudan role alanını kontrol et
        return user.role in required_roles
    
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if check_user_role(request.user):
                return view_func(request, *args, **kwargs)
            
            error_message = message or f"Bu sayfaya erişim için gerekli yetkiye sahip değilsiniz."
            
            # AJAX isteği ise JSON yanıtı döndür
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_message}, status=403)
            
            # Yönlendirme URL'i belirtilmişse yönlendir
            if redirect_to:
                messages.error(request, error_message)
                return redirect(redirect_to)
            
            # Aksi takdirde 403 hatası döndür
            return HttpResponseForbidden(error_message)
        
        return _wrapped_view
    
    return decorator


def check_permission(module, permission_type, redirect_to=None, message=None):
    """
    Kullanıcının belirli bir modül üzerinde belirli bir eylem izni olup olmadığını 
    kontrol eden decorator.
    
    Parameters:
    -----------
    module : str
        İzin kontrolü yapılacak modül adı (örn. 'accounting', 'finance', 'stock').
    permission_type : str
        İzin türü ('create', 'view', 'update', 'delete').
    redirect_to : str, optional
        Erişim reddedildiğinde yönlendirilecek URL.
    message : str, optional
        Erişim reddedildiğinde gösterilecek hata mesajı.
    
    Returns:
    --------
    function
        Decorated view function.
    
    Examples:
    ---------
    @check_permission('finance', 'create')
    def create_invoice(request):
        ...
    """
    def check_user_permission(user):
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
        
        # Belirli modül için izinleri kontrol et
        module_perms = role_perms.get(module, [])
        return permission_type in module_perms
    
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if check_user_permission(request.user):
                return view_func(request, *args, **kwargs)
            
            error_message = message or f"Bu işlemi yapmak için gerekli yetkiye sahip değilsiniz."
            
            # AJAX isteği ise JSON yanıtı döndür
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_message}, status=403)
            
            # Yönlendirme URL'i belirtilmişse yönlendir
            if redirect_to:
                messages.error(request, error_message)
                return redirect(redirect_to)
            
            # Aksi takdirde 403 hatası döndür
            return HttpResponseForbidden(error_message)
        
        return _wrapped_view
    
    return decorator


def check_module_permission(module, permission_type='view', check_dependencies=True, redirect_to=None, message=None):
    """
    Belirli bir modül için izin kontrolü yapar, isteğe bağlı olarak 
    modül bağımlılıklarını da kontrol eder.
    
    Parameters:
    -----------
    module : str
        İzin kontrolü yapılacak modül adı.
    permission_type : str, default 'view'
        İzin türü.
    check_dependencies : bool, default True
        Modül bağımlılıklarını kontrol edip etmeme.
    redirect_to : str, optional
        Erişim reddedildiğinde yönlendirilecek URL.
    message : str, optional
        Erişim reddedildiğinde gösterilecek hata mesajı.
    
    Returns:
    --------
    function
        Decorated view function.
    
    Examples:
    ---------
    @check_module_permission('reports')
    def financial_report_view(request):
        ...
    """
    def check_user_module_permission(user):
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
    
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if check_user_module_permission(request.user):
                return view_func(request, *args, **kwargs)
            
            error_message = message or f"Bu modülü kullanmak için gerekli yetkiye sahip değilsiniz."
            
            # AJAX isteği ise JSON yanıtı döndür
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_message}, status=403)
            
            # Yönlendirme URL'i belirtilmişse yönlendir
            if redirect_to:
                messages.error(request, error_message)
                return redirect(redirect_to)
            
            # Aksi takdirde 403 hatası döndür
            return HttpResponseForbidden(error_message)
        
        return _wrapped_view
    
    return decorator

def require_permission(permission_codename):
    """
    Belirli bir izne sahip olmayı gerektiren dekoratör
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Bu işlem için giriş yapmanız gerekiyor.")
            
            if not has_permission(request.user, permission_codename):
                logger.warning(f"İzin reddedildi: {request.user.username} - {permission_codename}")
                raise PermissionDenied("Bu işlem için yetkiniz bulunmuyor.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_role(role_codes):
    """
    Belirli bir role sahip olmayı gerektiren dekoratör
    """
    if isinstance(role_codes, str):
        role_codes = [role_codes]
    
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Bu işlem için giriş yapmanız gerekiyor.")
            
            user_roles = get_user_roles(request.user)
            if not any(role.code in role_codes for role in user_roles):
                logger.warning(f"Rol reddedildi: {request.user.username} - {role_codes}")
                raise PermissionDenied("Bu işlem için gerekli role sahip değilsiniz.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_ip_whitelist(view_func):
    """
    IP beyaz listesi kontrolü yapan dekoratör
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not get_setting('IP_WHITELIST_ENABLED'):
            return view_func(request, *args, **kwargs)
        
        client_ip = request.META.get('REMOTE_ADDR')
        if not is_ip_whitelisted(client_ip):
            logger.warning(f"IP erişimi reddedildi: {client_ip}")
            raise PermissionDenied("Bu IP adresinden erişim izniniz bulunmuyor.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def require_2fa(view_func):
    """
    İki faktörlü kimlik doğrulama gerektiren dekoratör
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not get_setting('TWO_FACTOR_ENABLED'):
            return view_func(request, *args, **kwargs)
        
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Bu işlem için giriş yapmanız gerekiyor.")
        
        if not verify_2fa(request.user, request.session.get('2fa_verified')):
            logger.warning(f"2FA doğrulaması başarısız: {request.user.username}")
            raise PermissionDenied("İki faktörlü kimlik doğrulama gerekiyor.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def audit_log(action, model=None):
    """
    Denetim kaydı oluşturan dekoratör
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            from .models import AuditLog
            
            response = view_func(request, *args, **kwargs)
            
            if request.user.is_authenticated and get_setting('AUDIT_LOG_ENABLED'):
                try:
                    object_id = kwargs.get('pk') or kwargs.get('id')
                    details = f"{action} işlemi gerçekleştirildi"
                    
                    if model:
                        details += f" - Model: {model}"
                    if object_id:
                        details += f" - ID: {object_id}"
                    
                    AuditLog.objects.create(
                        user=request.user,
                        action=action,
                        model=model,
                        object_id=object_id,
                        details=details
                    )
                except Exception as e:
                    logger.error(f"Denetim kaydı oluşturulamadı: {str(e)}")
            
            return response
        return _wrapped_view
    return decorator

def cache_permissions(timeout=None):
    """
    İzin sonuçlarını önbelleğe alan dekoratör
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            cache_timeout = timeout or get_setting('CACHE_TIMEOUT')
            permissions = get_user_permissions(request.user)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 