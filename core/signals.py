# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=User)
def clear_user_cache(sender, instance, **kwargs):
    """
    Kullanıcı değişikliklerinde ilgili cache'leri temizler
    """
    cache.delete_pattern(f'user_{instance.id}_*')
    logger.info(f"Kullanıcı cache'i temizlendi: {instance.username}")

@receiver(pre_save, sender=User)
def log_user_changes(sender, instance, **kwargs):
    """
    Kullanıcı değişikliklerini loglar
    """
    try:
        if instance.pk:  # Güncelleme işlemi
            old_user = User.objects.get(pk=instance.pk)
            changes = []
            
            if old_user.username != instance.username:
                changes.append(f"Kullanıcı adı: {old_user.username} -> {instance.username}")
            if old_user.email != instance.email:
                changes.append(f"E-posta: {old_user.email} -> {instance.email}")
            if old_user.is_active != instance.is_active:
                changes.append(f"Aktiflik: {old_user.is_active} -> {instance.is_active}")
            
            if changes:
                logger.info(f"Kullanıcı değişiklikleri ({instance.username}): {', '.join(changes)}")
    except User.DoesNotExist:
        pass  # Yeni kullanıcı oluşturma 