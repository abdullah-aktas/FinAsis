from __future__ import annotations

from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.role_models import RoleBasedUserProfile, UserRole
from common.role_utils import get_user_role

User = get_user_model()


ROLE_ALIASES = {
    'superuser': 'super_admin',
    'super_admin': 'super_admin',
    'system_admin': 'admin',
    'company_owner': 'kobi_owner',
    'business_owner': 'kobi_owner',
    'kobi_owner': 'kobi_owner',
    'employee': 'kobi_employee',
    'kobi_staff': 'kobi_employee',
    'staff': 'kobi_employee',
    'finance_manager': 'finance_manager',
    'financial_manager': 'finance_manager',
    'accountant': 'accountant',
    'advisor': 'financial_advisor',
    'financial_advisor': 'financial_advisor',
    'auditor': 'auditor',
    'teacher': 'teacher',
    'student': 'student',
    'player': 'player',
    'viewer': 'viewer',
    'guest': 'viewer',
}


def _resolve_role_code(user) -> str:
    """
    Determine the most suitable UserRole code for the given user.
    Priority:
        1. Explicit user_type code (with alias fallback)
        2. CustomUser.role (with alias fallback)
        3. Superuser/admin flags
        4. Default viewer
    """
    if getattr(user, "is_superuser", False):
        return "super_admin"

    # Prefer user_type if present
    user_type_code: Optional[str] = None
    if hasattr(user, "user_type") and user.user_type:
        user_type_code = getattr(user.user_type, "code", None)

    if user_type_code:
        normalized = ROLE_ALIASES.get(user_type_code, user_type_code)
        if UserRole.objects.filter(name=normalized).exists():
            return normalized

    # Next, rely on the legacy role resolution helper
    legacy_role = get_user_role(user) or getattr(user, "role", None)
    if legacy_role:
        normalized = ROLE_ALIASES.get(legacy_role, legacy_role)
        if UserRole.objects.filter(name=normalized).exists():
            return normalized

    # Staff users without explicit mapping should fall back to admin
    if getattr(user, "is_staff", False):
        if UserRole.objects.filter(name="admin").exists():
            return "admin"

    # Fallback
    return "viewer"


@transaction.atomic
def ensure_role_profile(user, *, explicit_role: Optional[str] = None) -> Tuple[RoleBasedUserProfile, bool]:
    """
    Guarantee that the given user has a RoleBasedUserProfile with a valid UserRole assignment.

    Returns:
        (profile, created) tuple where `created` indicates whether a new profile was generated.
    """
    if user is None:
        raise ValueError("User must be provided to ensure_role_profile.")

    # Determine role code and fetch UserRole instance
    role_code = explicit_role or _resolve_role_code(user)
    role = UserRole.objects.filter(name=role_code).first()
    if role is None:
        role = UserRole.objects.filter(name="viewer").first()

    if role is None:
        # Auto-create a minimal 'viewer' role to avoid hard test dependency on seed commands
        try:
            role = UserRole.objects.create(
                name="viewer",
                display_name="Görüntüleyici",
                description="Varsayılan görüntüleyici rolü (otomatik).",
                is_active=True,
                hierarchy_level=10,
            )
        except Exception:
            raise UserRole.DoesNotExist(
                "No default UserRole found and could not auto-create 'viewer'. Run `python manage.py create_default_roles_and_plans`."
            )

    profile, created = RoleBasedUserProfile.objects.select_for_update().get_or_create(
        user=user,
        defaults={
            "role": role,
            "language": getattr(user, "preferred_language", "tr"),
            "timezone": "Europe/Istanbul",
        },
    )

    if not created and profile.role_id != role.id:
        profile.role = role
        profile.save(update_fields=["role", "updated_at"])

    return profile, created


def backfill_role_profiles():
    """
    Iterate over every user and make sure role profiles exist.
    Returns summary dict for logging purposes.
    """
    created = 0
    updated = 0
    errors = 0

    for user in User.objects.all().select_related("user_type"):
        try:
            profile, was_created = ensure_role_profile(user)
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception:
            errors += 1

    return {
        "created": created,
        "updated": updated,
        "errors": errors,
    }

