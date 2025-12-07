# -*- coding: utf-8 -*-
"""
Security Views - Güvenlik Görünümleri
CSRF failure, rate limit ve error handler view'ları
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)


def csrf_failure(request, reason=""):
    """
    CSRF doğrulama başarısız olduğunda gösterilecek view
    """
    logger.warning(
        f"CSRF failure: {reason}",
        extra={
            "ip": _get_client_ip(request),
            "path": request.path,
            "method": request.method,
        },
    )

    if request.accepts("application/json"):
        return JsonResponse(
            {
                "error": "CSRF doğrulama hatası",
                "message": "Güvenlik nedeniyle işleminiz gerçekleştirilemedi. Lütfen sayfayı yenileyip tekrar deneyin.",
                "code": "CSRF_FAILURE",
            },
            status=403,
        )

    return render(request, "security/csrf_failure.html", {"reason": reason}, status=403)


def rate_limit_exceeded(request, exception=None):
    """
    Rate limit aşıldığında gösterilecek view
    """
    logger.warning(
        "Rate limit exceeded",
        extra={
            "ip": _get_client_ip(request),
            "path": request.path,
            "user": (
                request.user.username if request.user.is_authenticated else "anonymous"
            ),
        },
    )

    if request.accepts("application/json"):
        return JsonResponse(
            {
                "error": "Rate limit aşıldı",
                "message": "Çok fazla istek gönderdiniz. Lütfen birkaç dakika bekleyip tekrar deneyin.",
                "code": "RATE_LIMIT_EXCEEDED",
            },
            status=429,
        )

    return render(request, "security/rate_limit.html", status=429)


def security_violation(request, violation_type="unknown"):
    """
    Güvenlik ihlali tespit edildiğinde gösterilecek view
    """
    logger.error(
        f"Security violation detected: {violation_type}",
        extra={
            "ip": _get_client_ip(request),
            "path": request.path,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "user": (
                request.user.username if request.user.is_authenticated else "anonymous"
            ),
        },
    )

    return HttpResponseForbidden(
        "Güvenlik ihlali tespit edildi. Bu olay kaydedilmiştir."
    )


def _get_client_ip(request) -> str:
    """Client IP adresini al"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
