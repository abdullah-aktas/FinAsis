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


class PremiumPackage(models.Model):
    """Premium paket modeli"""
    PACKAGE_TYPES = [
        ('basic', 'Temel Paket'),
        ('professional', 'Profesyonel Paket'),
        ('enterprise', 'Kurumsal Paket'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Aylık'),
        ('yearly', 'Yıllık'),
    ]
    
    name = models.CharField(_('Paket Adı'), max_length=100)
    package_type = models.CharField(_('Paket Tipi'), max_length=20, choices=PACKAGE_TYPES)
    description = models.TextField(_('Açıklama'))
    price = models.DecimalField(_('Fiyat'), max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(_('Fatura Döngüsü'), max_length=20, choices=BILLING_CYCLES)
    features = models.JSONField(_('Özellikler'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Premium Paket')
        verbose_name_plural = _('Premium Paketler')
    
    def __str__(self):
        return f"{self.name} - {self.get_package_type_display()}"

