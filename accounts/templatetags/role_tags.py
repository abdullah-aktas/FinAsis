# accounts/templatetags/role_tags.py - Template'lerde rol kontrolü için

from django import template

register = template.Library()


@register.simple_tag
def user_has_role(user, role_name):
    """Kullanıcının belirli bir rolü olup olmadığını kontrol et"""
    if not user or not user.is_authenticated:
        return False

    try:
        return user.profile.role.name == role_name
    except (AttributeError, Exception):
        return False


@register.simple_tag
def user_has_permission(user, permission):
    """Kullanıcının belirli bir izni olup olmadığını kontrol et"""
    if not user or not user.is_authenticated:
        return False

    try:
        role = user.profile.role
        return getattr(role, permission, False)
    except (AttributeError, Exception):
        return False


@register.simple_tag
def user_can_access_module(user, module_name):
    """Kullanıcının modüle erişip erişemeyeceğini kontrol et"""
    if not user or not user.is_authenticated:
        return False

    try:
        role = user.profile.role
        subscription = user.subscription

        # Rol kontrolü
        role_permission_map = {
            "ai_assistant": role.can_access_ai,
            "education": role.can_use_education,
            "games": role.can_play_games,
            "blockchain": role.can_use_blockchain,
            "accounting": True,  # Temel modül
            "finance": True,  # Temel modül
        }

        # Plan kontrolü
        plan_feature_map = {
            "ai_assistant": subscription.plan.has_ai_assistant,
            "education": subscription.plan.has_education,
            "games": subscription.plan.has_games,
            "blockchain": subscription.plan.has_blockchain,
            "accounting": subscription.plan.has_accounting,
            "finance": subscription.plan.has_finance,
        }

        has_role_permission = role_permission_map.get(module_name, False)
        has_plan_feature = plan_feature_map.get(module_name, True)

        return has_role_permission and has_plan_feature and subscription.is_active

    except (AttributeError, Exception):
        return False


@register.simple_tag
def user_hierarchy_level(user):
    """Kullanıcının hiyerarşi seviyesi"""
    try:
        return user.profile.role.hierarchy_level
    except (AttributeError, Exception):
        return 999  # En düşük seviye


@register.simple_tag
def can_manage_user(manager_user, target_user):
    """Bir kullanıcının diğerini yönetip yönetemeyeceğini kontrol et"""
    if not manager_user or not manager_user.is_authenticated:
        return False

    try:
        manager_level = manager_user.profile.role.hierarchy_level
        target_level = target_user.profile.role.hierarchy_level
        manager_can_manage = manager_user.profile.role.can_manage_users

        # Süper admin herkesi yönetebilir
        if manager_user.profile.role.name == "super_admin":
            return True

        # Yönetici kendisini yönetemez
        if manager_user.id == target_user.id:
            return False

        # Yönetim iznine sahip olmalı ve daha üst seviyede olmalı
        return manager_can_manage and manager_level < target_level

    except (AttributeError, Exception):
        return False


@register.simple_tag
def subscription_feature_status(user, feature_name):
    """Abonelik özelliğinin durumunu kontrol et"""
    try:
        subscription = user.subscription
        if not subscription.is_active:
            return "expired"

        has_feature = getattr(subscription.plan, f"has_{feature_name}", False)

        if has_feature:
            return "active"
        else:
            return "unavailable"

    except (AttributeError, Exception):
        return "unavailable"


@register.simple_tag
def user_monthly_transaction_limit(user):
    """Kullanıcının aylık işlem limiti"""
    try:
        subscription = user.subscription
        role_limit = user.profile.role.max_transactions_per_month
        plan_limit = subscription.plan.max_transactions

        # En kısıtlayıcı limit geçerli
        if role_limit == -1 and plan_limit == -1:
            return -1  # Sınırsız
        elif role_limit == -1:
            return plan_limit
        elif plan_limit == -1:
            return role_limit
        else:
            return min(role_limit, plan_limit)

    except (AttributeError, Exception):
        return 0


@register.simple_tag
def user_remaining_transactions(user):
    """Kullanıcının kalan işlem sayısı"""
    try:
        subscription = user.subscription
        limit = user_monthly_transaction_limit(user)

        if limit == -1:
            return "Sınırsız"

        used = subscription.current_month_transactions
        remaining = max(0, limit - used)

        return remaining

    except (AttributeError, Exception):
        return 0


@register.filter
def role_badge_color(role_name):
    """Rol rozet rengi"""
    color_map = {
        "super_admin": "badge-danger",
        "admin": "badge-warning",
        "finance_manager": "badge-dark",
        "financial_advisor": "badge-info",
        "accountant": "badge-success",
        "kobi_owner": "badge-primary",
        "kobi_employee": "badge-secondary",
        "auditor": "badge-dark",
        "teacher": "badge-warning",
        "student": "badge-light",
        "player": "badge-success",
        "viewer": "badge-outline",
    }
    return color_map.get(role_name, "badge-secondary")


@register.filter
def subscription_status_color(status):
    """Abonelik durum rengi"""
    color_map = {
        "active": "text-success",
        "expired": "text-danger",
        "suspended": "text-warning",
        "pending": "text-info",
        "cancelled": "text-muted",
    }
    return color_map.get(status, "text-muted")


@register.inclusion_tag("accounts/tags/user_role_card.html")
def user_role_card(user):
    """Kullanıcı rol kartı"""
    try:
        profile = user.profile
        subscription = user.subscription

        context = {
            "user": user,
            "role": profile.role,
            "subscription": subscription,
            "can_upgrade": subscription.plan.name in ["free", "basic"],
            "expires_soon": subscription.days_remaining <= 7
            if subscription.is_active
            else False,
        }

        return context
    except (AttributeError, Exception):
        return {"user": user}


@register.inclusion_tag("accounts/tags/permission_list.html")
def user_permissions(user):
    """Kullanıcı izin listesi"""
    try:
        role = user.profile.role
        subscription = user.subscription

        permissions = []

        # Yönetim izinleri
        if role.can_manage_users:
            permissions.append(("👥", "Kullanıcı Yönetimi", "success"))
        if role.can_manage_companies:
            permissions.append(("🏢", "Şirket Yönetimi", "success"))
        if role.can_approve_transactions:
            permissions.append(("✅", "İşlem Onaylama", "success"))

        # Mali izinler
        if role.can_view_all_finances:
            permissions.append(("👁️", "Tüm Mali Veriler", "info"))
        if role.can_edit_finances:
            permissions.append(("💰", "Mali Düzenleme", "warning"))
        if role.can_generate_reports:
            permissions.append(("📊", "Rapor Oluşturma", "info"))

        # Modül erişimleri
        if role.can_access_ai and subscription.plan.has_ai_assistant:
            permissions.append(("🤖", "AI Asistan", "primary"))
        if role.can_use_education and subscription.plan.has_education:
            permissions.append(("🎓", "Eğitim Modülü", "success"))
        if role.can_play_games and subscription.plan.has_games:
            permissions.append(("🎮", "Oyunlar", "success"))
        if role.can_use_blockchain and subscription.plan.has_blockchain:
            permissions.append(("⛓️", "Blockchain", "warning"))

        return {"permissions": permissions}

    except (AttributeError, Exception):
        return {"permissions": []}


@register.simple_tag
def navigation_items(user):
    """Kullanıcı rolüne göre navigasyon öğeleri"""
    if not user or not user.is_authenticated:
        return []

    try:
        role = user.profile.role
        subscription = user.subscription

        nav_items = [
            {
                "name": "dashboard",
                "title": "Ana Sayfa",
                "icon": "🏠",
                "url": "/dashboard/",
                "allowed": True,
            },
        ]

        # Mali modüller
        if role.can_view_all_finances or role.can_edit_finances:
            nav_items.append(
                {
                    "name": "accounting",
                    "title": "Muhasebe",
                    "icon": "📚",
                    "url": "/accounting/",
                    "allowed": subscription.plan.has_accounting,
                }
            )
            nav_items.append(
                {
                    "name": "finance",
                    "title": "Finans",
                    "icon": "💼",
                    "url": "/finance/",
                    "allowed": subscription.plan.has_finance,
                }
            )

        # Özel modüller
        if role.can_access_ai:
            nav_items.append(
                {
                    "name": "ai",
                    "title": "AI Asistan",
                    "icon": "🤖",
                    "url": "/ai/",
                    "allowed": subscription.plan.has_ai_assistant,
                }
            )

        if role.can_use_education:
            nav_items.append(
                {
                    "name": "education",
                    "title": "Eğitim",
                    "icon": "🎓",
                    "url": "/education/",
                    "allowed": subscription.plan.has_education,
                }
            )

        if role.can_use_blockchain:
            nav_items.append(
                {
                    "name": "blockchain",
                    "title": "Blockchain",
                    "icon": "⛓️",
                    "url": "/blockchain/",
                    "allowed": subscription.plan.has_blockchain,
                }
            )

        # Yönetim
        if role.can_manage_users:
            nav_items.append(
                {
                    "name": "admin",
                    "title": "Yönetim",
                    "icon": "⚙️",
                    "url": "/admin/",
                    "allowed": True,
                }
            )

        return [item for item in nav_items if item["allowed"]]

    except (AttributeError, Exception):
        return [
            {
                "name": "dashboard",
                "title": "Ana Sayfa",
                "icon": "🏠",
                "url": "/dashboard/",
                "allowed": True,
            }
        ]
