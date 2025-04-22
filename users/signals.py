from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Kullanıcı oluşturulduğunda profil oluşturur"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Kullanıcı kaydedildiğinde profilini de kaydeder"""
    # get_or_create kullanılarak profil yoksa oluşturulması sağlanır
    instance.profile, created = UserProfile.objects.get_or_create(user=instance)
    instance.profile.save() 