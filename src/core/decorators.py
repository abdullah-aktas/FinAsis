"""
Özel dekoratörler.
Bu modül, proje genelinde kullanılacak özel dekoratörleri içerir.
"""

import functools
import time
import logging
from typing import Callable, Any
from django.core.cache import cache
from django.db import transaction
from .exceptions import RateLimitError, CacheError

logger = logging.getLogger(__name__)

def rate_limit(limit: int, window: int = 60):
    """
    İstek sınırlaması uygulayan dekoratör.
    
    Args:
        limit: Belirli bir süre içinde izin verilen maksimum istek sayısı
        window: Sınırlama penceresi (saniye)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"rate_limit:{func.__name__}:{args[0].__class__.__name__}"
            current = cache.get(key, 0)
            
            if current >= limit:
                raise RateLimitError(limit=limit, window=window)
            
            cache.set(key, current + 1, window)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cache_result(timeout: int = 300):
    """
    Fonksiyon sonucunu önbelleğe alan dekoratör.
    
    Args:
        timeout: Önbellek süresi (saniye)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                try:
                    cache.set(cache_key, result, timeout)
                except Exception as e:
                    raise CacheError(
                        operation="cache_set",
                        error_message=str(e)
                    )
            
            return result
        return wrapper
    return decorator

def transaction_atomic():
    """
    Veritabanı işlemlerini atomik hale getiren dekoratör.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
    return decorator

def log_execution_time():
    """
    Fonksiyon çalışma süresini loglayan dekoratör.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            logger.info(
                f"Function {func.__name__} executed in {end_time - start_time:.2f} seconds"
            )
            return result
        return wrapper
    return decorator

def retry_on_failure(max_attempts: int = 3, delay: int = 1):
    """
    Başarısız işlemleri yeniden deneyen dekoratör.
    
    Args:
        max_attempts: Maksimum deneme sayısı
        delay: Denemeler arası bekleme süresi (saniye)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}. Retrying..."
                        )
            
            raise last_exception
        return wrapper
    return decorator

def validate_input(validator: Callable[[Any], bool]):
    """
    Girdi doğrulaması yapan dekoratör.
    
    Args:
        validator: Doğrulama fonksiyonu
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not validator(*args, **kwargs):
                raise ValueError("Input validation failed")
            return func(*args, **kwargs)
        return wrapper
    return decorator 