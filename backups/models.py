# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from datetime import datetime

class BackupConfig(models.Model):
    BACKUP_TYPES = (
        ('full', 'Tam Yedek'),
        ('incremental', 'Artırımlı Yedek'),
        ('differential', 'Fark Yedek'),
    )

    STORAGE_TYPES = (
        ('local', 'Yerel Depolama'),
        ('s3', 'Amazon S3'),
        ('azure', 'Azure Blob'),
        ('gcp', 'Google Cloud Storage'),
    )

    name = models.CharField(_('Yedekleme Adı'), max_length=100)
    backup_type = models.CharField(_('Yedekleme Tipi'), max_length=20, choices=BACKUP_TYPES)
    storage_type = models.CharField(_('Depolama Tipi'), max_length=20, choices=STORAGE_TYPES)
    schedule = models.CharField(_('Zamanlama'), max_length=100)  # Cron format
    retention_days = models.IntegerField(_('Saklama Süresi (Gün)'), default=30)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Yedekleme Yapılandırması')
        verbose_name_plural = _('Yedekleme Yapılandırmaları')
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['backup_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_backup_type_display()})"

class BackupStorage(models.Model):
    config = models.ForeignKey(BackupConfig, on_delete=models.CASCADE, related_name='storages')
    storage_path = models.CharField(_('Depolama Yolu'), max_length=255)
    credentials = models.JSONField(_('Kimlik Bilgileri'), default=dict)
    is_encrypted = models.BooleanField(_('Şifrelenmiş'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Yedekleme Depolama')
        verbose_name_plural = _('Yedekleme Depolamaları')
        indexes = [
            models.Index(fields=['is_encrypted']),
        ]

    def __str__(self):
        return f"{self.config.name} - {self.storage_path}"

class BackupRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('restored', 'Geri Yüklendi'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey(BackupConfig, on_delete=models.CASCADE, related_name='records')
    storage = models.ForeignKey(BackupStorage, on_delete=models.CASCADE, related_name='records')
    backup_path = models.CharField(_('Yedek Yolu'), max_length=255)
    size_bytes = models.BigIntegerField(_('Boyut (Bayt)'), default=0)
    checksum = models.CharField(_('Kontrol Toplamı'), max_length=64)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(_('Başlangıç Zamanı'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Tamamlanma Zamanı'), null=True, blank=True)
    error_message = models.TextField(_('Hata Mesajı'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Yedekleme Kaydı')
        verbose_name_plural = _('Yedekleme Kayıtları')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['config', 'status']),
        ]

    def __str__(self):
        return f"{self.config.name} - {self.created_at}"

class BackupLog(models.Model):
    record = models.ForeignKey(BackupRecord, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(_('Seviye'), max_length=20)
    message = models.TextField(_('Mesaj'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Yedekleme Logu')
        verbose_name_plural = _('Yedekleme Logları')
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.record.config.name} - {self.level} - {self.created_at}" 