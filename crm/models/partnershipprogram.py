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


class PartnershipProgram(models.Model):
    """İş ortaklığı programı modeli"""
    PARTNER_TYPES = [
        ('reseller', 'Bayi'),
        ('consultant', 'Danışman'),
        ('affiliate', 'Affiliate'),
        ('strategic', 'Stratejik Ortak'),
    ]
    
    name = models.CharField(_('Program Adı'), max_length=100)
    partner_type = models.CharField(_('Ortak Tipi'), max_length=20, choices=PARTNER_TYPES)
    description = models.TextField(_('Açıklama'))
    commission_rate = models.DecimalField(_('Komisyon Oranı'), max_digits=5, decimal_places=2)
    min_sales_target = models.DecimalField(_('Minimum Satış Hedefi'), max_digits=10, decimal_places=2)
    benefits = models.JSONField(_('Avantajlar'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('İş Ortaklığı Programı')
        verbose_name_plural = _('İş Ortaklığı Programları')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['partner_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_partner_type_display()}"

