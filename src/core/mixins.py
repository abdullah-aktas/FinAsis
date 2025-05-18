# -*- coding: utf-8 -*-
"""
Özel mixin sınıfları.
Bu modül, proje genelinde kullanılacak özel mixin sınıflarını içerir.
"""

from django.db import models
from django.utils import timezone
from .decorators import cache_result

class TimestampMixin(models.Model):
    """
    Oluşturma ve güncelleme zamanlarını takip eden mixin.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteMixin(models.Model):
    """
    Yumuşak silme özelliği ekleyen mixin.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    class Meta:
        abstract = True

class CacheMixin:
    """
    Önbellekleme özellikleri ekleyen mixin.
    """
    @classmethod
    @cache_result(timeout=300)
    def get_cached(cls, *args, **kwargs):
        """
        Önbellekten nesne getiren metod.
        """
        return cls.objects.get(*args, **kwargs)

    @classmethod
    @cache_result(timeout=300)
    def filter_cached(cls, *args, **kwargs):
        """
        Önbellekten nesneleri filtreleyen metod.
        """
        return list(cls.objects.filter(*args, **kwargs))

class AuditMixin(models.Model):
    """
    Denetim izlerini takip eden mixin.
    """
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True

class StatusMixin(models.Model):
    """
    Durum yönetimi sağlayan mixin.
    """
    STATUS_CHOICES = (
        ('draft', 'Taslak'),
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('archived', 'Arşivlendi'),
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_status_changed'
    )

    def set_status(self, status, user=None):
        """
        Durumu güncelleyen metod.
        """
        if status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {status}")
        
        self.status = status
        self.status_changed_at = timezone.now()
        self.status_changed_by = user
        self.save()

    class Meta:
        abstract = True

class VersionMixin(models.Model):
    """
    Sürüm kontrolü sağlayan mixin.
    """
    version = models.PositiveIntegerField(default=1)
    previous_version = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Sürüm numarasını otomatik artıran save metodu.
        """
        if self.pk:
            self.previous_version = self.version
            self.version += 1
        super().save(*args, **kwargs)

    class Meta:
        abstract = True 