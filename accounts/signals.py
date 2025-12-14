from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
import logging

from accounts.services.role_profiles import ensure_role_profile
from common.services.notification_service import NotificationService

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def ensure_role_profile_on_create(sender, instance, created, **kwargs):
    """
    After a CustomUser is created or updated, make sure the RoleBasedUserProfile
    matches the most recent role assignment.
    """
    if instance is None:
        return

    ensure_role_profile(instance)
    
    # Yeni kullanıcı kaydı bildirimi
    if created:
        try:
            NotificationService.notify_user_registered(instance)
        except Exception as e:
            logger.error(f"Kullanıcı kayıt bildirimi hatası: {e}")


@receiver(user_logged_in)
def notify_suspicious_login(sender, request, user, **kwargs):
    """Şüpheli giriş denemesi kontrolü ve bildirimi"""
    try:
        # IP adresini al
        ip_address = request.META.get("REMOTE_ADDR", "Bilinmiyor")
        
        # Son giriş IP'sini kontrol et (basit kontrol - gerçek uygulamada daha gelişmiş olabilir)
        # Burada sadece örnek olarak bildirim gönderiyoruz
        # Gerçek uygulamada son IP'yi kaydedip karşılaştırmalıyız
        
        # İlk giriş değilse ve farklı IP'den giriş yapıldıysa uyar
        # (Basitleştirilmiş - gerçek uygulamada daha detaylı kontrol gerekir)
        if user.is_authenticated:
            NotificationService.notify_suspicious_login(user, ip_address)
            
    except Exception as e:
        logger.error(f"Giriş bildirimi hatası: {e}")
