from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone
import logging

from .models import SubscriptionProfile

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def ensure_billing_profile(sender, instance, created, **kwargs):
    if created:
        try:
            SubscriptionProfile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            # Tablo henüz yoksa (migrasyon uygulanmamışsa) sessizce geç
            pass


@receiver(post_save, sender=SubscriptionProfile)
def notify_subscription_changes(sender, instance, created, **kwargs):
    """Abonelik değişikliklerinde bildirim gönder"""
    try:
        from common.services.notification_service import NotificationService
        
        if created:
            # Yeni abonelik aktifleştirildi
            if instance.status == "active":
                NotificationService.notify_subscription_activated(instance, instance.user)
        else:
            # Abonelik durumu değişti
            # Abonelik süresi dolmak üzere kontrolü
            if hasattr(instance, 'end_date') and instance.end_date:
                days_remaining = (instance.end_date - timezone.now()).days
                if 0 < days_remaining <= 7:
                    NotificationService.notify_subscription_expiring(instance, instance.user, days_remaining)
            
            # Abonelik iptal edildi veya süresi doldu
            if instance.status in ["canceled", "past_due"]:
                title = "⚠️ Aboneliğiniz Sonlandı"
                message = f"Aboneliğiniz {instance.status} durumuna geçti.\n\n"
                message += "Hizmetlerinize kesintisiz devam etmek için aboneliğinizi yenileyin."
                
                NotificationService.send_notification(
                    user=instance.user,
                    title=title,
                    message=message,
                    notification_type="warning",
                    priority="high",
                    action_url="/billing/portal/",
                    category="subscription",
                    module="billing",
                    send_email=True,
                )
                
    except Exception as e:
        logger.error(f"Abonelik bildirimi hatası: {e}")
