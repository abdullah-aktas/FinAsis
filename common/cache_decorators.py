"""
Cache decorators for views, queries, and templates.
Provides high-performance caching utilities with Redis backend.
"""

from functools import wraps
from django.core.cache import cache, caches
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from typing import Callable, Optional, List
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cache_view(
    timeout: int = 300, key_prefix: str = "", vary_on: Optional[List[str]] = None
):
    """
    Cache entire view response with optional variations.

    Usage:
        @cache_view(timeout=600, key_prefix='homepage', vary_on=['Accept-Language'])
        def my_view(request):
            return render(request, 'template.html')

    Args:
        timeout: Cache timeout in seconds (default: 300 = 5 minutes)
        key_prefix: Prefix for cache key
        vary_on: List of headers to vary cache on (e.g., ['Accept-Language', 'Cookie'])
    """

    def decorator(view_func):
        # Apply cache_page decorator
        cached_view = cache_page(timeout, key_prefix=key_prefix)(view_func)

        # Apply vary_on decorators if specified
        if vary_on:
            for header in vary_on:
                if header.lower() == "cookie":
                    cached_view = vary_on_cookie(cached_view)
                else:
                    cached_view = vary_on_headers(header)(cached_view)

        return cached_view

    return decorator


def cache_query(timeout: int = 300, key_func: Optional[Callable] = None):
    """
    Cache database query results.

    Usage:
        @cache_query(timeout=600, key_func=lambda user_id: f'user_{user_id}_stats')
        def get_user_statistics(user_id):
            return User.objects.get(id=user_id).calculate_stats()

    Args:
        timeout: Cache timeout in seconds
        key_func: Function to generate cache key from arguments
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation from function name and arguments
                key_parts = [func.__module__, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return result

            # Cache miss - execute function and cache result
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def cache_model_instance(timeout: int = 600):
    """
    Cache model instance method results.

    Usage:
        class Company(models.Model):
            @cache_model_instance(timeout=3600)
            def get_financial_summary(self):
                # Expensive calculation
                return calculate_summary()
    """

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Generate cache key from model, pk, and method name
            cache_key = f"{self.__class__.__name__}:{self.pk}:{method.__name__}"

            # Add arguments to key if present
            if args or kwargs:
                arg_hash = hashlib.md5(
                    json.dumps([args, kwargs], sort_keys=True, default=str).encode()
                ).hexdigest()[:8]
                cache_key = f"{cache_key}:{arg_hash}"

            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Model cache HIT: {cache_key}")
                return result

            logger.debug(f"Model cache MISS: {cache_key}")
            result = method(self, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def cache_api_response(timeout: int = 300, vary_on_user: bool = True):
    """
    Cache DRF API responses.

    Usage:
        class MyAPIView(APIView):
            @cache_api_response(timeout=600, vary_on_user=True)
            def get(self, request):
                return Response(data)
    """

    def decorator(view_method):
        @wraps(view_method)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key
            key_parts = [
                request.path,
                request.method,
            ]

            if vary_on_user and request.user.is_authenticated:
                key_parts.append(f"user_{request.user.id}")

            # Add query parameters to key
            if request.query_params:
                query_hash = hashlib.md5(
                    json.dumps(dict(request.query_params), sort_keys=True).encode()
                ).hexdigest()[:8]
                key_parts.append(query_hash)

            cache_key = ":".join(key_parts)

            # Try cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f"API cache HIT: {cache_key}")
                return cached_response

            # Execute view
            logger.debug(f"API cache MISS: {cache_key}")
            response = view_method(self, request, *args, **kwargs)

            # Cache successful responses only
            if 200 <= response.status_code < 300:
                cache.set(cache_key, response, timeout)

            return response

        return wrapper

    return decorator


def invalidate_cache(*patterns: str):
    """
    Invalidate cache keys matching patterns.

    Usage:
        invalidate_cache('user_123_*', 'Company:456:*')
    """
    # First, try Redis fast-path if available
    try:
        from django_redis import get_redis_connection  # type: ignore

        redis_conn = get_redis_connection("default")
        deleted_count = 0
        for pattern in patterns:
            full_pattern = (
                f"finasis:{pattern}" if not pattern.startswith("finasis:") else pattern
            )
            for key in list(redis_conn.scan_iter(match=full_pattern)):
                redis_conn.delete(key)
                deleted_count += 1
        logger.info(
            f"Invalidated {deleted_count} cache keys matching patterns: {patterns}"
        )
        return deleted_count
    except Exception:
        # Fallback: best-effort invalidation for non-Redis backends (e.g., LocMemCache)
        try:
            backend = caches["default"]
            deleted_total = 0
            for pattern in patterns:
                full_pattern = (
                    f"finasis:{pattern}"
                    if not pattern.startswith("finasis:")
                    else pattern
                )
                prefix = full_pattern.replace("*", "")
                # Some backends (django-redis) expose delete_pattern
                if hasattr(backend, "delete_pattern"):
                    # type: ignore[attr-defined]
                    deleted = backend.delete_pattern(full_pattern)  # type: ignore[call-arg]
                    # delete_pattern may return None on some backends
                    deleted_total += int(deleted or 0)
                    continue
                # LocMemCache/private: iterate internal cache keys
                internal = getattr(backend, "_cache", None)
                if isinstance(internal, dict):
                    # Copy keys to avoid runtime mutation issues
                    keys = list(internal.keys())
                    for key in keys:
                        k = (
                            key.decode()
                            if isinstance(key, (bytes, bytearray))
                            else str(key)
                        )
                        # Convert to backend internal prefix representation if possible
                        try:
                            internal_prefix = backend.make_key(prefix)  # type: ignore[attr-defined]
                        except Exception:
                            internal_prefix = prefix
                        if k.startswith(internal_prefix):
                            # Directly remove from internal store for locmem backend
                            internal.pop(key, None)
                            expire_map = getattr(backend, "_expire_info", None)
                            if isinstance(expire_map, dict):
                                expire_map.pop(key, None)
                            deleted_total += 1
            logger.info(
                f"[fallback] Invalidated ~{deleted_total} cache keys matching patterns: {patterns}"
            )
            return deleted_total
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return 0


def cache_on_signal(
    signal, sender, timeout: int = 300, invalidate_on: Optional[List[str]] = None
):
    """
    Cache until signal is received, then invalidate.

    Usage:
        @cache_on_signal(
            signal=post_save,
            sender=Company,
            timeout=3600,
            invalidate_on=['Company:*']
        )
        def get_all_companies():
            return list(Company.objects.all())
    """

    def decorator(func):
        # Connect signal to invalidate cache
        if invalidate_on is not None and len(invalidate_on) > 0:
            patterns_to_invalidate: List[str] = invalidate_on  # Type hint for checker

            def invalidate_handler(sender, **kwargs):
                try:
                    invalidate_cache(*patterns_to_invalidate)
                except Exception as e:
                    logger.error(f"Cache invalidation failed in signal handler: {e}")

            signal.connect(invalidate_handler, sender=sender, weak=False)

        # Apply cache_query decorator
        return cache_query(timeout=timeout)(func)

    return decorator


class CacheService:
    """
    Centralized cache service with hit/miss tracking.
    """

    def __init__(self, cache_alias: str = "default"):
        self.cache = caches[cache_alias]
        self.cache_alias = cache_alias

    def get_or_set(self, key: str, default_func: Callable, timeout: int = 300):
        """
        Get from cache or execute function and cache result.

        Args:
            key: Cache key
            default_func: Function to execute on cache miss
            timeout: Cache timeout in seconds
        """
        value = self.cache.get(key)
        if value is not None:
            logger.debug(f"[{self.cache_alias}] Cache HIT: {key}")
            return value

        logger.debug(f"[{self.cache_alias}] Cache MISS: {key}")
        value = default_func()
        self.cache.set(key, value, timeout)
        return value

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        return invalidate_cache(pattern)

    def get_stats(self):
        """Get cache statistics (requires Redis)."""
        try:
            from django_redis import get_redis_connection

            redis_conn = get_redis_connection(self.cache_alias)
            info = redis_conn.info("stats")
            return {
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# Global cache service instance
default_cache_service = CacheService("default")
session_cache_service = CacheService("session")


# Template tag için helper function
def cache_fragment(fragment_name: str, timeout: int = 300, *vary_on):
    """
    Template fragment caching için helper.

    Django template'de kullanım:
        {% load cache %}
        {% cache 500 sidebar request.user.username %}
            ... expensive sidebar rendering ...
        {% endcache %}
    """
    return {
        "name": fragment_name,
        "timeout": timeout,
        "vary_on": vary_on,
    }
