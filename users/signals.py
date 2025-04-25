"""
Users Modülü - Signals
---------------------
Bu dosya, Users modülünün signal fonksiyonlarını içerir.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import UserProfile, UserPreferences, UserActivity, UserNotification, UserSession, UserSettings
from .tasks import send_welcome_email, send_profile_update_notification

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Yeni kullanıcı oluşturulduğunda profil, tercih ve ayarlarını oluştur"""
    if created:
        UserProfile.objects.create(user=instance)
        UserPreferences.objects.create(user=instance)
        UserSettings.objects.create(user=instance)
        # Hoş geldin e-postası gönder
        send_welcome_email.delay(instance.id)
        # Aktivite kaydı oluştur
        UserActivity.objects.create(
            user=instance,
            action='user_created',
            details='Kullanıcı hesabı oluşturuldu'
        )

@receiver(pre_save, sender=User)
def update_user_activity(sender, instance, **kwargs):
    """Kullanıcı bilgileri güncellendiğinde aktivite kaydı oluştur"""
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.email != instance.email:
                UserActivity.objects.create(
                    user=instance,
                    action='email_changed',
                    details=f'E-posta adresi {old_user.email} -> {instance.email} olarak değiştirildi'
                )
            if old_user.is_active != instance.is_active:
                action = 'account_activated' if instance.is_active else 'account_deactivated'
                UserActivity.objects.create(
                    user=instance,
                    action=action,
                    details='Hesap durumu değiştirildi'
                )
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=UserProfile)
def handle_profile_update(sender, instance, created, **kwargs):
    """Profil güncellendiğinde aktivite kaydı oluştur ve bildirim gönder"""
    if not created:
        UserActivity.objects.create(
            user=instance.user,
            action='profile_updated',
            details='Profil bilgileri güncellendi'
        )
        # Profil güncelleme bildirimi gönder
        send_profile_update_notification.delay(instance.user.id)
        # Önbelleği temizle
        cache.delete(f'profile_{instance.user.id}')

@receiver(post_save, sender=UserPreferences)
def handle_preferences_update(sender, instance, created, **kwargs):
    """Tercihler güncellendiğinde aktivite kaydı oluştur"""
    if not created:
        UserActivity.objects.create(
            user=instance.user,
            action='preferences_updated',
            details='Kullanıcı tercihleri güncellendi'
        )
        # Önbelleği temizle
        cache.delete(f'preferences_{instance.user.id}')

@receiver(post_save, sender=UserNotification)
def handle_notification_creation(sender, instance, created, **kwargs):
    """Yeni bildirim oluşturulduğunda önbelleği temizle"""
    if created:
        cache.delete(f'notifications_{instance.user.id}')

@receiver(post_delete, sender=UserNotification)
def handle_notification_deletion(sender, instance, **kwargs):
    """Bildirim silindiğinde önbelleği temizle"""
    cache.delete(f'notifications_{instance.user.id}')

@receiver(post_save, sender=UserSession)
def handle_session_update(sender, instance, created, **kwargs):
    """Oturum güncellendiğinde önbelleği temizle"""
    cache.delete(f'sessions_{instance.user.id}')

@receiver(post_delete, sender=UserSession)
def handle_session_deletion(sender, instance, **kwargs):
    """Oturum silindiğinde önbelleği temizle"""
    cache.delete(f'sessions_{instance.user.id}')

@receiver(post_save, sender=User)
def clear_user_cache(sender, instance, **kwargs):
    """Kullanıcı bilgileri güncellendiğinde önbelleği temizle"""
    cache.delete(f'user_{instance.id}')
    # İlişkili önbellekleri de temizle
    cache.delete(f'profile_{instance.id}')
    cache.delete(f'preferences_{instance.id}')
    cache.delete(f'notifications_{instance.id}')
    cache.delete(f'sessions_{instance.id}')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Kullanıcı güncellendiğinde profil, tercih ve ayarlarını güncelle"""
    instance.profile.save()
    instance.preferences.save()
    instance.settings.save()

@receiver(post_delete, sender=User)
def delete_user_cache(sender, instance, **kwargs):
    """Kullanıcı silindiğinde cache'i temizle"""
    cache.delete(f'profile_{instance.id}')
    cache.delete(f'preferences_{instance.id}')
    cache.delete(f'settings_{instance.id}')
    cache.delete(f'activities_{instance.id}')
    cache.delete(f'notifications_{instance.id}')
    cache.delete(f'sessions_{instance.id}') 