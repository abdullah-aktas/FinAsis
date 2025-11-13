# -*- coding: utf-8 -*-
"""
FinAsis RBAC (Role-Based Access Control) Sistemi
Kapsamlı yetki kontrolü ve rol tabanlı erişim yönetimi
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# ROL TANIMLARI VE YETKİ MATRİSİ
# ============================================================================

# Rol kategorileri
ROLE_CATEGORIES = {
    'superadmin': {
        'groups': ['Süper Yöneticiler', 'Sistem Yöneticileri'],
        'level': 100,
        'description': 'Tüm sistem yetkilerine sahip',
        'color': 'danger',
        'icon': 'bi-shield-fill-exclamation'
    },
    'system_admin': {
        'groups': ['Sistem Yöneticileri'],
        'level': 90,
        'description': 'Sistem yönetimi ve ayarları',
        'color': 'warning',
        'icon': 'bi-gear-fill'
    },
    'company_owner': {
        'groups': ['Şirket Sahipleri', 'Finans Yöneticisi'],
        'level': 80,
        'description': 'Şirket sahibi - Tüm şirket işlemleri',
        'color': 'primary',
        'icon': 'bi-building'
    },
    'finance_manager': {
        'groups': ['Finans Yöneticisi', 'Muhasebeciler'],
        'level': 70,
        'description': 'Finans ve muhasebe yönetimi',
        'color': 'success',
        'icon': 'bi-cash-stack'
    },
    'accountant': {
        'groups': ['Muhasebeciler'],
        'level': 60,
        'description': 'Muhasebe işlemleri',
        'color': 'info',
        'icon': 'bi-calculator'
    },
    'advisor': {
        'groups': ['Mali Müşavirler'],
        'level': 55,
        'description': 'Mali danışmanlık ve raporlama',
        'color': 'secondary',
        'icon': 'bi-person-badge'
    },
    'teacher': {
        'groups': ['Öğretmenler', 'Eğitim Yöneticisi'],
        'level': 50,
        'description': 'Eğitim içerik yönetimi',
        'color': 'warning',
        'icon': 'bi-mortarboard'
    },
    'employee': {
        'groups': ['Çalışanlar'],
        'level': 40,
        'description': 'Temel çalışan yetkisi',
        'color': 'secondary',
        'icon': 'bi-person'
    },
    'student': {
        'groups': ['Öğrenciler', 'Oyuncular'],
        'level': 30,
        'description': 'Eğitim ve oyun erişimi',
        'color': 'info',
        'icon': 'bi-book'
    },
    'auditor': {
        'groups': ['Denetçiler', 'Rapor Görüntüleyici'],
        'level': 20,
        'description': 'Salt okuma - Denetim',
        'color': 'dark',
        'icon': 'bi-eye'
    },
    'viewer': {
        'groups': ['Rapor Görüntüleyici'],
        'level': 10,
        'description': 'Sadece görüntüleme',
        'color': 'secondary',
        'icon': 'bi-eye'
    },
}

# APP bazında yetki matrisi
APP_PERMISSIONS = {
    'accounting': {
        'view': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'advisor', 'auditor'],
        'add': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant'],
        'change': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant'],
        'delete': ['superadmin', 'system_admin', 'company_owner'],
        'approve': ['superadmin', 'company_owner', 'finance_manager'],
    },
    'finance': {
        'view': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'advisor', 'auditor'],
        'add': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant'],
        'change': ['superadmin', 'system_admin', 'company_owner', 'finance_manager'],
        'delete': ['superadmin', 'system_admin', 'company_owner'],
        'banking': ['superadmin', 'company_owner', 'finance_manager'],
    },
    'ai_assistant': {
        'view': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'employee'],
        'use': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'employee'],
        'configure': ['superadmin', 'system_admin', 'company_owner'],
    },
    'education': {
        'view': ['superadmin', 'system_admin', 'teacher', 'student'],
        'add': ['superadmin', 'system_admin', 'teacher'],
        'change': ['superadmin', 'system_admin', 'teacher'],
        'delete': ['superadmin', 'system_admin', 'teacher'],
        'manage_students': ['superadmin', 'system_admin', 'teacher'],
        'take_course': ['student'],
    },
    'games': {
        'view': ['superadmin', 'system_admin', 'teacher', 'student'],
        'play': ['student', 'teacher'],
        'manage': ['superadmin', 'system_admin', 'teacher'],
    },
    'blockchain': {
        'view': ['superadmin', 'system_admin', 'company_owner', 'finance_manager'],
        'add': ['superadmin', 'system_admin', 'company_owner'],
        'manage': ['superadmin', 'system_admin'],
    },
    'management': {
        'view': ['superadmin', 'system_admin', 'company_owner'],
        'add': ['superadmin', 'system_admin', 'company_owner'],
        'change': ['superadmin', 'system_admin', 'company_owner'],
        'delete': ['superadmin', 'system_admin'],
        'user_management': ['superadmin', 'system_admin', 'company_owner'],
    },
    'audit': {
        'view': ['superadmin', 'system_admin', 'company_owner', 'auditor'],
        'export': ['superadmin', 'system_admin', 'auditor'],
    },
    'billing': {
        'view': ['superadmin', 'system_admin', 'company_owner'],
        'manage': ['superadmin', 'system_admin'],
        'subscribe': ['company_owner'],
    },
    'corporate': {
        'view': ['superadmin', 'system_admin', 'company_owner'],
        'manage': ['superadmin', 'system_admin', 'company_owner'],
    },
}

# URL Pattern bazında yetki kontrolü
URL_ROLE_MAPPING = {
    # Admin ve sistem yönetimi
    r'^/admin/': ['superadmin', 'system_admin'],
    r'^/management/': ['superadmin', 'system_admin', 'company_owner'],
    r'^/management/users/': ['superadmin', 'system_admin', 'company_owner'],
    r'^/management/settings/': ['superadmin', 'system_admin'],
    
    # Muhasebe
    r'^/accounting/': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'advisor', 'auditor'],
    r'^/accounting/.*/(edit|update|delete)/': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant'],
    r'^/accounting/.*/approve/': ['superadmin', 'company_owner', 'finance_manager'],
    
    # Finans
    r'^/finance/': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'advisor', 'auditor'],
    r'^/finance/banking/': ['superadmin', 'company_owner', 'finance_manager'],
    r'^/finance/.*/(edit|update|delete)/': ['superadmin', 'system_admin', 'company_owner', 'finance_manager'],
    
    # AI Asistan
    r'^/ai-assistant/': ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant', 'employee'],
    r'^/ai-assistant/settings/': ['superadmin', 'system_admin', 'company_owner'],
    
    # Eğitim
    r'^/education/': ['superadmin', 'system_admin', 'teacher', 'student'],
    r'^/education/manage/': ['superadmin', 'system_admin', 'teacher'],
    r'^/education/student/': ['student', 'teacher'],
    
    # Oyunlar
    r'^/games/': ['superadmin', 'system_admin', 'teacher', 'student'],
    r'^/games/trade-sim/': ['student', 'teacher'],
    r'^/games/manage/': ['superadmin', 'system_admin', 'teacher'],
    
    # Blockchain
    r'^/blockchain/': ['superadmin', 'system_admin', 'company_owner', 'finance_manager'],
    r'^/blockchain/contracts/': ['superadmin', 'system_admin', 'company_owner'],
    
    # Denetim
    r'^/audit/': ['superadmin', 'system_admin', 'company_owner', 'auditor'],
    
    # Faturalama
    r'^/billing/': ['superadmin', 'system_admin', 'company_owner'],
    r'^/billing/subscribe/': ['company_owner'],
}


# ============================================================================
# YETKİ KONTROL FONKSİYONLARI
# ============================================================================

def get_user_role_category(user) -> Optional[str]:
    """
    Kullanıcının rol kategorisini döndürür
    """
    if not user or not user.is_authenticated:
        return None
    
    # Superuser kontrolü
    if user.is_superuser:
        return 'superadmin'
    
    # Kullanıcının gruplarını al
    user_groups = set(user.groups.values_list('name', flat=True))
    
    # En yüksek yetkili rolü bul
    highest_role = None
    highest_level = 0
    
    for role_name, role_info in ROLE_CATEGORIES.items():
        role_groups = set(role_info['groups'])
        if user_groups & role_groups:  # Kesişim var mı?
            if role_info['level'] > highest_level:
                highest_level = role_info['level']
                highest_role = role_name
    
    return highest_role


def user_has_role(user, required_roles: List[str]) -> bool:
    """
    Kullanıcının gerekli rollerden birine sahip olup olmadığını kontrol eder
    """
    if not user or not user.is_authenticated:
        return False
    
    user_role = get_user_role_category(user)
    
    if not user_role:
        return False
    
    # Süper admin her şeyi yapabilir
    if user_role == 'superadmin':
        return True
    
    return user_role in required_roles


def user_has_app_permission(user, app_name: str, permission: str) -> bool:
    """
    Kullanıcının belirli bir app'te belirli bir yetkiye sahip olup olmadığını kontrol eder
    """
    if not user or not user.is_authenticated:
        return False
    
    # App permission matrix'te var mı?
    if app_name not in APP_PERMISSIONS:
        logger.warning(f"App '{app_name}' not found in APP_PERMISSIONS")
        return False
    
    if permission not in APP_PERMISSIONS[app_name]:
        logger.warning(f"Permission '{permission}' not found for app '{app_name}'")
        return False
    
    required_roles = APP_PERMISSIONS[app_name][permission]
    return user_has_role(user, required_roles)


def get_user_accessible_apps(user) -> dict:
    """
    Kullanıcının erişebileceği app'leri ve yetkilerini döndürür
    """
    if not user or not user.is_authenticated:
        return {}
    
    accessible_apps = {}
    user_role = get_user_role_category(user)
    
    if not user_role:
        return {}
    
    for app_name, permissions in APP_PERMISSIONS.items():
        app_permissions = {}
        for perm, roles in permissions.items():
            if user_has_role(user, roles):
                app_permissions[perm] = True
        
        if app_permissions:
            accessible_apps[app_name] = app_permissions
    
    return accessible_apps


def check_url_permission(user, url_path: str) -> bool:
    """
    Kullanıcının belirli bir URL'ye erişim yetkisi olup olmadığını kontrol eder
    """
    if not user or not user.is_authenticated:
        return False
    
    # Süper admin her şeye erişebilir
    if user.is_superuser:
        return True
    
    import re
    
    for url_pattern, required_roles in URL_ROLE_MAPPING.items():
        if re.match(url_pattern, url_path):
            return user_has_role(user, required_roles)
    
    # Pattern bulunamadıysa, varsayılan olarak izin ver
    # (Bu, her URL'i tanımlamak zorunda olmamak için)
            return True


# ============================================================================
# DECORATORS
# ============================================================================

def role_required(*required_roles):
    """
    View için rol kontrolü decorator'u
    
    Kullanım:
        @role_required('company_owner', 'finance_manager')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
                return redirect('accounts:login')
            
            if not user_has_role(request.user, required_roles):
                user_role = get_user_role_category(request.user)
                logger.warning(
                    f"Yetkisiz erişim denemesi: User={request.user.username}, "
                    f"Role={user_role}, Required={required_roles}, "
                    f"Path={request.path}"
                )
                messages.error(
                    request,
                    f'Bu sayfaya erişim yetkiniz yok. Gerekli rol: {", ".join(required_roles)}'
                )
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def app_permission_required(app_name: str, permission: str):
    """
    App bazlı yetki kontrolü decorator'u
    
    Kullanım:
        @app_permission_required('accounting', 'add')
        def add_invoice(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
                return redirect('accounts:login')
            
            if not user_has_app_permission(request.user, app_name, permission):
                user_role = get_user_role_category(request.user)
                logger.warning(
                    f"Yetkisiz erişim denemesi: User={request.user.username}, "
                    f"Role={user_role}, App={app_name}, Permission={permission}, "
                    f"Path={request.path}"
                )
                messages.error(
                    request,
                    f'Bu işlemi yapmaya yetkiniz yok. ({app_name}.{permission})'
                )
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def superadmin_required(view_func):
    """
    Sadece süper admin için
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
            return redirect('accounts:login')
        
        if not request.user.is_superuser:
            logger.warning(
                f"Süper admin erişim denemesi: User={request.user.username}, "
                f"Path={request.path}"
            )
            messages.error(request, 'Bu sayfaya sadece süper yöneticiler erişebilir.')
            return redirect('accounts:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def company_owner_required(view_func):
    """
    Sadece şirket sahipleri için
    """
    return role_required('superadmin', 'system_admin', 'company_owner')(view_func)


def finance_access_required(view_func):
    """
    Finans erişimi gereken view'lar için
    """
    return role_required(
        'superadmin', 'system_admin', 'company_owner', 
        'finance_manager', 'accountant'
    )(view_func)


# ============================================================================
# CLASS-BASED VIEW MIXINS
# ============================================================================

class RoleRequiredMixin:
    """
    Class-based view'lar için rol kontrolü mixin'i
    
    Kullanım:
        class MyView(RoleRequiredMixin, View):
            required_roles = ['company_owner', 'finance_manager']
    """
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
            return redirect('accounts:login')
        
        if not user_has_role(request.user, self.required_roles):
            user_role = get_user_role_category(request.user)
            logger.warning(
                f"Yetkisiz erişim denemesi: User={request.user.username}, "
                f"Role={user_role}, Required={self.required_roles}, "
                f"Path={request.path}"
            )
            messages.error(
                request,
                f'Bu sayfaya erişim yetkiniz yok. Gerekli rol: {", ".join(self.required_roles)}'
            )
            return redirect('accounts:dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class AppPermissionRequiredMixin:
    """
    Class-based view'lar için app permission kontrolü
    
    Kullanım:
        class AddInvoiceView(AppPermissionRequiredMixin, View):
            app_name = 'accounting'
            permission = 'add'
    """
    app_name = None
    permission = None
    
    def dispatch(self, request, *args, **kwargs):
        if not self.app_name or not self.permission:
            raise ValueError("app_name and permission must be set")
        
        if not request.user.is_authenticated:
            messages.error(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
            return redirect('accounts:login')
        
        if not user_has_app_permission(request.user, self.app_name, self.permission):
            user_role = get_user_role_category(request.user)
            logger.warning(
                f"Yetkisiz erişim denemesi: User={request.user.username}, "
                f"Role={user_role}, App={self.app_name}, Permission={self.permission}, "
                f"Path={request.path}"
            )
            messages.error(
                request,
                f'Bu işlemi yapmaya yetkiniz yok. ({self.app_name}.{self.permission})'
            )
            return redirect('accounts:dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class CompanyOwnerRequiredMixin(RoleRequiredMixin):
    """Şirket sahibi kontrolü"""
    required_roles = ['superadmin', 'system_admin', 'company_owner']


class FinanceAccessRequiredMixin(RoleRequiredMixin):
    """Finans erişimi kontrolü"""
    required_roles = ['superadmin', 'system_admin', 'company_owner', 'finance_manager', 'accountant']


class SuperAdminRequiredMixin:
    """Süper admin kontrolü"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, 'Bu sayfaya sadece süper yöneticiler erişebilir.')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_role_info(role_name: str) -> dict:
    """Rol bilgisini döndürür"""
    return ROLE_CATEGORIES.get(role_name, {})


def get_user_role_info(user) -> dict:
    """Kullanıcının rol bilgisini döndürür"""
    role_name = get_user_role_category(user)
    if not role_name:
        return {}
    
    role_info = get_role_info(role_name)
    role_info['name'] = role_name
    role_info['user_groups'] = list(user.groups.values_list('name', flat=True))
    
    return role_info
