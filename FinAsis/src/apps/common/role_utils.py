"""
Role-based access control utilities for FinAsis
Kullanıcı rollerine göre erişim kontrolü için yardımcı fonksiyonlar
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _


# Rol Tanımları
class UserRoles:
    """Sistemdeki tüm roller"""
    # CustomUser.role field'ı için
    ADMIN = 'admin'
    STAFF = 'staff'
    VIEWER = 'viewer'
    
    # UserType.code field'ı için (audience types)
    KOBI_OWNER = 'kobi_owner'
    KOBI_STAFF = 'kobi_staff'
    ACCOUNTANT = 'accountant'
    FINANCIAL_ADVISOR = 'financial_advisor'
    FINANCE_MANAGER = 'finance_manager'
    TEACHER = 'teacher'
    STUDENT = 'student'
    PLAYER = 'player'
    AUDITOR = 'auditor'


# Permission Groups
class PermissionGroups:
    """İzin grupları"""
    # Finansal işlemler
    CAN_VIEW_FINANCE = ['admin', 'kobi_owner', 'accountant', 'financial_advisor', 'finance_manager']
    CAN_CREATE_INVOICE = ['admin', 'kobi_owner', 'accountant']
    CAN_DELETE_INVOICE = ['admin', 'kobi_owner']
    CAN_APPROVE_PAYMENT = ['admin', 'kobi_owner', 'finance_manager']
    
    # Eğitim işlemleri
    CAN_VIEW_EDUCATION = ['admin', 'teacher', 'student']
    CAN_CREATE_COURSE = ['admin', 'teacher']
    CAN_GRADE_ASSIGNMENT = ['admin', 'teacher']
    
    # Oyun işlemleri
    CAN_PLAY_GAMES = ['admin', 'player', 'student']
    CAN_VIEW_LEADERBOARD = ['admin', 'player', 'student', 'teacher']
    
    # Yönetim işlemleri
    CAN_MANAGE_USERS = ['admin']
    CAN_MANAGE_COMPANY = ['admin', 'kobi_owner']
    CAN_VIEW_REPORTS = ['admin', 'kobi_owner', 'accountant', 'financial_advisor', 'finance_manager']
    
    # AI Asistan
    CAN_USE_AI = ['admin', 'kobi_owner', 'accountant', 'financial_advisor', 'finance_manager', 'teacher']


def get_user_role(user):
    """
    Kullanıcının ana rolünü döndürür
    Öncelik: UserType > CustomUser.role > 'viewer'
    """
    if not user or not user.is_authenticated:
        return None
    
    # UserType varsa onu kullan
    if hasattr(user, 'user_type') and user.user_type:
        return user.user_type.code
    
    # CustomUser.role kullan
    if hasattr(user, 'role'):
        return user.role
    
    # Default
    return 'viewer'


def get_user_roles(user):
    """
    Kullanıcının tüm rollerini liste olarak döndürür
    (Multi-role support için)
    """
    if not user or not user.is_authenticated:
        return []
    
    roles = []
    
    # CustomUser.role
    if hasattr(user, 'role') and user.role:
        roles.append(user.role)
    
    # UserType
    if hasattr(user, 'user_type') and user.user_type:
        roles.append(user.user_type.code)
    
    # İleride permissions app eklenirse buraya kod eklenebilir
    # Şimdilik CustomUser.role ve UserType.code yeterli
    
    # Remove duplicates
    return list(set(roles))


def user_has_role(user, role):
    """Kullanıcının belirtilen rolü var mı?"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    user_roles = get_user_roles(user)
    return role in user_roles


def user_has_any_role(user, roles):
    """Kullanıcının belirtilen rollerden herhangi biri var mı?"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    user_roles = get_user_roles(user)
    return any(role in user_roles for role in roles)


def user_can(user, permission_group):
    """Kullanıcının belirtilen izin grubu var mı?"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    user_roles = get_user_roles(user)
    return any(role in permission_group for role in user_roles)


# Decorators
def role_required(*roles):
    """
    View decorator: Belirtilen rollerden birini gerektiren view
    
    Kullanım:
    @role_required('admin', 'kobi_owner')
    def my_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _('Bu sayfaya erişmek için giriş yapmalısınız.'))
                return redirect('accounts:login')
            
            if not user_has_any_role(request.user, roles):
                messages.error(request, _('Bu sayfaya erişim yetkiniz yok.'))
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def permission_required(permission_group):
    """
    View decorator: Belirtilen izin grubunu gerektiren view
    
    Kullanım:
    @permission_required(PermissionGroups.CAN_CREATE_INVOICE)
    def create_invoice(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _('Bu sayfaya erişmek için giriş yapmalısınız.'))
                return redirect('accounts:login')
            
            if not user_can(request.user, permission_group):
                messages.error(request, _('Bu işlem için yetkiniz yok.'))
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# Template Context Helpers
def get_menu_items_for_user(user):
    """Kullanıcının erişebileceği menü öğelerini döndürür"""
    if not user or not user.is_authenticated:
        return []
    
    menu_items = []
    
    # Dashboard - herkes görebilir
    menu_items.append({
        'name': _('Dashboard'),
        'url': 'dashboard',
        'icon': 'bi-speedometer2',
        'roles': ['*']  # herkes
    })
    
    # Muhasebe
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        menu_items.append({
            'name': _('Muhasebe'),
            'url': 'accounting:home',
            'icon': 'bi-calculator',
            'roles': PermissionGroups.CAN_VIEW_FINANCE
        })
    
    # Finans
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        menu_items.append({
            'name': _('Finans'),
            'url': 'finance:home',
            'icon': 'bi-graph-up',
            'roles': PermissionGroups.CAN_VIEW_FINANCE
        })
    
    # Eğitim
    if user_can(user, PermissionGroups.CAN_VIEW_EDUCATION):
        menu_items.append({
            'name': _('Eğitim'),
            'url': 'education:index',
            'icon': 'bi-mortarboard',
            'roles': PermissionGroups.CAN_VIEW_EDUCATION
        })
    
    # Oyunlar
    if user_can(user, PermissionGroups.CAN_PLAY_GAMES):
        menu_items.append({
            'name': _('Oyunlar'),
            'url': 'games:home',
            'icon': 'bi-controller',
            'roles': PermissionGroups.CAN_PLAY_GAMES
        })
    
    # AI Asistan
    if user_can(user, PermissionGroups.CAN_USE_AI):
        menu_items.append({
            'name': _('AI Asistan'),
            'url': 'ai_assistant:home',
            'icon': 'bi-robot',
            'roles': PermissionGroups.CAN_USE_AI
        })
    
    # Raporlar
    if user_can(user, PermissionGroups.CAN_VIEW_REPORTS):
        menu_items.append({
            'name': _('Raporlar'),
            'url': 'finance:reports_index',
            'icon': 'bi-file-earmark-text',
            'roles': PermissionGroups.CAN_VIEW_REPORTS
        })
    
    # Yönetim (sadece admin)
    if user_has_role(user, 'admin'):
        menu_items.append({
            'name': _('Yönetim'),
            'url': 'management:dashboard',
            'icon': 'bi-gear',
            'roles': ['admin']
        })
    
    return menu_items


def get_quick_actions_for_user(user):
    """Kullanıcının yapabileceği hızlı işlemleri döndürür"""
    if not user or not user.is_authenticated:
        return []
    
    actions = []
    
    # Fatura oluşturma
    if user_can(user, PermissionGroups.CAN_CREATE_INVOICE):
        actions.append({
            'name': _('Yeni Fatura'),
            'url': 'accounting:invoice_create',
            'icon': 'bi-receipt',
            'color': 'primary'
        })
    
    # Gider ekleme
    if user_can(user, PermissionGroups.CAN_CREATE_INVOICE):
        actions.append({
            'name': _('Gider Ekle'),
            'url': 'accounting:expense_create',
            'icon': 'bi-cash-coin',
            'color': 'danger'
        })
    
    # Rapor oluşturma
    if user_can(user, PermissionGroups.CAN_VIEW_REPORTS):
        actions.append({
            'name': _('Rapor Oluştur'),
            'url': 'finance:reports_index',
            'icon': 'bi-file-earmark-text',
            'color': 'success'
        })
    
    # Müşteri ekleme
    if user_can(user, PermissionGroups.CAN_CREATE_INVOICE):
        actions.append({
            'name': _('Müşteri Ekle'),
            'url': 'accounting:customer_create',
            'icon': 'bi-person-plus',
            'color': 'info'
        })
    
    return actions


def get_dashboard_widgets_for_user(user):
    """Kullanıcının dashboard'ında göreceği widget'ları döndürür"""
    if not user or not user.is_authenticated:
        return []
    
    widgets = []
    
    # KPI Widget'ları
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        widgets.extend([
            {'type': 'kpi', 'name': 'total_income', 'order': 1},
            {'type': 'kpi', 'name': 'total_expense', 'order': 2},
            {'type': 'kpi', 'name': 'net_profit', 'order': 3},
            {'type': 'kpi', 'name': 'cash_balance', 'order': 4},
        ])
    
    # Grafik
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        widgets.append({'type': 'chart', 'name': 'financial_trend', 'order': 5})
    
    # Hızlı İşlemler
    if user_can(user, PermissionGroups.CAN_CREATE_INVOICE):
        widgets.append({'type': 'quick_actions', 'name': 'quick_actions', 'order': 6})
    
    # AI Önerileri
    if user_can(user, PermissionGroups.CAN_USE_AI):
        widgets.append({'type': 'ai_suggestions', 'name': 'ai_suggestions', 'order': 7})
    
    # Son Aktiviteler
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        widgets.extend([
            {'type': 'list', 'name': 'recent_invoices', 'order': 8},
            {'type': 'list', 'name': 'pending_payments', 'order': 9},
        ])
    
    # Eğitim widget'ları
    if user_has_any_role(user, ['teacher', 'student']):
        widgets.extend([
            {'type': 'list', 'name': 'recent_courses', 'order': 10},
            {'type': 'list', 'name': 'assignments', 'order': 11},
        ])
    
    # Oyun widget'ları
    if user_has_role(user, 'player'):
        widgets.extend([
            {'type': 'leaderboard', 'name': 'leaderboard', 'order': 12},
            {'type': 'achievements', 'name': 'achievements', 'order': 13},
        ])
    
    # Order'a göre sırala
    return sorted(widgets, key=lambda x: x['order'])


def get_user_dashboard_type(user):
    """Kullanıcı için hangi dashboard gösterileceğini belirler"""
    if not user or not user.is_authenticated:
        return 'default'
    
    # Superuser
    if user.is_superuser:
        return 'admin'
    
    # UserType'a göre
    if hasattr(user, 'user_type') and user.user_type:
        code = user.user_type.code
        if 'kobi' in code:
            return 'kobi'
        elif code == 'teacher':
            return 'teacher'
        elif code == 'student':
            return 'student'
        elif code == 'player':
            return 'player'
        elif 'accountant' in code:
            return 'accountant'
        elif 'financial_advisor' in code:
            return 'advisor'
        elif 'finance_manager' in code:
            return 'finance_manager'
    
    # CustomUser.role'e göre
    if hasattr(user, 'role'):
        if user.role == 'admin':
            return 'admin'
        elif user.role == 'staff':
            return 'staff'
    
    return 'default'


def get_allowed_modules_for_user(user):
    """Kullanıcının erişebileceği modülleri döndürür"""
    if not user or not user.is_authenticated:
        return []
    
    modules = []
    
    # Muhasebe
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        modules.append('accounting')
    
    # Finans
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        modules.append('finance')
    
    # Eğitim
    if user_can(user, PermissionGroups.CAN_VIEW_EDUCATION):
        modules.append('education')
    
    # Oyunlar
    if user_can(user, PermissionGroups.CAN_PLAY_GAMES):
        modules.append('games')
    
    # AI Asistan
    if user_can(user, PermissionGroups.CAN_USE_AI):
        modules.append('ai_assistant')
    
    # Blockchain
    if user_can(user, PermissionGroups.CAN_VIEW_FINANCE):
        modules.append('blockchain')
    
    # Audit
    if user_has_any_role(user, ['admin', 'auditor', 'financial_advisor']):
        modules.append('audit')
    
    # Yönetim
    if user_has_role(user, 'admin'):
        modules.append('management')
    
    return modules


def get_role_display_name(role_code):
    """Rol kodunu görünen isme çevirir"""
    role_names = {
        'admin': 'Yönetici',
        'staff': 'Çalışan',
        'viewer': 'İzleyici',
        'kobi_owner': 'KOBİ Sahibi',
        'kobi_staff': 'KOBİ Çalışanı',
        'accountant': 'Muhasebeci',
        'financial_advisor': 'Mali Müşavir',
        'finance_manager': 'Finans Müdürü',
        'teacher': 'Öğretmen',
        'student': 'Öğrenci',
        'player': 'Oyuncu',
        'auditor': 'Denetçi',
    }
    return role_names.get(role_code, role_code.title())


def get_role_icon(role_code):
    """Rol koduna uygun icon döndürür"""
    role_icons = {
        'admin': 'bi-shield-lock',
        'kobi_owner': 'bi-building',
        'accountant': 'bi-calculator',
        'financial_advisor': 'bi-briefcase',
        'finance_manager': 'bi-graph-up',
        'teacher': 'bi-mortarboard',
        'student': 'bi-book',
        'player': 'bi-controller',
        'auditor': 'bi-shield-check',
    }
    return role_icons.get(role_code, 'bi-person')


def get_role_color(role_code):
    """Rol koduna uygun renk döndürür"""
    role_colors = {
        'admin': 'danger',
        'kobi_owner': 'primary',
        'accountant': 'success',
        'financial_advisor': 'info',
        'finance_manager': 'warning',
        'teacher': 'purple',
        'student': 'info',
        'player': 'success',
        'auditor': 'secondary',
    }
    return role_colors.get(role_code, 'secondary')

