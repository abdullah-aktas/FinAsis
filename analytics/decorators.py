# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
import time

def rate_limit(key_prefix, max_requests=60, time_window=60):
    """
    Rate limiting decorator
    
    Args:
        key_prefix: Cache key prefix
        max_requests: Maximum number of requests allowed
        time_window: Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Kullanıcı bazlı rate limiting
            user_id = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
            cache_key = f"{key_prefix}:{user_id}"
            
            # Mevcut istek sayısını al
            current = cache.get(cache_key, 0)
            
            if current >= max_requests:
                return JsonResponse({
                    'error': 'Çok fazla istek gönderdiniz. Lütfen bir süre bekleyin.',
                    'retry_after': time_window
                }, status=429)
            
            # İstek sayısını artır
            cache.set(cache_key, current + 1, time_window)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 