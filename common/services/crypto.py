from __future__ import annotations

import functools
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _get_key_from_settings() -> bytes:
    key = getattr(settings, "DATA_ENCRYPTION_KEY", None) or settings.ENV(
        "DATA_ENCRYPTION_KEY", None
    )
    if not key:
        raise ImproperlyConfigured(
            "DATA_ENCRYPTION_KEY belirtilmemiş. Lütfen 32 baytlık bir Fernet anahtarını environment değişkeni olarak tanımlayın."
        )
    return key.encode() if isinstance(key, str) else key


@functools.lru_cache(maxsize=2)
def get_fernet(key: Optional[bytes] = None) -> Fernet:
    material = key or _get_key_from_settings()
    if isinstance(material, str):
        material = material.encode()
    return Fernet(material)


def encrypt(value: str | bytes, *, key: Optional[bytes] = None) -> str:
    fernet = get_fernet(key)
    data = value.encode() if isinstance(value, str) else value
    return fernet.encrypt(data).decode()


def decrypt(
    token: str | bytes,
    *,
    key: Optional[bytes] = None,
    fallback_key: Optional[bytes] = None,
) -> str:
    fernet = get_fernet(key)
    token_bytes = token.encode() if isinstance(token, str) else token
    try:
        return fernet.decrypt(token_bytes).decode()
    except InvalidToken:
        fallback_material = (
            fallback_key
            or getattr(settings, "DATA_ENCRYPTION_FALLBACK_KEY", None)
            or settings.ENV("DATA_ENCRYPTION_FALLBACK_KEY", None)
        )
        if fallback_material:
            fallback = get_fernet(
                fallback_material
                if isinstance(fallback_material, bytes)
                else fallback_material.encode()
            )
            return fallback.decrypt(token_bytes).decode()
        raise


__all__ = ["encrypt", "decrypt", "get_fernet"]
