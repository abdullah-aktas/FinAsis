from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditEvent

# If TRACKED_MODELS empty => track only apps in ALLOWED_APP_LABELS
TRACKED_MODELS = []  # optional explicit model name allow-list
ALLOWED_APP_LABELS = {"finance", "tenancy", "virtual_company", "accounts", "accounting"}


def _audit_ready():
    """Return True if the audit table exists (i.e., after migrations)."""
    try:
        return "audit_auditevent" in connection.introspection.table_names()
    except Exception:
        return False


def _should_track(sender):
    if sender is AuditEvent:
        return False
    app_label = getattr(sender._meta, "app_label", None)
    if TRACKED_MODELS:
        return sender.__name__ in TRACKED_MODELS
    return app_label in ALLOWED_APP_LABELS


@receiver(post_save)
def create_update_audit(sender, instance, created, **kwargs):
    if not _audit_ready() or not _should_track(sender):
        return
    try:
        AuditEvent.objects.create(
            action="create" if created else "update",
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(getattr(instance, "pk", "")),
        )
    except Exception:
        # Fail silent in audit layer; never break core flow
        pass


@receiver(post_delete)
def delete_audit(sender, instance, **kwargs):
    if not _audit_ready() or not _should_track(sender):
        return
    try:
        AuditEvent.objects.create(
            action="delete",
            content_type=ContentType.objects.get_for_model(sender),
            object_id=str(getattr(instance, "pk", "")),
        )
    except Exception:
        pass
