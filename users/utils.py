"""
Users Modülü - Yardımcı Fonksiyonlar
---------------------
Bu dosya, Users modülünün yardımcı fonksiyonlarını içerir.
"""

from django.utils import timezone
from django.core.cache import cache
from .models import (
    UserActivity, UserNotification, UserSession,
    UserPreferences, UserSettings
)

def log_user_activity(user, action, details=None):
    """
    Kullanıcı aktivitelerini loglar.
    
    Args:
        user: Kullanıcı objesi
        action: Yapılan işlem (string)
        details: İşlem detayları (dict, optional)
    """
    UserActivity.objects.create(
        user=user,
        action=action,
        details=details or {},
        timestamp=timezone.now()
    )
    
    # Cache'i temizle
    cache.delete(f'user_activities_{user.id}')
    
    return True

def get_client_ip(request):
    """İstemci IP adresini döndürür"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_activities(user, limit=10):
    """Kullanıcının son aktivitelerini döndürür"""
    cache_key = f'user_activities_{user.id}'
    activities = cache.get(cache_key)
    
    if activities is None:
        activities = UserActivity.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
        cache.set(cache_key, activities, 300)  # 5 dakika cache
    
    return activities

def get_user_notifications(user, limit=10):
    """Kullanıcının son bildirimlerini döndürür"""
    cache_key = f'user_notifications_{user.id}'
    notifications = cache.get(cache_key)
    
    if notifications is None:
        notifications = UserNotification.objects.filter(
            user=user,
            is_read=False
        ).order_by('-created_at')[:limit]
        cache.set(cache_key, notifications, 300)  # 5 dakika cache
    
    return notifications

def get_user_sessions(user):
    """Kullanıcının aktif oturumlarını döndürür"""
    cache_key = f'user_sessions_{user.id}'
    sessions = cache.get(cache_key)
    
    if sessions is None:
        sessions = UserSession.objects.filter(
            user=user,
            last_activity__gt=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-last_activity')
        cache.set(cache_key, sessions, 300)  # 5 dakika cache
    
    return sessions

def get_user_preferences(user):
    """Kullanıcının tercihlerini döndürür"""
    cache_key = f'user_preferences_{user.id}'
    preferences = cache.get(cache_key)
    
    if preferences is None:
        preferences = UserPreferences.objects.get_or_create(user=user)[0]
        cache.set(cache_key, preferences, 300)  # 5 dakika cache
    
    return preferences

def get_user_settings(user):
    """Kullanıcının ayarlarını döndürür"""
    cache_key = f'user_settings_{user.id}'
    settings = cache.get(cache_key)
    
    if settings is None:
        settings = UserSettings.objects.get_or_create(user=user)[0]
        cache.set(cache_key, settings, 300)  # 5 dakika cache
    
    return settings 