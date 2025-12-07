# -*- coding: utf-8 -*-
"""
Context Processors
Template'lerde global olarak kullanılacak değişkenler
"""

from copy import deepcopy

from django.conf import settings
from django.templatetags.static import static
from django.utils import timezone

from .permissions import (
    get_user_role_category,
    get_user_role_info,
    get_user_accessible_apps,
)


BRAND_IDENTITY = {
    "name": "FinAsis",
    "tagline": "Yerel AI Finans Platformu",
    "tagline_short": "Yerel AI Finans",
    "description": (
        "Yapay zeka destekli finansal yönetim, eğitim ve e-dönüşüm süreçlerini "
        "tek ekosistemde birleştiren yerli ve güvenli platform."
    ),
    "values": [
        {"icon": "shield-check", "label": "KVKK ve ISO 27001 Uyumlu"},
        {"icon": "lock", "label": "256-bit SSL ve veri şifreleme"},
        {"icon": "rocket-takeoff", "label": "5 Dakikada aktif kullanım"},
    ],
    "colors": {
        "primary": "#0AAE94",
        "primary_strong": "#008E7A",
        "accent": "#FFB300",
        "accent_strong": "#FF8F00",
        "ink": "#0D3B66",
        "surface": "#FFFFFF",
        "surface_alt": "#F4FAF8",
    },
    "version": {
        "label": "BETA v2.0",
        "number": "2.1.0",
        "status": "beta",
    },
    "support": {
        "email": "destek@finasis.com",
        "phone": "+90 850 000 00 00",
        "hours": "Hafta içi 09:00 - 18:00",
        "address": "İstanbul, Türkiye",
        "slack_channel": "https://finasis.slack.com/support",
    },
    "assets": {
        "logo_full": static("common/FinAsis_logo.png"),
        "logo_mark": static("common/finasis_logo-192.png"),
        "favicon": static("common/favicon.ico"),
    },
    "social": [
        {
            "name": "LinkedIn",
            "icon": "linkedin",
            "url": "https://www.linkedin.com/in/finasis/",
            "class": "linkedin",
        },
        {
            "name": "Instagram",
            "icon": "instagram",
            "url": "https://www.instagram.com/finasisapp/",
            "class": "instagram",
        },
        {
            "name": "X",
            "icon": "twitter-x",
            "url": "https://x.com/finasis",
            "class": "twitter",
        },
        {
            "name": "YouTube",
            "icon": "youtube",
            "url": "https://www.youtube.com/@FinAsisApp",
            "class": "youtube",
        },
    ],
    "cta": {
        "primary": {
            "label": "Ücretsiz Başlayın",
            "url_name": "accounts:register",
            "icon": "rocket-takeoff",
        },
        "secondary": {
            "label": "Demo Talep Et",
            "url_name": "contact",
            "icon": "calendar-event",
        },
    },
}


def rbac_context(request):
    """
    RBAC ile ilgili context değişkenleri
    """
    if not request.user.is_authenticated:
        return {}

    user_role = get_user_role_category(request.user)
    role_info = get_user_role_info(request.user)
    accessible_apps = get_user_accessible_apps(request.user)

    return {
        "user_role": user_role,
        "user_role_info": role_info,
        "user_accessible_apps": accessible_apps,
        "is_superadmin": user_role == "superadmin",
        "is_company_owner": user_role
        in ["superadmin", "system_admin", "company_owner", "kobi_owner"],
        "has_finance_access": user_role
        in [
            "superadmin",
            "system_admin",
            "company_owner",
            "kobi_owner",
            "finance_manager",
            "accountant",
            "kobi_employee",
        ],
        "has_education_access": "education" in accessible_apps,
        "has_games_access": "games" in accessible_apps,
        "has_management_access": "management" in accessible_apps,
    }


def user_roles(request):
    """
    Backward compatibility için eski context processor
    """
    if not request.user.is_authenticated:
        return {
            "user_groups": [],
            "is_kobi_owner": False,
            "is_accountant": False,
            "is_teacher": False,
            "is_student": False,
        }

    user_groups = list(request.user.groups.values_list("name", flat=True))
    user_role = get_user_role_category(request.user)

    return {
        "user_groups": user_groups,
        "is_kobi_owner": user_role in ["superadmin", "company_owner", "kobi_owner"],
        "is_accountant": user_role in ["superadmin", "finance_manager", "accountant"],
        "is_teacher": user_role == "teacher",
        "is_student": user_role == "student",
        "is_finance_manager": user_role
        in ["superadmin", "company_owner", "kobi_owner", "finance_manager"],
        "is_system_admin": user_role in ["superadmin", "system_admin"],
    }


def platform_context(request):
    """
    Platform genelinde kullanılan değişkenler
    (Mevcut, dokunmuyoruz)
    """
    languages = getattr(settings, "LANGUAGES", [])
    current_language = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    return {
        "platform_name": "FinAsis",
        "platform_version": "2.1.0",
        "support_email": "destek@finasis.com",
        "available_languages": languages,
        "current_language": current_language,
    }


def brand_identity(request):
    """Marka kimliği bilgilerini template'lere taşır."""
    brand_data = deepcopy(BRAND_IDENTITY)
    brand_data["current_year"] = timezone.now().year
    return {
        "brand_identity": brand_data,
    }
