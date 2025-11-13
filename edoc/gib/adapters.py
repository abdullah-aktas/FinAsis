from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Protocol

import requests

from ..shared.config import EdocSettings
from ..shared.logging import get_logger

Status = Literal["PENDING", "ACCEPTED", "REJECTED", "ERROR"]


@dataclass(slots=True)
class SendResult:
    tracking_id: str
    status: Status


class GibAdapter(Protocol):
    def send_invoice(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult: ...
    def send_archive_invoice(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult: ...
    def poll(self, tracking_id: str) -> Status: ...


class StubGibAdapter:
    """Local stub adapter with idempotent state persisted to .edoc_state.

    Matches prior behavior but wrapped as an adapter.
    """

    def __init__(self, state_dir: Optional[str] = None) -> None:
        self.logger = get_logger(__name__)
        base = Path(state_dir or ".edoc_state")
        base.mkdir(parents=True, exist_ok=True)
        self.state_dir = base

    def _status_path(self, tracking_id: str) -> Path:
        return self.state_dir / f"{tracking_id}.json"

    def _send_kind(self, kind: str, idempotency_key: Optional[str] = None) -> SendResult:
        tracking_id = idempotency_key or str(uuid.uuid4())
        p = self._status_path(tracking_id)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            return SendResult(tracking_id=tracking_id, status=data["status"])  # idempotent
        p.write_text(json.dumps({"kind": kind, "status": "PENDING"}), encoding="utf-8")
        self.logger.info(f"{kind} sent; tracking_id={tracking_id}")
        return SendResult(tracking_id=tracking_id, status="PENDING")

    def send_invoice(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult:
        return self._send_kind("invoice", idempotency_key)

    def send_archive_invoice(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult:
        return self._send_kind("archive", idempotency_key)

    def poll(self, tracking_id: str) -> Status:
        p = self._status_path(tracking_id)
        if not p.exists():
            return "ERROR"
        data = json.loads(p.read_text(encoding="utf-8"))
        status: Status = data["status"]
        if status == "PENDING":
            status = "ACCEPTED"
            data["status"] = status
            p.write_text(json.dumps(data), encoding="utf-8")
        return status


class HttpGibAdapter:
    """HTTP adapter for GİB-like endpoints.

    Uses EdocSettings.endpoints to define URL paths. Polling assumes a status endpoint that takes tracking_id.
    """

    def __init__(self, settings: Optional[EdocSettings] = None, session: Optional[requests.Session] = None) -> None:
        self.settings = settings or EdocSettings.from_env()
        self.logger = get_logger(__name__)
        self.session = session or requests.Session()

    def _send(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult:
        ep = self.settings.endpoints
        if not ep or not ep.send_url():
            return SendResult(tracking_id=idempotency_key or str(uuid.uuid4()), status="ERROR")
        headers = {"Content-Type": "application/xml"}
        # Pass idempotency key to upstream if provided (many gateways honor this)
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        try:
            r = self.session.post(ep.send_url(), data=xml_bytes, headers=headers, timeout=15)
            if r.status_code in (200, 202):
                payload = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                tracking = payload.get("tracking_id") or idempotency_key or str(uuid.uuid4())
                status: Status = payload.get("status") or ("PENDING" if r.status_code == 202 else "ACCEPTED")
                return SendResult(tracking_id=tracking, status=status)
            return SendResult(tracking_id=idempotency_key or str(uuid.uuid4()), status="ERROR")
        except Exception as e:  # pragma: no cover - network
            self.logger.error(f"HttpGibAdapter send error: {e}")
            return SendResult(tracking_id=idempotency_key or str(uuid.uuid4()), status="ERROR")

    def send_invoice(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult:
        return self._send(xml_bytes, idempotency_key)

    def send_archive_invoice(self, xml_bytes: bytes, idempotency_key: Optional[str] = None) -> SendResult:
        return self._send(xml_bytes, idempotency_key)

    def poll(self, tracking_id: str) -> Status:
        ep = self.settings.endpoints
        if not ep or not ep.status_url():
            return "ERROR"
        try:
            r = self.session.get(ep.status_url(), params={"tracking_id": tracking_id}, timeout=10)
            if r.status_code == 200:
                payload = r.json()
                return payload.get("status", "ERROR")
            return "ERROR"
        except Exception as e:  # pragma: no cover - network
            self.logger.error(f"HttpGibAdapter poll error: {e}")
            return "ERROR"
