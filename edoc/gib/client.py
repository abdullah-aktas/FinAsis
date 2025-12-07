from __future__ import annotations

import time
import uuid
import os
from typing import Optional

from ..shared.config import EdocSettings
from ..shared.logging import get_logger
from .adapters import GibAdapter, StubGibAdapter, HttpGibAdapter, SendResult, Status


class GibClient:
    """GİB client delegating to adapters.

    Mode selection via environment:
      - EDOC_GIB_MODE=stub (default)
      - EDOC_GIB_MODE=http
    """

    def __init__(
        self,
        settings: Optional[EdocSettings] = None,
        state_dir: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> None:
        self.settings = settings or EdocSettings.from_env()
        self.logger = get_logger(__name__)
        effective_mode = (mode or os.environ.get("EDOC_GIB_MODE") or "stub").lower()
        if effective_mode == "http":
            self.adapter: GibAdapter = HttpGibAdapter(self.settings)
        else:
            # default to stub and preserve state_dir behavior
            self.adapter = StubGibAdapter(state_dir)

    def send_with_retry(
        self, xml_bytes: bytes, idempotency_key: Optional[str] = None
    ) -> SendResult:
        rp = self.settings.retry
        attempt = 0
        last = None
        delay = rp.backoff_factor
        while attempt < rp.max_attempts:
            attempt += 1
            res = self.send_invoice(xml_bytes, idempotency_key=idempotency_key)
            last = res
            if res.status != "ERROR":
                return res
            time.sleep(min(delay, rp.max_backoff_seconds))
            delay *= 2
        return last or SendResult(
            tracking_id=idempotency_key or str(uuid.uuid4()), status="ERROR"
        )

    # --- Delegated public API for backwards compatibility ---
    def send_invoice(
        self, xml_bytes: bytes, idempotency_key: Optional[str] = None
    ) -> SendResult:
        return self.adapter.send_invoice(xml_bytes, idempotency_key)

    def send_archive_invoice(
        self, xml_bytes: bytes, idempotency_key: Optional[str] = None
    ) -> SendResult:
        return self.adapter.send_archive_invoice(xml_bytes, idempotency_key)

    def poll(self, tracking_id: str) -> Status:
        return self.adapter.poll(tracking_id)
