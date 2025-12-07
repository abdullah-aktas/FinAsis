"""
Cache invalidation signals for automatic cache clearing on model changes.
Ensures data consistency while maintaining high cache hit rates.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .cache_decorators import invalidate_cache
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# GENERIC MODEL CACHE INVALIDATION
# ============================================================================


def create_model_invalidation_signals(model_class, cache_patterns: list):
    """
    Create cache invalidation signals for a model.

    Usage:
        create_model_invalidation_signals(
            Company,
            ['Company:*', 'user_*_companies', 'companies_list']
        )
    """

    @receiver(post_save, sender=model_class)
    def invalidate_on_save(sender, instance, created, **kwargs):
        action = "created" if created else "updated"
        logger.info(f"{model_class.__name__} {action}: {instance.pk}")
        invalidate_cache(*cache_patterns)

    @receiver(post_delete, sender=model_class)
    def invalidate_on_delete(sender, instance, **kwargs):
        logger.info(f"{model_class.__name__} deleted: {instance.pk}")
        invalidate_cache(*cache_patterns)


# ============================================================================
# USER & AUTHENTICATION CACHE INVALIDATION
# ============================================================================


@receiver(post_save, sender="auth.User")
def invalidate_user_cache(sender, instance, created, **kwargs):
    """Invalidate user-related cache on user changes."""
    user_id = instance.id
    patterns = [
        f"user_{user_id}_*",  # All user-specific caches
        f"User:{user_id}:*",  # Model instance caches
        "users_list",  # User list cache
    ]
    invalidate_cache(*patterns)
    logger.debug(f"Invalidated cache for user {user_id}")


@receiver(post_delete, sender="auth.User")
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    """Invalidate user cache on deletion."""
    user_id = instance.id
    patterns = [f"user_{user_id}_*", f"User:{user_id}:*", "users_list"]
    invalidate_cache(*patterns)


# ============================================================================
# SESSION CACHE INVALIDATION
# ============================================================================


@receiver(post_save, sender="sessions.Session")
def invalidate_session_cache(sender, instance, **kwargs):
    """Clear session cache on session update."""
    session_key = instance.session_key
    cache.delete(f"session:{session_key}")


# ============================================================================
# COMPANY & ORGANIZATION CACHE
# ============================================================================


def setup_company_cache_invalidation(Company):
    """
    Setup cache invalidation for Company model.

    Call this in apps.py ready() method:
        from apps.common.cache_signals import setup_company_cache_invalidation
        from apps.companies.models import Company
        setup_company_cache_invalidation(Company)
    """

    @receiver(post_save, sender=Company)
    def invalidate_company_cache(sender, instance, created, **kwargs):
        patterns = [
            f"Company:{instance.pk}:*",
            (
                f"user_{instance.owner_id}_companies"
                if hasattr(instance, "owner_id")
                else None
            ),
            "companies_list",
            "companies_stats",
        ]
        patterns = [p for p in patterns if p]  # Remove None values
        invalidate_cache(*patterns)

    @receiver(post_delete, sender=Company)
    def invalidate_company_cache_on_delete(sender, instance, **kwargs):
        patterns = [
            f"Company:{instance.pk}:*",
            "companies_list",
            "companies_stats",
        ]
        invalidate_cache(*patterns)


# ============================================================================
# ACCOUNTING & FINANCE CACHE
# ============================================================================


def setup_accounting_cache_invalidation(GLAccount, GLJournal):
    """Setup cache invalidation for accounting models."""

    @receiver(post_save, sender=GLAccount)
    def invalidate_glaccount_cache(sender, instance, **kwargs):
        patterns = [
            f"GLAccount:{instance.pk}:*",
            (
                f"company_{instance.company_id}_accounts"
                if hasattr(instance, "company_id")
                else None
            ),
            "chart_of_accounts",
        ]
        patterns = [p for p in patterns if p]
        invalidate_cache(*patterns)

    @receiver(post_save, sender=GLJournal)
    def invalidate_journal_cache(sender, instance, **kwargs):
        patterns = [
            f"GLJournal:{instance.pk}:*",
            (
                f"company_{instance.company_id}_journals"
                if hasattr(instance, "company_id")
                else None
            ),
            "financial_statements",
            "balance_sheet",
            "income_statement",
        ]
        patterns = [p for p in patterns if p]
        invalidate_cache(*patterns)


# ============================================================================
# EDOC (E-INVOICE/E-LEDGER) CACHE
# ============================================================================


def setup_edoc_cache_invalidation(EInvoice, ELedger):
    """Setup cache invalidation for e-document models."""

    @receiver(post_save, sender=EInvoice)
    def invalidate_einvoice_cache(sender, instance, **kwargs):
        patterns = [
            f"EInvoice:{instance.pk}:*",
            (
                f"company_{instance.company_id}_einvoices"
                if hasattr(instance, "company_id")
                else None
            ),
            "einvoices_pending",
            "einvoices_stats",
        ]
        patterns = [p for p in patterns if p]
        invalidate_cache(*patterns)

    @receiver(post_save, sender=ELedger)
    def invalidate_eledger_cache(sender, instance, **kwargs):
        patterns = [
            f"ELedger:{instance.pk}:*",
            (
                f"company_{instance.company_id}_eledgers"
                if hasattr(instance, "company_id")
                else None
            ),
            "eledgers_stats",
        ]
        patterns = [p for p in patterns if p]
        invalidate_cache(*patterns)


# ============================================================================
# API RESPONSE CACHE INVALIDATION
# ============================================================================


class CacheInvalidationMixin:
    """
    Mixin for DRF ViewSets to auto-invalidate cache on create/update/delete.

    Usage:
        class CompanyViewSet(CacheInvalidationMixin, ModelViewSet):
            cache_patterns = ['Company:*', 'companies_list']
    """

    cache_patterns: list = []

    def perform_create(self, serializer):
        """Override in DRF ViewSet."""
        super().perform_create(serializer)  # type: ignore
        self.invalidate_cache()

    def perform_update(self, serializer):
        """Override in DRF ViewSet."""
        super().perform_update(serializer)  # type: ignore
        self.invalidate_cache()

    def perform_destroy(self, instance):
        """Override in DRF ViewSet."""
        super().perform_destroy(instance)  # type: ignore
        self.invalidate_cache()

    def invalidate_cache(self):
        if self.cache_patterns:
            invalidate_cache(*self.cache_patterns)
            logger.debug(f"Invalidated cache patterns: {self.cache_patterns}")


# ============================================================================
# CACHE WARMING UTILITIES
# ============================================================================


def warm_critical_caches():
    """
    Warm up critical caches on application start or after flush.
    Call this from a management command or Celery task.
    """
    from django.contrib.auth import get_user_model

    logger.info("Starting cache warm-up...")

    try:
        User = get_user_model()

        # Warm user count cache
        user_count = User.objects.count()
        cache.set("users_count", user_count, timeout=3600)
        logger.info(f"Warmed user count cache: {user_count}")

        # Add more critical caches here based on your app
        # Example:
        # active_companies = Company.objects.filter(is_active=True).count()
        # cache.set('active_companies_count', active_companies, timeout=3600)

        logger.info("Cache warm-up completed successfully")
        return True

    except Exception as e:
        logger.error(f"Cache warm-up failed: {e}")
        return False


# ============================================================================
# CACHE STATISTICS & MONITORING
# ============================================================================


def get_cache_statistics():
    """
    Get comprehensive cache statistics.
    Returns hit rate, memory usage, key count, etc.
    """
    try:
        from django_redis import get_redis_connection

        redis_conn = get_redis_connection("default")

        info = redis_conn.info()
        stats_info = redis_conn.info("stats")

        hits = stats_info.get("keyspace_hits", 0)
        misses = stats_info.get("keyspace_misses", 0)
        total_requests = hits + misses
        hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hit_rate": round(hit_rate, 2),
            "hits": hits,
            "misses": misses,
            "total_requests": total_requests,
            "memory_used": info.get("used_memory_human", "N/A"),
            "memory_peak": info.get("used_memory_peak_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "total_keys": sum(
                int(value.get("keys", 0))
                for key, value in info.items()
                if key.startswith("db")
            ),
            "evicted_keys": info.get("evicted_keys", 0),
            "expired_keys": info.get("expired_keys", 0),
        }
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        return {
            "error": str(e),
            "hit_rate": 0,
        }


def log_cache_stats():
    """Log current cache statistics."""
    stats = get_cache_statistics()
    if "error" not in stats:
        logger.info(
            f"Cache Stats - Hit Rate: {stats['hit_rate']}%, "
            f"Total Keys: {stats['total_keys']}, "
            f"Memory: {stats['memory_used']}"
        )
    else:
        logger.warning(f"Cache stats unavailable: {stats['error']}")
