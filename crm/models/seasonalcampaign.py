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


class SeasonalCampaign(models.Model):
    """Sezonsal kampanya modeli"""
    CAMPAIGN_TYPES = [
        ('summer', 'Yaz Kampanyası'),
        ('winter', 'Kış Kampanyası'),
        ('spring', 'Bahar Kampanyası'),
        ('autumn', 'Sonbahar Kampanyası'),
        ('holiday', 'Tatil Kampanyası'),
    ]
    
    name = models.CharField(_('Kampanya Adı'), max_length=100)
    campaign_type = models.CharField(_('Kampanya Tipi'), max_length=20, choices=CAMPAIGN_TYPES)
    description = models.TextField(_('Açıklama'))
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    discount_rate = models.DecimalField(_('İndirim Oranı'), max_digits=5, decimal_places=2, null=True)
    min_purchase_amount = models.DecimalField(_('Minimum Alışveriş Tutarı'), max_digits=10, decimal_places=2, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sezonsal Kampanya')
        verbose_name_plural = _('Sezonsal Kampanyalar')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['campaign_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_campaign_type_display()}"

