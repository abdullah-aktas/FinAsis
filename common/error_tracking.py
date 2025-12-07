"""
Beta Error Tracking & Alert System
Canlıdaki hataları yakalar ve admin'e bildirir
"""
import logging
import traceback
import sys
from typing import Optional, Dict, Any
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

logger = logging.getLogger(__name__)

User = get_user_model()


class ErrorLog(models.Model):
    """Sistem hatalarını kaydet"""

    SEVERITY_CHOICES = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    STATUS_CHOICES = [
        ("NEW", "Yeni"),
        ("INVESTIGATING", "İnceleniyor"),
        ("RESOLVED", "Çözüldü"),
        ("IGNORED", "Yok Sayıldı"),
    ]

    # Error details
    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES, default="ERROR"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    error_type = models.CharField(max_length=200, verbose_name="Hata Tipi")
    error_message = models.TextField(verbose_name="Hata Mesajı")
    traceback = models.TextField(blank=True, verbose_name="Stack Trace")

    # Context
    url = models.URLField(blank=True, max_length=500, verbose_name="URL")
    method = models.CharField(max_length=10, blank=True, verbose_name="HTTP Method")
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="beta_errors",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Request data
    request_data = models.JSONField(
        default=dict, blank=True, verbose_name="Request Data"
    )
    headers = models.JSONField(default=dict, blank=True, verbose_name="Headers")

    # System info
    server_name = models.CharField(max_length=200, blank=True)
    python_version = models.CharField(max_length=50, blank=True)
    django_version = models.CharField(max_length=50, blank=True)

    # Timestamps
    first_seen = models.DateTimeField(auto_now_add=True, verbose_name="İlk Görüldü")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Son Görüldü")
    occurrence_count = models.IntegerField(default=1, verbose_name="Tekrar Sayısı")

    # Resolution
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="beta_resolved_errors",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Notification
    admin_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Hata Kaydı"
        verbose_name_plural = "Hata Kayıtları"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["-last_seen"]),
            models.Index(fields=["severity", "status"]),
            models.Index(fields=["error_type", "-last_seen"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.error_type}: {self.error_message[:100]}"

    @property
    def is_critical(self):
        return self.severity in ["CRITICAL", "ERROR"]

    @property
    def needs_notification(self):
        """Critical hatalar veya ilk görülen hatalar bildirim gerektirir"""
        return self.is_critical and not self.admin_notified


class BetaErrorTracker:
    """Beta error tracking utility"""

    def __init__(self):
        self.logger = logging.getLogger("beta_errors")

    def capture_exception(
        self,
        exception: Exception,
        request: Optional[Any] = None,
        extra_data: Optional[Dict] = None,
        severity: str = "ERROR",
    ) -> Optional[ErrorLog]:
        """
        Hata yakala ve kaydet

        Args:
            exception: Python exception
            request: Django request object
            extra_data: Ekstra context data
            severity: ERROR, CRITICAL, WARNING, etc.
        """
        try:
            # Exception details
            error_type = type(exception).__name__
            error_message = str(exception)
            tb = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )

            # Request context
            url = ""
            method = ""
            user = None
            ip_address = None
            user_agent = ""
            request_data = {}
            headers = {}

            if request:
                url = request.build_absolute_uri()
                method = request.method
                user = (
                    request.user
                    if hasattr(request, "user") and request.user.is_authenticated
                    else None
                )
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get("HTTP_USER_AGENT", "")

                # Request data (sanitize sensitive info)
                request_data = {
                    "GET": dict(request.GET),
                    "POST": self._sanitize_data(dict(request.POST)),
                }

                # Headers (sanitize sensitive info)
                headers = {
                    k: v
                    for k, v in request.META.items()
                    if k.startswith("HTTP_")
                    and k not in ["HTTP_AUTHORIZATION", "HTTP_COOKIE"]
                }

            # System info
            import django

            server_name = (
                settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "unknown"
            )
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            django_version = django.get_version()

            # Check if similar error exists (deduplication)
            similar_error = ErrorLog.objects.filter(
                error_type=error_type,
                error_message=error_message,
                status__in=["NEW", "INVESTIGATING"],
            ).first()

            if similar_error:
                # Update existing error
                from django.utils import timezone as tz

                similar_error.occurrence_count += 1
                similar_error.last_seen = tz.now()
                similar_error.save()
                error_log = similar_error
                self.logger.info(
                    f"Updated existing error: {error_type} (count: {error_log.occurrence_count})"
                )
            else:
                # Create new error
                error_log = ErrorLog.objects.create(
                    severity=severity,
                    error_type=error_type,
                    error_message=error_message,
                    traceback=tb,
                    url=url,
                    method=method,
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_data=request_data,
                    headers=headers,
                    server_name=server_name,
                    python_version=python_version,
                    django_version=django_version,
                )
                self.logger.error(f"New error captured: {error_type}")

            # Send notifications for critical errors
            if error_log.needs_notification:
                self._send_notifications(error_log)

            return error_log

        except Exception as e:
            # Don't let error tracking break the app
            self.logger.exception(f"Error tracking failed: {e}")
            return None

    def _get_client_ip(self, request) -> Optional[str]:
        """Get client IP from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _sanitize_data(self, data: Dict) -> Dict:
        """Remove sensitive data from request data"""
        sensitive_keys = [
            "password",
            "secret",
            "token",
            "api_key",
            "apikey",
            "auth",
            "authorization",
            "credit_card",
            "cvv",
            "ssn",
        ]

        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value

        return sanitized

    def _send_notifications(self, error_log: ErrorLog):
        """Send notifications to admins"""
        try:
            # Email notification
            self._send_email_notification(error_log)

            # Slack/Discord webhook (if configured)
            self._send_webhook_notification(error_log)

            # Mark as notified
            from django.utils import timezone

            error_log.admin_notified = True
            error_log.notification_sent_at = timezone.now()
            error_log.save()

        except Exception as e:
            self.logger.exception(f"Failed to send notifications: {e}")

    def _send_email_notification(self, error_log: ErrorLog):
        """Send email to admins"""
        if not settings.ADMINS:
            return

        subject = f"🚨 [{error_log.severity}] FinAsis Beta Error: {error_log.error_type}"

        message = f"""
FinAsis Beta Error Alert
{'=' * 60}

Severity: {error_log.severity}
Error Type: {error_log.error_type}
Message: {error_log.error_message}

URL: {error_log.url}
Method: {error_log.method}
User: {error_log.user.email if error_log.user else 'Anonymous'}
IP: {error_log.ip_address}

Occurrence Count: {error_log.occurrence_count}
First Seen: {error_log.first_seen}
Last Seen: {error_log.last_seen}

Stack Trace:
{error_log.traceback}

{'=' * 60}
View in Admin: {settings.SITE_URL}/admin/common/errorlog/{error_log.id}/change/
"""

        try:
            recipient_list = [admin[1] for admin in settings.ADMINS]
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            self.logger.info(f"Email notification sent for error {error_log.id}")
        except Exception as e:
            self.logger.exception(f"Failed to send email: {e}")

    def _send_webhook_notification(self, error_log: ErrorLog):
        """Send webhook notification (Slack/Discord)"""
        webhook_url = getattr(settings, "ERROR_WEBHOOK_URL", None)
        if not webhook_url:
            return

        try:
            import requests

            # Determine webhook type
            if "discord" in webhook_url.lower():
                payload = self._format_discord_payload(error_log)
            elif "slack" in webhook_url.lower():
                payload = self._format_slack_payload(error_log)
            else:
                # Generic webhook
                payload = self._format_generic_payload(error_log)

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Webhook notification sent for error {error_log.id}")

        except Exception as e:
            self.logger.exception(f"Failed to send webhook: {e}")

    def _format_discord_payload(self, error_log: ErrorLog) -> Dict:
        """Format Discord webhook payload"""
        color_map = {
            "CRITICAL": 0xFF0000,  # Red
            "ERROR": 0xFF6B6B,  # Light red
            "WARNING": 0xFFA500,  # Orange
            "INFO": 0x00BFFF,  # Blue
        }

        return {
            "embeds": [
                {
                    "title": f"🚨 {error_log.error_type}",
                    "description": error_log.error_message[:500],
                    "color": color_map.get(error_log.severity, 0xFF6B6B),
                    "fields": [
                        {
                            "name": "Severity",
                            "value": error_log.severity,
                            "inline": True,
                        },
                        {
                            "name": "Occurrences",
                            "value": str(error_log.occurrence_count),
                            "inline": True,
                        },
                        {
                            "name": "URL",
                            "value": error_log.url or "N/A",
                            "inline": False,
                        },
                        {
                            "name": "User",
                            "value": error_log.user.email
                            if error_log.user
                            else "Anonymous",
                            "inline": True,
                        },
                    ],
                    "timestamp": error_log.last_seen.isoformat(),
                    "footer": {"text": "FinAsis Beta Error Tracker"},
                }
            ]
        }

    def _format_slack_payload(self, error_log: ErrorLog) -> Dict:
        """Format Slack webhook payload"""
        color_map = {
            "CRITICAL": "danger",
            "ERROR": "danger",
            "WARNING": "warning",
            "INFO": "good",
        }

        return {
            "attachments": [
                {
                    "color": color_map.get(error_log.severity, "danger"),
                    "title": f"🚨 {error_log.error_type}",
                    "text": error_log.error_message[:500],
                    "fields": [
                        {
                            "title": "Severity",
                            "value": error_log.severity,
                            "short": True,
                        },
                        {
                            "title": "Occurrences",
                            "value": str(error_log.occurrence_count),
                            "short": True,
                        },
                        {
                            "title": "URL",
                            "value": error_log.url or "N/A",
                            "short": False,
                        },
                        {
                            "title": "User",
                            "value": error_log.user.email
                            if error_log.user
                            else "Anonymous",
                            "short": True,
                        },
                    ],
                    "ts": int(error_log.last_seen.timestamp()),
                }
            ]
        }

    def _format_generic_payload(self, error_log: ErrorLog) -> Dict:
        """Format generic webhook payload"""
        return {
            "severity": error_log.severity,
            "error_type": error_log.error_type,
            "error_message": error_log.error_message,
            "url": error_log.url,
            "user": error_log.user.email if error_log.user else None,
            "occurrence_count": error_log.occurrence_count,
            "timestamp": error_log.last_seen.isoformat(),
        }


# Global error tracker instance
error_tracker = BetaErrorTracker()


def track_error(exception: Exception, request=None, **kwargs):
    """
    Convenience function to track errors

    Usage:
        try:
            # your code
        except Exception as e:
            track_error(e, request)
            raise
    """
    return error_tracker.capture_exception(exception, request, **kwargs)
