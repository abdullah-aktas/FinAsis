from __future__ import annotations

import time

from django.utils.deprecation import MiddlewareMixin
from prometheus_client import Counter, Histogram, REGISTRY

from developer_portal.models import DeveloperAPIKey
from developer_portal.services import usage_service


def _register_metric(
    name: str,
    constructor,
    documentation: str,
    labelnames: tuple[str, ...],
):
    existing = REGISTRY._names_to_collectors.get(name)
    if existing is not None:
        return existing
    return constructor(
        name,
        documentation,
        labelnames=labelnames,
        registry=REGISTRY,
    )


DEVELOPER_API_CALLS = _register_metric(
    "finasis_api_calls_total",
    Counter,
    "Developer portal API anahtarı ile yapılan HTTP çağrıları",
    ("plan", "status"),
)

DEVELOPER_API_LATENCY = _register_metric(
    "finasis_api_call_latency_seconds",
    Histogram,
    "Developer portal API çağrılarının süreleri (saniye)",
    ("plan",),
)


class APIUsageLoggingMiddleware(MiddlewareMixin):
    """
    DRF üzerinden gelen ve API anahtarı ile doğrulanan istekleri kaydeder.

    - Süre hesabı için monotonic zaman kullanır.
    - İsteklerde hata olsa bile (response üretildiği sürece) log kaydı tutulur.
    """

    timer_attr = "_developer_api_timer"

    def process_request(self, request) -> None:
        setattr(request, self.timer_attr, time.monotonic())

    def process_response(self, request, response):
        api_key = getattr(request, "_developer_api_key", None)
        if isinstance(api_key, DeveloperAPIKey):
            started = getattr(request, self.timer_attr, None)
            duration_ms = 0
            if isinstance(started, (int, float)):
                duration_ms = int((time.monotonic() - started) * 1000)

            if not getattr(request, "_developer_api_logged", False):
                usage_service.log_usage(
                    api_key=api_key,
                    path=request.path,
                    method=request.method,
                    response_code=getattr(response, "status_code", 0),
                    duration_ms=max(duration_ms, 0),
                    client_ip=self._get_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )
                self._observe_metrics(
                    api_key=api_key,
                    status_code=getattr(response, "status_code", 0),
                    duration_ms=duration_ms,
                )
                setattr(request, "_developer_api_logged", True)
        return response

    def process_exception(self, request, exception):
        # Hata durumunda DRF response üretmeden önce tetikleneceği için manuel loglama
        api_key = getattr(request, "_developer_api_key", None)
        if isinstance(api_key, DeveloperAPIKey):
            started = getattr(request, self.timer_attr, None)
            duration_ms = 0
            if isinstance(started, (int, float)):
                duration_ms = int((time.monotonic() - started) * 1000)

            if not getattr(request, "_developer_api_logged", False):
                usage_service.log_usage(
                    api_key=api_key,
                    path=request.path,
                    method=request.method,
                    response_code=500,
                    duration_ms=max(duration_ms, 0),
                    client_ip=self._get_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )
                self._observe_metrics(
                    api_key=api_key,
                    status_code=500,
                    duration_ms=duration_ms,
                )
                setattr(request, "_developer_api_logged", True)
        return None

    @staticmethod
    def _get_ip(request) -> str | None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def _observe_metrics(*, api_key: DeveloperAPIKey, status_code: int, duration_ms: int) -> None:
        plan = (api_key.rate_limit_plan or "unknown").lower()
        DEVELOPER_API_CALLS.labels(plan=plan, status=str(status_code)).inc()
        if duration_ms >= 0:
            DEVELOPER_API_LATENCY.labels(plan=plan).observe(max(duration_ms, 0) / 1000.0)


__all__ = ["APIUsageLoggingMiddleware"]

