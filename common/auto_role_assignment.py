"""
Otomatik Rol Atama Sistemi
Kullanıcı oluşturulduğunda veya güncellendiğinde otomatik rol atar
"""

from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# Otomatik rol atama kuralları
AUTO_ROLE_RULES = {
    # UserType bazlı roller
    "kobi_owner": {
        "groups": ["Şirket Sahipleri", "Finans Yöneticisi", "Rapor Görüntüleyici"],
        "custom_role": "admin",
        "user_role": "kobi_owner",
        "description": "KOBİ sahipleri için tam yetki",
    },
    "kobi_employee": {
        "groups": ["Çalışanlar", "Rapor Görüntüleyici"],
        "custom_role": "staff",
        "user_role": "kobi_employee",
        "description": "KOBİ çalışanları için temel yetki",
    },
    "accountant": {
        "groups": ["Muhasebeciler", "Finans Yöneticisi", "Rapor Görüntüleyici"],
        "custom_role": "staff",
        "user_role": "accountant",
        "description": "Muhasebeciler için finans yetkisi",
    },
    "financial_advisor": {
        "groups": ["Mali Müşavirler", "Finans Yöneticisi", "Rapor Görüntüleyici"],
        "custom_role": "staff",
        "user_role": "financial_advisor",
        "description": "Mali müşavirler için danışmanlık yetkisi",
    },
    "teacher": {
        "groups": ["Öğretmenler", "Eğitim Yöneticisi"],
        "custom_role": "staff",
        "user_role": "teacher",
        "description": "Öğretmenler için eğitim yetkisi",
    },
    "student": {
        "groups": ["Öğrenciler", "Oyuncular"],
        "custom_role": "viewer",
        "user_role": "student",
        "description": "Öğrenciler için eğitim ve oyun yetkisi",
    },
    "player": {
        "groups": ["Oyuncular"],
        "custom_role": "viewer",
        "user_role": "player",
        "description": "Oyuncular için oyun yetkisi",
    },
    "auditor": {
        "groups": ["Denetçiler", "Rapor Görüntüleyici"],
        "custom_role": "viewer",
        "user_role": "auditor",
        "description": "Denetçiler için salt okuma yetkisi",
    },
}

# Admin kullanıcılar için özel roller
ADMIN_USER_RULES = {
    "superuser": {
        "groups": [
            "Süper Yöneticiler",
            "Sistem Yöneticileri",
            "Finans Yöneticisi",
            "Eğitim Yöneticisi",
            "Rapor Görüntüleyici",
        ],
        "custom_role": "admin",
        "user_role": "super_admin",
        "description": "Süper kullanıcılar için tam sistem yetkisi",
    },
    "staff": {
        "groups": ["Sistem Yöneticileri", "Rapor Görüntüleyici"],
        "custom_role": "admin",
        "user_role": "admin",
        "description": "Staff kullanıcılar için yönetim yetkisi",
    },
}

# Email domain bazlı roller (demo amaçlı)
EMAIL_DOMAIN_RULES = {
    "finasis.com": {
        "groups": ["FinAsis Çalışanları", "Sistem Yöneticileri"],
        "custom_role": "admin",
        "user_role": "admin",
        "description": "FinAsis çalışanları için özel yetki",
    },
    "gmail.com": {
        "groups": ["Dış Kullanıcılar"],
        "custom_role": "viewer",
        "user_role": "viewer",
        "description": "Dış kullanıcılar için temel yetki",
    },
}


def get_required_groups():
    """
    Sistemde olması gereken tüm grupları döndürür
    """
    groups = set()

    # AUTO_ROLE_RULES'dan grupları topla
    for rule in AUTO_ROLE_RULES.values():
        groups.update(rule.get("groups", []))

    # ADMIN_USER_RULES'dan grupları topla
    for rule in ADMIN_USER_RULES.values():
        groups.update(rule.get("groups", []))

    # EMAIL_DOMAIN_RULES'dan grupları topla
    for rule in EMAIL_DOMAIN_RULES.values():
        groups.update(rule.get("groups", []))

    return list(groups)


def create_required_groups():
    """
    Gerekli grupları oluşturur
    """
    created_count = 0
    for group_name in get_required_groups():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            created_count += 1
            logger.info(f"Grup oluşturuldu: {group_name}")

    if created_count > 0:
        logger.info(f"Toplam {created_count} grup oluşturuldu")

    return created_count


def assign_roles_to_user(user, force=False):
    """
    Kullanıcıya otomatik rol atar

    Args:
        user: CustomUser instance
        force: True ise mevcut rolleri güncellemeden önce siler
    """
    if not user or not user.is_authenticated:
        return

    try:
        # Gerekli grupları oluştur
        create_required_groups()

        # Eğer force=True ise mevcut grupları temizle
        if force:
            user.groups.clear()
            logger.info(f"Kullanıcı {user.username} grupları temizlendi")

        assigned_groups = []
        assigned_custom_role = None
        assigned_user_role = None

        # 1. SuperUser kontrolü
        if user.is_superuser:
            rule = ADMIN_USER_RULES["superuser"]
            for group_name in rule["groups"]:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                assigned_groups.append(group_name)
            assigned_custom_role = rule["custom_role"]
            assigned_user_role = rule.get("user_role")
            logger.info(
                f"SuperUser {user.username} için roller atandı: {assigned_groups}"
            )

        # 2. Staff kontrolü
        elif user.is_staff:
            rule = ADMIN_USER_RULES["staff"]
            for group_name in rule["groups"]:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                assigned_groups.append(group_name)
            assigned_custom_role = rule["custom_role"]
            assigned_user_role = rule.get("user_role")
            logger.info(f"Staff {user.username} için roller atandı: {assigned_groups}")

        # 3. UserType bazlı rol atama
        elif hasattr(user, "user_type") and user.user_type:
            user_type_code = user.user_type.code
            if user_type_code in AUTO_ROLE_RULES:
                rule = AUTO_ROLE_RULES[user_type_code]
                for group_name in rule["groups"]:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)
                    assigned_groups.append(group_name)
                assigned_custom_role = rule["custom_role"]
                assigned_user_role = rule.get("user_role")
                logger.info(
                    f"UserType {user_type_code} için {user.username} kullanıcısına roller atandı: {assigned_groups}"
                )

        # 4. Email domain bazlı rol atama (fallback)
        else:
            email_domain = (
                user.email.split("@")[-1] if user.email and "@" in user.email else None
            )
            if email_domain and email_domain in EMAIL_DOMAIN_RULES:
                rule = EMAIL_DOMAIN_RULES[email_domain]
                for group_name in rule["groups"]:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)
                    assigned_groups.append(group_name)
                assigned_custom_role = rule["custom_role"]
                assigned_user_role = rule.get("user_role")
                logger.info(
                    f"Email domain {email_domain} için {user.username} kullanıcısına roller atandı: {assigned_groups}"
                )

            # Varsayılan rol (hiçbiri uymazsa)
            else:
                default_groups = ["Kullanıcılar"]
                for group_name in default_groups:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)
                    assigned_groups.append(group_name)
                assigned_custom_role = "viewer"
                assigned_user_role = "viewer"
                logger.info(
                    f"Varsayılan rol için {user.username} kullanıcısına roller atandı: {assigned_groups}"
                )

        # CustomUser.role güncelle
        if assigned_custom_role and (force or not user.role):
            user.role = assigned_custom_role
            user.save(update_fields=["role"])
            logger.info(
                f"Kullanıcı {user.username} rolü güncellendi: {assigned_custom_role}"
            )

        return {
            "success": True,
            "assigned_groups": assigned_groups,
            "assigned_role": assigned_custom_role,
            "assigned_user_role": assigned_user_role,
            "user_id": user.id,
            "username": user.username,
        }

    except Exception as e:
        logger.error(f"Kullanıcı {user.username} için rol atama hatası: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "user_id": user.id,
            "username": user.username,
        }


def bulk_assign_roles(users=None, force=False):
    """
    Toplu rol atama

    Args:
        users: Kullanıcı queryset'i, None ise tüm kullanıcılar
        force: Mevcut rolleri sil ve yeniden ata
    """
    if users is None:
        users = User.objects.all()

    results = []
    success_count = 0
    error_count = 0

    logger.info(f"Toplu rol atama başlıyor - {users.count()} kullanıcı")

    for user in users:
        result = assign_roles_to_user(user, force=force)
        results.append(result)

        if result["success"]:
            success_count += 1
        else:
            error_count += 1

    logger.info(
        f"Toplu rol atama tamamlandı - Başarılı: {success_count}, Hata: {error_count}"
    )

    return {
        "total": users.count(),
        "success": success_count,
        "errors": error_count,
        "results": results,
    }


# Signal handlers - Otomatik tetiklenme
@receiver(post_save, sender=User)
def auto_assign_roles_on_user_create(sender, instance, created, **kwargs):
    """
    Kullanıcı oluşturulduğunda otomatik rol atar
    """
    if created:
        assign_roles_to_user(instance)
        logger.info(
            f"Yeni kullanıcı {instance.username} için otomatik rol atama tamamlandı"
        )


@receiver(post_save, sender=User)
def auto_assign_roles_on_user_update(sender, instance, created, **kwargs):
    """
    Kullanıcı güncellendiğinde (user_type değişimi) rol atar
    """
    if not created:
        # Sadece belirli alanlar değişirse rol atamasını tetikle
        if hasattr(instance, "_state") and instance._state.adding is False:
            # user_type, is_staff, is_superuser değişimlerini kontrol et
            if (
                hasattr(instance, "user_type")
                or instance.is_staff
                or instance.is_superuser
            ):
                assign_roles_to_user(instance, force=False)
                logger.info(
                    f"Kullanıcı {instance.username} güncellemesi için rol kontrolü yapıldı"
                )


def get_role_assignment_summary():
    """
    Rol atama durumunun özetini döndürür
    """
    total_users = User.objects.count()
    users_with_groups = User.objects.filter(groups__isnull=False).distinct().count()
    users_without_groups = total_users - users_with_groups

    # Grup istatistikleri
    group_stats = []
    for group in Group.objects.all():
        user_count = User.objects.filter(groups=group).count()
        group_stats.append({"name": group.name, "user_count": user_count})

    return {
        "total_users": total_users,
        "users_with_groups": users_with_groups,
        "users_without_groups": users_without_groups,
        "total_groups": Group.objects.count(),
        "group_stats": group_stats,
        "coverage_percentage": round(
            (users_with_groups / total_users * 100) if total_users > 0 else 0, 2
        ),
    }
