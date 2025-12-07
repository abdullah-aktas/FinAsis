from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.services.role_profiles import ensure_role_profile

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_role_profile_on_create(sender, instance, created, **kwargs):
    """
    After a CustomUser is created or updated, make sure the RoleBasedUserProfile
    matches the most recent role assignment.
    """
    if instance is None:
        return

    ensure_role_profile(instance)
