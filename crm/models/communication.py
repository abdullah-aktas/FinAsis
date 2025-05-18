# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounting.models import BaseModel, Account
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Communication(models.Model):
    """İletişim kaydı modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='communications')
    contact = models.ForeignKey('crm.Contact', on_delete=models.SET_NULL, null=True, related_name='communications')
    type = models.CharField(_('Tür'), max_length=20, choices=[
        ('CALL', _('Telefon Görüşmesi')),
        ('EMAIL', _('E-posta')),
        ('MEETING', _('Toplantı')),
        ('CHAT', _('Sohbet')),
        ('LETTER', _('Mektup')),
    ])
    subject = models.CharField(_('Konu'), max_length=255)
    content = models.TextField(_('İçerik'))
    direction = models.CharField(_('Yön'), max_length=10, choices=[
        ('INBOUND', _('Gelen')),
        ('OUTBOUND', _('Giden')),
    ])
    status = models.CharField(_('Durum'), max_length=20, choices=[
        ('PENDING', _('Beklemede')),
        ('COMPLETED', _('Tamamlandı')),
        ('FAILED', _('Başarısız')),
    ])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='communications')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('İletişim Kaydı')
        verbose_name_plural = _('İletişim Kayıtları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['contact']),
            models.Index(fields=['type']),
            models.Index(fields=['direction']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.subject}"

