"""
Site Health Check ve Monitoring Views
finasis.com.tr için kapsamlı sağlık kontrolü
"""

import time
import logging
from datetime import timedelta
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check_simple(request):
    """
    Basit health check endpoint - Cloud Run ve monitoring araçları için
    Public erişilebilir, authentication gerektirmez
    """
    try:
        # Database kontrolü
        db_ok = False
        db_time_ms = 0
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                db_ok = result and result[0] == 1
            db_time_ms = int((time.time() - start_time) * 1000)
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_ok = False

        # Cache kontrolü
        cache_ok = False
        try:
            cache.set("health_check", "ok", timeout=10)
            cache_ok = cache.get("health_check") == "ok"
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            cache_ok = False

        # Genel durum
        overall_status = "healthy" if (db_ok and cache_ok) else "unhealthy"
        http_status = (
            status.HTTP_200_OK
            if overall_status == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        response_data = {
            "status": overall_status,
            "timestamp": timezone.now().isoformat(),
            "checks": {
                "database": {
                    "status": "ok" if db_ok else "failed",
                    "response_time_ms": db_time_ms,
                },
                "cache": {
                    "status": "ok" if cache_ok else "failed",
                },
            },
            "version": getattr(settings, "APP_VERSION", "unknown"),
        }

        return JsonResponse(response_data, status=http_status)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse(
            {
                "status": "error",
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """
    Detaylı health check endpoint - Sistem durumu için kapsamlı bilgi
    Public erişilebilir, authentication gerektirmez
    """
    try:
        checks = {}
        overall_healthy = True

        # 1. Database Kontrolü
        db_start = time.time()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                db_ok = result and result[0] == 1

                # Database bilgileri
                if connection.vendor == "postgresql":
                    cursor.execute("SELECT version()")
                    db_version = cursor.fetchone()[0]
                else:
                    db_version = connection.vendor

                # Connection pool bilgileri
                cursor.execute(
                    "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                active_connections = (
                    cursor.fetchone()[0] if connection.vendor == "postgresql" else None
                )
        except Exception as e:
            db_ok = False
            db_version = None
            active_connections = None
            logger.error(f"Database check failed: {e}")

        db_time_ms = int((time.time() - db_start) * 1000)
        checks["database"] = {
            "status": "ok" if db_ok else "failed",
            "response_time_ms": db_time_ms,
            "version": db_version,
            "active_connections": active_connections,
            "vendor": connection.vendor,
        }
        if not db_ok:
            overall_healthy = False

        # 2. Cache Kontrolü
        cache_start = time.time()
        try:
            cache.set("health_check", "ok", timeout=10)
            cache_ok = cache.get("health_check") == "ok"
            cache_time_ms = int((time.time() - cache_start) * 1000)
        except Exception as e:
            cache_ok = False
            cache_time_ms = 0
            logger.error(f"Cache check failed: {e}")

        checks["cache"] = {
            "status": "ok" if cache_ok else "failed",
            "response_time_ms": cache_time_ms,
        }
        if not cache_ok:
            overall_healthy = False

        # 3. Static Files Kontrolü
        try:
            static_ok = True  # Static dosyalar genelde sorunsuz
        except Exception as e:
            static_ok = False
            logger.error(f"Static files check failed: {e}")

        checks["static_files"] = {
            "status": "ok" if static_ok else "failed",
        }

        # 4. Settings Kontrolü
        settings_check = {
            "debug": settings.DEBUG,
            "allowed_hosts": settings.ALLOWED_HOSTS,
            "database_engine": settings.DATABASES["default"]["ENGINE"],
        }

        # 5. Son Hatalar (son 5 dakika)
        try:
            from common.error_tracking import ErrorLog

            recent_errors = ErrorLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).count()
        except Exception:
            recent_errors = None

        # 6. Aktif Kullanıcı Sayısı (son 15 dakika)
        try:
            from django.contrib.sessions.models import Session

            active_sessions = Session.objects.filter(
                expire_date__gte=timezone.now()
            ).count()
        except Exception:
            active_sessions = None

        response_data = {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": timezone.now().isoformat(),
            "checks": checks,
            "system_info": {
                "settings": settings_check,
                "recent_errors_5min": recent_errors,
                "active_sessions": active_sessions,
                "version": getattr(settings, "APP_VERSION", "unknown"),
            },
        }

        http_status = (
            status.HTTP_200_OK
            if overall_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return JsonResponse(response_data, status=http_status)

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JsonResponse(
            {
                "status": "error",
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def site_status(request):
    """
    Site durum sayfası - finasis.com.tr için genel durum bilgisi
    Public erişilebilir
    """
    try:
        # Temel kontroller
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_ok = True
        except Exception:
            pass

        cache_ok = False
        try:
            cache.set("status_check", "ok", timeout=5)
            cache_ok = cache.get("status_check") == "ok"
        except Exception:
            pass

        # Modül durumları
        modules = [
            {
                "name": "Muhasebe",
                "code": "accounting",
                "status": "operational" if db_ok else "degraded",
            },
            {
                "name": "Finans",
                "code": "finance",
                "status": "operational" if db_ok else "degraded",
            },
            {
                "name": "AI Asistan",
                "code": "ai_assistant",
                "status": "operational",
            },
            {
                "name": "Eğitim",
                "code": "education",
                "status": "operational" if db_ok else "degraded",
            },
            {
                "name": "Blockchain",
                "code": "blockchain",
                "status": "operational" if db_ok else "degraded",
            },
        ]

        overall_status = "operational" if (db_ok and cache_ok) else "degraded"

        response_data = {
            "status": overall_status,
            "timestamp": timezone.now().isoformat(),
            "modules": modules,
            "incidents": [],  # Gelecekte incident tracking eklenebilir
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Site status check failed: {e}")
        return JsonResponse(
            {
                "status": "error",
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
