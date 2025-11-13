from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Iterable, Tuple
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class APIKeyStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    ROTATED = "rotated", _("Rotated")
    REVOKED = "revoked", _("Revoked")


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def _generate_prefix(length: int = 8) -> str:
    return secrets.token_hex(length // 2).upper()


class DeveloperAPIKey(models.Model):
    """API anahtarlarının metadata kaydı. Tam key yalnızca oluşturma anında gösterilir."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="developer_api_keys",
    )
    organization = models.ForeignKey(
        "accounting.Company",
        on_delete=models.CASCADE,
        related_name="developer_api_keys",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    prefix = models.CharField(max_length=12, db_index=True, editable=False)
    hashed_key = models.CharField(max_length=128, editable=False)
    rate_limit_plan = models.CharField(max_length=32, default="standard")
    allowed_ips = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=APIKeyStatus.choices, default=APIKeyStatus.ACTIVE
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Developer API Key")
        verbose_name_plural = _("Developer API Keys")
        indexes = [
            models.Index(fields=("prefix", "status")),
            models.Index(fields=("organization", "status")),
        ]
        permissions = [
            ("manage_keys", _("Developer portal API anahtarlarını yönetebilir")),
        ]

    def __str__(self) -> str:  # pragma: no cover - admin representation
        return f"{self.name} · {self.masked_key}"

    @property
    def masked_key(self) -> str:
        return f"{self.prefix}…"

    @property
    def is_active(self) -> bool:
        return self.status == APIKeyStatus.ACTIVE and not self.is_expired

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at < timezone.now())

    def mark_used(self) -> None:
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])

    @classmethod
    def create_with_secret(
        cls,
        *,
        owner,
        organization,
        name: str,
        description: str = "",
        rate_limit_plan: str = "standard",
        allowed_ips: Iterable[str] | None = None,
        expires_at=None,
    ) -> Tuple["DeveloperAPIKey", str]:
        raw_secret = secrets.token_urlsafe(32)
        prefix = _generate_prefix()
        full_key = f"{prefix}.{raw_secret}"

        instance = cls.objects.create(
            owner=owner,
            organization=organization,
            name=name,
            description=description,
            prefix=prefix,
            hashed_key=_hash_key(full_key),
            rate_limit_plan=rate_limit_plan,
            allowed_ips=list(allowed_ips or []),
            expires_at=expires_at,
        )
        return instance, full_key

    def rotate(self) -> Tuple["DeveloperAPIKey", str]:
        """Var olan anahtarı geçersiz kılar ve yeni bir key döner."""
        self.status = APIKeyStatus.ROTATED
        self.save(update_fields=["status", "updated_at"])
        rotated, secret = self.create_with_secret(
            owner=self.owner,
            organization=self.organization,
            name=f"{self.name} (rotated)",
            description=self.description,
            rate_limit_plan=self.rate_limit_plan,
            allowed_ips=self.allowed_ips,
            expires_at=self.expires_at,
        )
        return rotated, secret

    def revoke(self) -> None:
        self.status = APIKeyStatus.REVOKED
        self.save(update_fields=["status", "updated_at"])

    @staticmethod
    def hash_raw_key(raw_key: str) -> str:
        return _hash_key(raw_key)


class APIKeyUsageLog(models.Model):
    api_key = models.ForeignKey(
        DeveloperAPIKey, on_delete=models.CASCADE, related_name="usage_logs"
    )
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=8)
    response_code = models.IntegerField()
    duration_ms = models.IntegerField()
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = _("API Key Usage Log")
        verbose_name_plural = _("API Key Usage Logs")
        indexes = [
            models.Index(fields=("api_key", "timestamp")),
            models.Index(fields=("api_key", "response_code")),
        ]


class DeveloperPortalAuditLog(models.Model):
    """Portal içindeki önemli aksiyonlar için audit trail."""

    id = models.BigAutoField(primary_key=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="developer_portal_audit_logs",
    )
    api_key = models.ForeignKey(
        DeveloperAPIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Developer Portal Audit Log")
        verbose_name_plural = _("Developer Portal Audit Logs")


class WebhookTestLog(models.Model):
    """Webhook test konsolundan gönderilen log kayıtları."""

    EVENT_TYPE_MAX_LENGTH = 64

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="developer_webhook_tests",
    )
    event_type = models.CharField(max_length=EVENT_TYPE_MAX_LENGTH)
    target_url = models.URLField()
    request_headers = models.JSONField(default=dict, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    signature = models.CharField(max_length=128, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Webhook Test Logu")
        verbose_name_plural = _("Webhook Test Logları")
        indexes = [
            models.Index(fields=("event_type", "created_at")),
            models.Index(fields=("actor", "created_at")),
        ]

    def __str__(self) -> str:  # pragma: no cover - admin representation
        return f"{self.event_type} → {self.target_url} ({self.response_status or 'error'})"

