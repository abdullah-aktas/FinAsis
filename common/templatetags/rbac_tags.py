# -*- coding: utf-8 -*-
"""
RBAC Template Tags
Template'lerde rol kontrolü için template tag'ler
"""

from django import template
from common.permissions import (
    user_has_role,
    user_has_app_permission,
    get_user_role_category,
    get_user_role_info,
    get_user_accessible_apps,
    get_role_info,
    ROLE_CATEGORIES,
)

register = template.Library()


@register.filter(name="has_role")
def has_role(user, roles):
    """
    Kullanıcının rolü var mı kontrol eder

    Kullanım:
        {% if user|has_role:"company_owner,finance_manager" %}
        {% endif %}
    """
    if not roles:
        return False

    role_list = [r.strip() for r in roles.split(",")]
    return user_has_role(user, role_list)


@register.filter(name="has_app_permission")
def has_app_permission(user, permission_str):
    """
    Kullanıcının app permission'ı var mı kontrol eder

    Kullanım:
        {% if user|has_app_permission:"accounting.add" %}
        {% endif %}
    """
    if not permission_str or "." not in permission_str:
        return False

    try:
        app_name, permission = permission_str.split(".", 1)
        return user_has_app_permission(user, app_name, permission)
    except (ValueError, AttributeError, Exception):
        return False


@register.simple_tag
def user_role(user):
    """
    Kullanıcının rol kategorisini döndürür

    Kullanım:
        {% user_role user as role %}
        {{ role }}
    """
    return get_user_role_category(user)


@register.simple_tag
def user_role_info(user):
    """
    Kullanıcının rol bilgilerini döndürür

    Kullanım:
        {% user_role_info user as role_info %}
        {{ role_info.description }}
    """
    return get_user_role_info(user)


@register.simple_tag
def user_accessible_apps(user):
    """
    Kullanıcının erişebileceği app'leri döndürür

    Kullanım:
        {% user_accessible_apps user as apps %}
        {% for app_name, permissions in apps.items %}
            {{ app_name }}
        {% endfor %}
    """
    return get_user_accessible_apps(user)


@register.inclusion_tag("common/rbac/role_badge.html")
def role_badge(user):
    """
    Rol rozeti gösterir

    Kullanım:
        {% role_badge user %}
    """
    role_info = get_user_role_info(user)
    return {"role_info": role_info}


@register.inclusion_tag("common/rbac/permission_check.html")
def show_if_has_role(user, roles):
    """
    Rol varsa içeriği gösterir

    Kullanım:
        {% show_if_has_role user "company_owner,finance_manager" %}
            <button>Düzenle</button>
        {% endshow_if_has_role %}
    """
    role_list = [r.strip() for r in roles.split(",")]
    has_permission = user_has_role(user, role_list)
    return {"has_permission": has_permission}


@register.inclusion_tag("common/rbac/app_menu.html")
def rbac_menu(user):
    """
    Kullanıcı için rol bazlı menü oluşturur

    Kullanım:
        {% rbac_menu user %}
    """
    accessible_apps = get_user_accessible_apps(user)
    role_info = get_user_role_info(user)

    # Menü yapısı
    menu_items = []

    # Dashboard (herkes)
    if user.is_authenticated:
        menu_items.append(
            {
                "name": "Dashboard",
                "url": "/dashboard/",
                "icon": "bi-speedometer2",
                "active": True,
            }
        )

    # Accounting & Finance
    if "accounting" in accessible_apps or "finance" in accessible_apps:
        accounting_menu = {
            "name": "Muhasebe & Finans",
            "icon": "bi-calculator",
            "children": [],
        }

        if "accounting" in accessible_apps:
            accounting_menu["children"].append(
                {"name": "Muhasebe", "url": "/accounting/", "icon": "bi-journal-text"}
            )

        if "finance" in accessible_apps:
            accounting_menu["children"].append(
                {"name": "Finans", "url": "/finance/", "icon": "bi-cash-stack"}
            )

        menu_items.append(accounting_menu)

    # AI Assistant
    if "ai_assistant" in accessible_apps:
        menu_items.append(
            {
                "name": "AI Asistan",
                "url": "/ai-assistant/",
                "icon": "bi-robot",
            }
        )

    # Education
    if "education" in accessible_apps:
        menu_items.append(
            {
                "name": "Eğitim",
                "url": "/education/",
                "icon": "bi-mortarboard",
            }
        )

    # Games
    if "games" in accessible_apps:
        menu_items.append(
            {
                "name": "Oyunlar",
                "url": "/games/",
                "icon": "bi-joystick",
            }
        )

    # Blockchain
    if "blockchain" in accessible_apps:
        menu_items.append(
            {
                "name": "Blockchain",
                "url": "/blockchain/",
                "icon": "bi-link-45deg",
            }
        )

    # Management
    if "management" in accessible_apps:
        menu_items.append(
            {
                "name": "Yönetim",
                "url": "/management/",
                "icon": "bi-gear",
            }
        )

    # Audit
    if "audit" in accessible_apps:
        menu_items.append(
            {
                "name": "Denetim",
                "url": "/audit/",
                "icon": "bi-eye",
            }
        )

    return {"menu_items": menu_items, "role_info": role_info, "user": user}


@register.filter
def can_edit(user, obj):
    """
    Nesneyi düzenleyebilir mi kontrol eder

    Kullanım:
        {% if user|can_edit:invoice %}
        {% endif %}
    """
    # Superadmin her şeyi düzenleyebilir
    if user.is_superuser:
        return True

    # Nesnenin app'ini tespit et
    app_label = obj._meta.app_label

    # App permission kontrolü
    return user_has_app_permission(user, app_label, "change")


@register.filter
def can_delete(user, obj):
    """
    Nesneyi silebilir mi kontrol eder

    Kullanım:
        {% if user|can_delete:invoice %}
        {% endif %}
    """
    # Superadmin her şeyi silebilir
    if user.is_superuser:
        return True

    # Nesnenin app'ini tespit et
    app_label = obj._meta.app_label

    # App permission kontrolü
    return user_has_app_permission(user, app_label, "delete")


@register.filter
def can_approve(user, obj):
    """
    Nesneyi onaylayabilir mi kontrol eder

    Kullanım:
        {% if user|can_approve:voucher %}
        {% endif %}
    """
    # Superadmin her şeyi onaylayabilir
    if user.is_superuser:
        return True

    # Nesnenin app'ini tespit et
    app_label = obj._meta.app_label

    # App permission kontrolü
    return user_has_app_permission(user, app_label, "approve")


@register.simple_tag
def get_all_roles():
    """
    Tüm rolleri döndürür

    Kullanım:
        {% get_all_roles as roles %}
        {% for role_name, role_info in roles.items %}
            {{ role_info.description }}
        {% endfor %}
    """
    return ROLE_CATEGORIES


@register.filter
def role_level(user):
    """
    Kullanıcının rol seviyesini döndürür

    Kullanım:
        {{ user|role_level }}
    """
    role_name = get_user_role_category(user)
    if not role_name:
        return 0

    role_info = get_role_info(role_name)
    return role_info.get("level", 0)


@register.filter
def is_higher_role(user, target_role):
    """
    Kullanıcının rolü hedef rolden daha yüksek mi kontrol eder

    Kullanım:
        {% if user|is_higher_role:"accountant" %}
        {% endif %}
    """
    user_role_name = get_user_role_category(user)
    if not user_role_name:
        return False

    user_role_info = get_role_info(user_role_name)
    target_role_info = get_role_info(target_role)

    user_level = user_role_info.get("level", 0)
    target_level = target_role_info.get("level", 0)

    return user_level > target_level
