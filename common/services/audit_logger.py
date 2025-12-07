from __future__ import annotations

import logging
from typing import Any, Mapping

from django.contrib.auth import get_user_model
from django.utils import timezone

from security.models import SecurityAuditLog

User = get_user_model()

logger = logging.getLogger(__name__)


def _extract_ip(request) -> str | None:
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _extract_user_agent(request) -> str | None:
    if request is None:
        return None
    return request.META.get("HTTP_USER_AGENT")


def log_security_event(
    *,
    action: str,
    actor: User | None = None,
    request=None,
    resource: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    success: bool = True,
) -> SecurityAuditLog:
    """
    Platform genelinde güvenlik kritik aksiyonları kayıt altına alır.

    Args:
        action: `module.action` formatında kısa kod.
        actor: İşlemi yapan kullanıcı (opsiyonel).
        request: Django request objesi (IP ve user agent için).
        resource: Etkilenen kaynak (örn. `DeveloperAPIKey:uuid`).
        metadata: Ek bağlam (dict).
        success: İşlem sonucunun başarı durumu.
    """

    if actor is None and request is not None and request.user.is_authenticated:
        actor = request.user

    user_agent = _extract_user_agent(request) or ""
    entry = SecurityAuditLog.objects.create(
        actor=actor,
        action=action,
        resource=resource or "",
        ip_address=_extract_ip(request),
        user_agent=user_agent,
        metadata=dict(metadata or {}),
        success=success,
        occurred_at=timezone.now(),
    )

    logger.info(
        "security.audit",
        extra={
            "audit_action": action,
            "audit_actor": getattr(actor, "pk", None),
            "audit_resource": resource,
            "audit_success": success,
            "audit_metadata": metadata,
        },
    )

    return entry


__all__ = ["log_security_event"]
