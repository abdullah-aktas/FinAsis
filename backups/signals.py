# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import BackupConfig, BackupRecord, BackupLog
from .tasks import create_backup, cleanup_old_backups
import logging
import os

logger = logging.getLogger(__name__)

@receiver(post_save, sender=BackupConfig)
def handle_backup_config_save(sender, instance, created, **kwargs):
    """
    Yedekleme yapılandırması kaydedildiğinde tetiklenir.
    """
    if created and instance.is_active:
        logger.info(f"Yeni yedekleme yapılandırması oluşturuldu: {instance.name}")
        # İlk yedeklemeyi başlat
        create_backup.delay(instance.id)

@receiver(post_save, sender=BackupRecord)
def handle_backup_record_save(sender, instance, created, **kwargs):
    """
    Yedekleme kaydı kaydedildiğinde tetiklenir.
    """
    if created:
        logger.info(f"Yeni yedekleme kaydı oluşturuldu: {instance.id}")
    elif instance.status == 'completed':
        logger.info(f"Yedekleme tamamlandı: {instance.id}")
        # Eski yedekleri temizle
        cleanup_old_backups.delay()

@receiver(pre_delete, sender=BackupRecord)
def handle_backup_record_delete(sender, instance, **kwargs):
    """
    Yedekleme kaydı silinmeden önce tetiklenir.
    """
    try:
        # Yedek dosyasını sil
        if instance.backup_path and os.path.exists(instance.backup_path):
            os.remove(instance.backup_path)
            logger.info(f"Yedek dosyası silindi: {instance.backup_path}")
    except Exception as e:
        logger.error(f"Yedek dosyası silinirken hata oluştu: {str(e)}")

@receiver(post_save, sender=BackupLog)
def handle_backup_log_save(sender, instance, created, **kwargs):
    """
    Yedekleme logu kaydedildiğinde tetiklenir.
    """
    if created:
        logger.info(f"Yeni log kaydı oluşturuldu: {instance.level} - {instance.message}")
        # Hata durumunda bildirim gönder
        if instance.level == 'error':
            send_error_notification(instance)

def send_error_notification(log):
    """
    Hata bildirimi gönderir.
    """
    # Bildirim gönderme mantığı
    pass 