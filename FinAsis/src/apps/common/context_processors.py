"""
Context processors for FinAsis
Tüm template'lere otomatik olarak eklenecek context verileri
"""

from .role_utils import (
    get_user_role,
    get_user_roles,
    get_menu_items_for_user,
    get_quick_actions_for_user,
    get_dashboard_widgets_for_user,
    get_user_dashboard_type,
    get_allowed_modules_for_user,
    get_role_display_name,
    get_role_icon,
    get_role_color,
    user_can,
    user_has_role,
    user_has_any_role,
    PermissionGroups,
)


def user_roles(request):
    """
    Kullanıcı rol bilgilerini tüm template'lere ekler
    
    Template'lerde kullanım:
    {% if user_role == 'admin' %}
    {% if 'accounting' in user_modules %}
    {% for item in user_menu_items %}
    """
    if not request.user or not request.user.is_authenticated:
        return {
            'user_role': None,
            'user_roles': [],
            'user_menu_items': [],
            'user_quick_actions': [],
            'user_dashboard_widgets': [],
            'user_dashboard_type': 'default',
            'user_modules': [],
            'user_role_display': '',
            'user_role_icon': '',
            'user_role_color': '',
        }
    
    primary_role = get_user_role(request.user)
    all_roles = get_user_roles(request.user)
    
    return {
        'user_role': primary_role,
        'user_roles': all_roles,
        'user_menu_items': get_menu_items_for_user(request.user),
        'user_quick_actions': get_quick_actions_for_user(request.user),
        'user_dashboard_widgets': get_dashboard_widgets_for_user(request.user),
        'user_dashboard_type': get_user_dashboard_type(request.user),
        'user_modules': get_allowed_modules_for_user(request.user),
        'user_role_display': get_role_display_name(primary_role) if primary_role else '',
        'user_role_icon': get_role_icon(primary_role) if primary_role else '',
        'user_role_color': get_role_color(primary_role) if primary_role else '',
        # Helper fonksiyonlar
        'user_can': lambda perm_group: user_can(request.user, perm_group),
        'user_has_role': lambda role: user_has_role(request.user, role),
        'user_has_any_role': lambda roles: user_has_any_role(request.user, roles),
        'PermissionGroups': PermissionGroups,
    }


def platform_context(request):
    """
    Platform genelindeki bilgileri template'lere ekler
    """
    return {
        'platform_name': 'FinAsis',
        'platform_version': 'v2.0',
        'support_email': 'destek@finasis.com.tr',
        'company_name': 'FinAsis Teknoloji A.Ş.',
    }

