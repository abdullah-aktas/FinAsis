from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError
from .models import SubscriptionProfile

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_billing_profile(sender, instance, created, **kwargs):
    if created:
        try:
            SubscriptionProfile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            # Tablo henüz yoksa (migrasyon uygulanmamışsa) sessizce geç
            pass
