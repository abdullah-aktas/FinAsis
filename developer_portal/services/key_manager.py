from __future__ import annotations

from typing import Iterable, Tuple

from django.utils import timezone

from developer_portal.models import (
    APIKeyStatus,
    DeveloperAPIKey,
    DeveloperPortalAuditLog,
)


def create_api_key(
    *,
    owner,
    organization,
    name: str,
    description: str = "",
    rate_limit_plan: str = "standard",
    allowed_ips: Iterable[str] | None = None,
    expires_at=None,
    actor=None,
) -> Tuple[DeveloperAPIKey, str]:
    key, raw_secret = DeveloperAPIKey.create_with_secret(
        owner=owner,
        organization=organization,
        name=name,
        description=description,
        rate_limit_plan=rate_limit_plan,
        allowed_ips=allowed_ips,
        expires_at=expires_at,
    )
    DeveloperPortalAuditLog.objects.create(
        actor=actor or owner,
        api_key=key,
        action="create_key",
        metadata={
            "rate_limit_plan": rate_limit_plan,
            "allowed_ips": list(allowed_ips or []),
            "expires_at": expires_at.isoformat() if expires_at else None,
        },
    )
    return key, raw_secret


def rotate_api_key(
    key: DeveloperAPIKey,
    *,
    actor=None,
) -> Tuple[DeveloperAPIKey, str]:
    new_key, raw_secret = key.rotate()
    DeveloperPortalAuditLog.objects.bulk_create(
        [
            DeveloperPortalAuditLog(
                actor=actor,
                api_key=key,
                action="rotate_key_old",
                metadata={"rotated_at": timezone.now().isoformat()},
            ),
            DeveloperPortalAuditLog(
                actor=actor,
                api_key=new_key,
                action="rotate_key_new",
                metadata={"from_key": str(key.id)},
            ),
        ]
    )
    return new_key, raw_secret


def revoke_api_key(
    key: DeveloperAPIKey, *, actor=None, reason: str | None = None
) -> None:
    key.revoke()
    DeveloperPortalAuditLog.objects.create(
        actor=actor,
        api_key=key,
        action="revoke_key",
        metadata={"reason": reason},
    )


def mask_full_key(full_key: str) -> str:
    """UI gösterimi için anahtarın maskeli halini döndürür."""
    if not full_key or "." not in full_key:
        return full_key
    prefix, *_ = full_key.split(".")
    return f"{prefix}…{full_key[-4:]}"


def validate_raw_key(raw_key: str) -> bool:
    return bool(raw_key and len(raw_key) >= 16)


def extract_prefix(raw_key: str) -> str:
    if not raw_key or "." not in raw_key:
        raise ValueError("API key formatı hatalı.")
    prefix, *_ = raw_key.split(".")
    return prefix


def verify_raw_key(raw_key: str) -> DeveloperAPIKey | None:
    """Header’den gelen key’i doğrular."""
    if not validate_raw_key(raw_key):
        return None
    prefix = extract_prefix(raw_key)
    try:
        candidate = DeveloperAPIKey.objects.get(
            prefix=prefix, status=APIKeyStatus.ACTIVE
        )
    except DeveloperAPIKey.DoesNotExist:
        return None
    if candidate.hash_raw_key(raw_key) != candidate.hashed_key:
        return None
    return candidate


__all__ = [
    "create_api_key",
    "rotate_api_key",
    "revoke_api_key",
    "mask_full_key",
    "validate_raw_key",
    "extract_prefix",
    "verify_raw_key",
]
