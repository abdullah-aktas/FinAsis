from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import (
    CheckCategory, CheckType, CheckRule,
    CheckResult, CheckSchedule
)
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CheckCategory)
def clear_category_cache(sender, instance, **kwargs):
    """
    Kategori değişikliklerinde ilgili cache'leri temizler.
    """
    cache.delete_pattern('check_category_*')
    logger.info(f"Kategori cache'i temizlendi: {instance.name}")

@receiver(post_save, sender=CheckType)
def clear_type_cache(sender, instance, **kwargs):
    """
    Kontrol tipi değişikliklerinde ilgili cache'leri temizler.
    """
    cache.delete_pattern('check_type_*')
    logger.info(f"Kontrol tipi cache'i temizlendi: {instance.name}")

@receiver(post_save, sender=CheckRule)
def clear_rule_cache(sender, instance, **kwargs):
    """
    Kural değişikliklerinde ilgili cache'leri temizler.
    """
    cache.delete_pattern('check_rule_*')
    logger.info(f"Kural cache'i temizlendi: {instance.name}")

@receiver(post_save, sender=CheckResult)
def clear_result_cache(sender, instance, **kwargs):
    """
    Sonuç değişikliklerinde ilgili cache'leri temizler.
    """
    cache.delete_pattern('check_result_*')
    cache.delete('check_results_statistics')
    logger.info(f"Sonuç cache'i temizlendi: {instance.check_type.name}")

@receiver(post_save, sender=CheckSchedule)
def clear_schedule_cache(sender, instance, **kwargs):
    """
    Zamanlama değişikliklerinde ilgili cache'leri temizler.
    """
    cache.delete_pattern('check_schedule_*')
    logger.info(f"Zamanlama cache'i temizlendi: {instance.check_type.name}")

@receiver(pre_save, sender=CheckResult)
def calculate_duration(sender, instance, **kwargs):
    """
    Kontrol sonucunun süresini hesaplar.
    """
    if instance.completed_at and instance.started_at:
        instance.duration = instance.completed_at - instance.started_at

@receiver(post_delete, sender=CheckCategory)
def handle_category_deletion(sender, instance, **kwargs):
    """
    Kategori silindiğinde ilgili kontrolleri devre dışı bırakır.
    """
    CheckType.objects.filter(category=instance).update(is_active=False)
    logger.warning(f"Kategori silindi, ilgili kontroller devre dışı bırakıldı: {instance.name}")

@receiver(post_delete, sender=CheckType)
def handle_type_deletion(sender, instance, **kwargs):
    """
    Kontrol tipi silindiğinde ilgili kuralları ve zamanlamaları siler.
    """
    CheckRule.objects.filter(check_type=instance).delete()
    CheckSchedule.objects.filter(check_type=instance).delete()
    logger.warning(f"Kontrol tipi silindi, ilgili kurallar ve zamanlamalar silindi: {instance.name}") 