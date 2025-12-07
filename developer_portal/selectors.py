from __future__ import annotations

from typing import Iterable

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from developer_portal.models import DeveloperAPIKey, WebhookTestLog

User = get_user_model()


def user_api_keys(user: User) -> QuerySet[DeveloperAPIKey]:
    return DeveloperAPIKey.objects.filter(owner=user).select_related("organization")


def organization_api_keys(organization_id) -> QuerySet[DeveloperAPIKey]:
    return DeveloperAPIKey.objects.filter(organization_id=organization_id)


def active_api_keys_queryset() -> QuerySet[DeveloperAPIKey]:
    return DeveloperAPIKey.objects.filter(status="active")


def api_keys_with_ids(ids: Iterable[str]) -> QuerySet[DeveloperAPIKey]:
    return DeveloperAPIKey.objects.filter(id__in=list(ids))


def user_webhook_logs(user: User) -> QuerySet[WebhookTestLog]:
    return WebhookTestLog.objects.filter(actor=user)


__all__ = [
    "user_api_keys",
    "organization_api_keys",
    "active_api_keys_queryset",
    "api_keys_with_ids",
    "user_webhook_logs",
]
