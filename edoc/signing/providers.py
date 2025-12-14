from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Signer(Protocol):
    def sign(self, data: bytes, *, profile: str = "XAdES-BES") -> bytes:
        ...


@runtime_checkable
class TimestampProvider(Protocol):
    def timestamp(self, data: bytes) -> bytes:
        ...


@dataclass(slots=True)
class DummySigner:
    marker: bytes = b"--SIGNED--"

    def sign(self, data: bytes, *, profile: str = "XAdES-BES") -> bytes:  # type: ignore[override]
        return data + b"|" + self.marker + b"|" + profile.encode()


@dataclass(slots=True)
class DummyTimestampProvider:
    marker: bytes = b"--TIMESTAMP--"

    def timestamp(self, data: bytes) -> bytes:  # type: ignore[override]
        return data + b"|" + self.marker


@dataclass(slots=True)
class HSMSigner:
    """Skeleton for a hardware-backed signer (e.g., smart card/HSM).

    This class is a placeholder. Integrate with vendor SDK to implement .sign().

    Example params:
    - slot: HSM slot/index or reader id
    - cert_label: certificate label/alias
    - pin_env: name of env var holding PIN (avoid hard-coding)
    """

    slot: str | None = None
    cert_label: str | None = None
    pin_env: str | None = None

    def sign(self, data: bytes, *, profile: str = "XAdES-BES") -> bytes:  # type: ignore[override]
        # TODO: Replace with vendor SDK implementation
        # For now, mark as pseudo-signed to enable end-to-end flow in dev.
        marker = f"--HSM-SIGNED[{self.slot or 'default'}:{self.cert_label or 'cert'}]--".encode()
        return data + b"|" + marker + b"|" + profile.encode()


@dataclass(slots=True)
class HttpTSAProvider:
    """Simple HTTP-based TSA client skeleton.

    Configure with endpoint URL and optional auth headers. Implement RFC 3161 or provider-specific
    protocol when integrating for real. For now, it returns a deterministic placeholder.
    """

    endpoint: str
    api_key: str | None = None

    def timestamp(self, data: bytes) -> bytes:  # type: ignore[override]
        # TODO: Implement RFC 3161 request to self.endpoint
        marker = f"--HTTP-TSA[{self.endpoint}]--".encode()
        return data + b"|" + marker
