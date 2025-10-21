"""
Template tags for role-based access control
Rol bazlı erişim kontrolü için template tag'leri
"""

from django import template
from src.apps.common.role_utils import (
    user_can,
    user_has_role,
    user_has_any_role,
    get_user_role,
    get_user_roles,
    PermissionGroups,
)

register = template.Library()


@register.simple_tag
def can_user(user, permission_group_name):
    """
    Kullanıcının belirtilen izin grubunu kontrol eder
    
    Kullanım:
    {% can_user user 'CAN_CREATE_INVOICE' as can_create %}
    {% if can_create %}
        <button>Fatura Oluştur</button>
    {% endif %}
    """
    if not hasattr(PermissionGroups, permission_group_name):
        return False
    
    perm_group = getattr(PermissionGroups, permission_group_name)
    return user_can(user, perm_group)


@register.filter
def has_role(user, role):
    """
    Kullanıcının belirtilen rolü var mı kontrol eder
    
    Kullanım:
    {% if user|has_role:'admin' %}
        <a href="/admin/">Admin Panel</a>
    {% endif %}
    """
    return user_has_role(user, role)


@register.filter
def has_any_role(user, roles):
    """
    Kullanıcının belirtilen rollerden herhangi biri var mı?
    
    Kullanım:
    {% if user|has_any_role:'admin,kobi_owner' %}
        <button>Özel İşlem</button>
    {% endif %}
    """
    if isinstance(roles, str):
        roles = [r.strip() for r in roles.split(',')]
    return user_has_any_role(user, roles)


@register.simple_tag
def user_primary_role(user):
    """Kullanıcının ana rolünü döndürür"""
    return get_user_role(user)


@register.simple_tag
def user_all_roles(user):
    """Kullanıcının tüm rollerini döndürür"""
    return get_user_roles(user)


@register.inclusion_tag('components/role_badge.html')
def show_role_badge(user):
    """Kullanıcı rol rozetini gösterir"""
    from src.apps.common.role_utils import get_role_display_name, get_role_icon, get_role_color
    role = get_user_role(user)
    return {
        'role': role,
        'role_display': get_role_display_name(role),
        'role_icon': get_role_icon(role),
        'role_color': get_role_color(role),
    }


@register.inclusion_tag('components/quick_actions_menu.html', takes_context=True)
def show_quick_actions(context):
    """Hızlı işlemler menüsünü gösterir"""
    return {
        'actions': context.get('user_quick_actions', []),
        'user': context.get('user'),
    }

