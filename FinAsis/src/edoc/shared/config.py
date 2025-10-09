from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class GibEndpoints:
    base_url: str
    send_path: str = "/send"
    status_path: str = "/status"

    def send_url(self) -> str:
        return self.base_url.rstrip("/") + self.send_path

    def status_url(self) -> str:
        return self.base_url.rstrip("/") + self.status_path


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_factor: float = 0.7
    max_backoff_seconds: float = 8.0


@dataclass(slots=True)
class EdocSettings:
    profile_id: str = "TICARIFATURA"
    customization_id: str = "TR1.2"
    schemas_dir: Optional[str] = None
    endpoints: Optional[GibEndpoints] = None
    retry: RetryPolicy = field(default_factory=RetryPolicy)

    @staticmethod
    def from_env() -> "EdocSettings":
        schemas_dir = os.environ.get("EDOC_SCHEMAS_DIR")
        profile = os.environ.get("EDOC_PROFILE_ID", "TICARIFATURA")
        customization = os.environ.get("EDOC_CUSTOMIZATION_ID", "TR1.2")
        base_url = os.environ.get("GIB_TEST_BASE_URL")
        endpoints = GibEndpoints(base_url) if base_url else None
        max_attempts = int(os.environ.get("EDOC_RETRY_MAX", "3"))
        backoff = float(os.environ.get("EDOC_RETRY_BACKOFF", "0.7"))
        max_backoff = float(os.environ.get("EDOC_RETRY_MAX_BACKOFF", "8.0"))
        settings = EdocSettings(
            profile_id=profile,
            customization_id=customization,
            schemas_dir=schemas_dir,
            endpoints=endpoints,
            retry=RetryPolicy(max_attempts=max_attempts, backoff_factor=backoff, max_backoff_seconds=max_backoff),
        )
        return settings
