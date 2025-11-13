from __future__ import annotations

from django.db.models import Avg, Count
from django.utils import timezone

from developer_portal.models import APIKeyUsageLog, DeveloperAPIKey


def log_usage(
    *,
    api_key: DeveloperAPIKey,
    path: str,
    method: str,
    response_code: int,
    duration_ms: int,
    client_ip: str | None = None,
    user_agent: str | None = None,
) -> APIKeyUsageLog:
    api_key.mark_used()
    return APIKeyUsageLog.objects.create(
        api_key=api_key,
        path=path[:255],
        method=method.upper()[:8],
        response_code=response_code,
        duration_ms=max(duration_ms, 0),
        client_ip=client_ip,
        user_agent=(user_agent or "")[:255],
    )


def usage_summary(api_key: DeveloperAPIKey, hours: int = 24) -> dict:
    since = timezone.now() - timezone.timedelta(hours=hours)
    queryset = api_key.usage_logs.filter(timestamp__gte=since)
    aggregate = queryset.aggregate(
        count=Count("id"),
        avg_duration=Avg("duration_ms"),
    )
    return {
        "requests": aggregate["count"] or 0,
        "avg_duration_ms": round(aggregate["avg_duration"] or 0, 2),
    }


__all__ = ["log_usage", "usage_summary"]

