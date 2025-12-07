"""
Error Tracking Middleware
Tüm hataları otomatik yakalar ve bildirir
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from .error_tracking import error_tracker

logger = logging.getLogger(__name__)


class ErrorTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to catch and track all exceptions
    """

    def process_exception(self, request, exception):
        """
        Called when a view raises an exception
        """
        # Store exception in request for error handler
        request._exception = exception

        # Track the error
        try:
            error_log = error_tracker.capture_exception(
                exception, request=request, severity="ERROR"
            )

            # Log to console
            logger.exception(
                f"Exception in {request.method} {request.path}",
                extra={
                    "error_log_id": error_log.id if error_log else None,
                    "user": (
                        request.user.email
                        if hasattr(request, "user") and request.user.is_authenticated
                        else "Anonymous"
                    ),
                },
            )

        except Exception as e:
            # Don't let error tracking break the app
            logger.exception(f"Error tracking middleware failed: {e}")

        # Let Django's default error handling proceed
        return None


class CriticalErrorMiddleware(MiddlewareMixin):
    """
    Middleware to catch critical system errors
    """

    def process_exception(self, request, exception):
        """
        Catch critical errors and notify immediately
        """
        # Critical exception types
        critical_exceptions = (
            MemoryError,
            SystemError,
            RecursionError,
        )

        if isinstance(exception, critical_exceptions):
            try:
                error_tracker.capture_exception(
                    exception, request=request, severity="CRITICAL"
                )
                logger.critical(
                    f"CRITICAL ERROR: {type(exception).__name__} in {request.path}",
                    exc_info=True,
                )
            except Exception as e:
                logger.exception(f"Failed to track critical error: {e}")

        return None


class APIErrorTrackingMiddleware(MiddlewareMixin):
    """
    Special middleware for API endpoints
    Returns JSON error responses
    """

    def process_exception(self, request, exception):
        """
        Handle API exceptions
        """
        # Only process API requests
        if not request.path.startswith("/api/"):
            return None

        # Track the error
        try:
            error_log = error_tracker.capture_exception(
                exception, request=request, severity="ERROR"
            )

            # Return JSON error response
            error_id = error_log.id if error_log else "unknown"

            if settings.DEBUG:
                # In debug mode, show detailed error
                return JsonResponse(
                    {
                        "error": True,
                        "error_type": type(exception).__name__,
                        "message": str(exception),
                        "error_id": error_id,
                    },
                    status=500,
                )
            else:
                # In production, show generic error
                return JsonResponse(
                    {
                        "error": True,
                        "message": "Internal server error. Our team has been notified.",
                        "error_id": error_id,
                    },
                    status=500,
                )

        except Exception as e:
            logger.exception(f"API error tracking failed: {e}")
            return JsonResponse(
                {
                    "error": True,
                    "message": "An unexpected error occurred.",
                },
                status=500,
            )
