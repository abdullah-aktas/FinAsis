from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.contrib.auth.decorators import permission_required as django_permission_required

def permission_required(perm, login_url=None, raise_exception=True):
    """
    Özel izin kontrolü decorator'ı
    """
    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        
        if user.has_perms(perms):
            return True
        
        if raise_exception:
            raise PermissionDenied
        return False

    return user_passes_test(check_perms, login_url=login_url)

def has_finance_permission(permission_name):
    """
    Finans modülü izin kontrolü decorator'ı
    """
    return permission_required(f'finance.{permission_name}')

def has_permission(permission_name):
    """
    Kullanıcının belirtilen izne sahip olup olmadığını kontrol eden decorator
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator

def is_finance_manager(function=None):
    """
    Finans yöneticisi kontrolü
    """
    actual_decorator = user_passes_test(
        lambda u: u.groups.filter(name='Finance Manager').exists() or u.is_superuser
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def can_manage_transactions(function=None):
    """
    Kullanıcının işlem yönetimi yetkisine sahip olup olmadığını kontrol eden decorator
    """
    actual_decorator = user_passes_test(
        lambda u: u.has_perm('finance.manage_transactions')
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
