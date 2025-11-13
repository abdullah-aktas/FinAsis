from __future__ import annotations

import hmac
import json
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Dict, Iterable, Mapping, Tuple

import requests
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from developer_portal.models import WebhookTestLog
from common.services import audit_logger

DEFAULT_TIMEOUT = 10
MAX_RESPONSE_BODY = 4000


@dataclass(frozen=True)
class WebhookEventDefinition:
    key: str
    title: str
    summary: str
    sample_payload: Mapping[str, Any]


EVENT_DEFINITIONS: Tuple[WebhookEventDefinition, ...] = (
    WebhookEventDefinition(
        key="invoice.created",
        title=_("Fatura Oluşturuldu"),
        summary=_("Yeni oluşturulan faturalar için tetiklenir."),
        sample_payload={
            "id": "inv_123456",
            "type": "invoice",
            "status": "pending",
            "issued_at": timezone.now().isoformat(),
            "amount": {"currency": "TRY", "total": "1299.90"},
            "customer": {"id": "cust_987", "name": "Örnek Şirket A.Ş."},
        },
    ),
    WebhookEventDefinition(
        key="payment.succeeded",
        title=_("Ödeme Başarılı"),
        summary=_("Tahsilat başarıyla tamamlandığında tetiklenir."),
        sample_payload={
            "id": "pay_47391",
            "type": "payment",
            "status": "succeeded",
            "processed_at": timezone.now().isoformat(),
            "amount": {"currency": "TRY", "total": "599.50"},
            "source": {"method": "credit_card"},
        },
    ),
    WebhookEventDefinition(
        key="audit.alert",
        title=_("Uyumluluk Uyarısı"),
        summary=_("MASAK/KVKK kontrollerinde anomaliler bulunduğunda tetiklenir."),
        sample_payload={
            "id": "audit_8201",
            "type": "compliance",
            "severity": "high",
            "triggered_at": timezone.now().isoformat(),
            "rules": [
                {"code": "MASAK-TRX-01", "description": "Yüksek tutarlı transfer", "score": 0.92},
                {"code": "KVKK-LOG-04", "description": "PII loglama riski", "score": 0.77},
            ],
        },
    ),
)

EVENT_LOOKUP = {definition.key: definition for definition in EVENT_DEFINITIONS}


def available_event_choices() -> Iterable[Tuple[str, str]]:
    return ((definition.key, f"{definition.title}") for definition in EVENT_DEFINITIONS)


def _prepare_payload(event_key: str, payload_override: str | None = None) -> Mapping[str, Any]:
    if payload_override:
        try:
            return json.loads(payload_override)
        except json.JSONDecodeError as exc:
            raise ValueError(_("Geçersiz JSON payload: %(error)s") % {"error": exc}) from exc
    definition = EVENT_LOOKUP.get(event_key)
    if not definition:
        raise ValueError(_("Desteklenmeyen webhook olayı: %(event)s") % {"event": event_key})
    return definition.sample_payload


def _prepare_headers(custom_headers: Mapping[str, Any] | None = None) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "User-Agent": "FinAsis-WebhookTester/1.0",
        "Content-Type": "application/json",
    }
    for key, value in (custom_headers or {}).items():
        headers[str(key)] = str(value)
    return headers


def _parse_custom_headers(raw_headers: str | None) -> Dict[str, str]:
    if not raw_headers:
        return {}
    try:
        parsed = json.loads(raw_headers)
        if not isinstance(parsed, Mapping):
            raise ValueError
        return {str(k): str(v) for k, v in parsed.items()}
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(_("Başlıklar JSON formatında olmalı.")) from exc


def _compute_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()
    return digest


def dispatch_webhook(
    *,
    actor,
    target_url: str,
    event_key: str,
    signature_secret: str | None = None,
    custom_headers_raw: str | None = None,
    payload_override: str | None = None,
) -> WebhookTestLog:
    payload = _prepare_payload(event_key, payload_override)
    headers = _prepare_headers(_parse_custom_headers(custom_headers_raw))

    body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    signature_value = ""
    if signature_secret:
        signature_value = _compute_signature(signature_secret, body_bytes)
        headers["X-Finasis-Signature"] = signature_value
        headers["X-Finasis-Event"] = event_key

    start = time.monotonic()
    response_status: int | None = None
    response_body: str = ""
    error_message: str = ""

    try:
        response = requests.post(
            target_url,
            headers=headers,
            data=body_bytes,
            timeout=DEFAULT_TIMEOUT,
        )
        response_status = response.status_code
        response_body = response.text[:MAX_RESPONSE_BODY]
    except requests.RequestException as exc:
        error_message = str(exc)
    duration_ms = int((time.monotonic() - start) * 1000)

    log_entry = WebhookTestLog.objects.create(
        actor=actor if actor.is_authenticated else None,
        event_type=event_key,
        target_url=target_url,
        request_headers=headers,
        payload=payload,
        signature=signature_value,
        response_status=response_status,
        response_body=response_body,
        duration_ms=duration_ms,
        error=error_message,
    )

    audit_logger.log_security_event(
        action="developer_portal.webhook_test",
        actor=actor,
        resource=f"WebhookTestLog:{log_entry.pk}",
        metadata={
            "event": event_key,
            "target_url": target_url,
            "status": response_status,
            "duration_ms": duration_ms,
            "error": error_message,
        },
        success=not error_message,
    )

    return log_entry


__all__ = ["dispatch_webhook", "available_event_choices", "EVENT_DEFINITIONS"]

