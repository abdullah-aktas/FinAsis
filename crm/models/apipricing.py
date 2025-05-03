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


class APIPricing(models.Model):
    """API kullanım bazlı fiyatlandırma modeli"""
    PRICING_TIERS = [
        ('free', 'Ücretsiz'),
        ('basic', 'Temel'),
        ('premium', 'Premium'),
        ('enterprise', 'Kurumsal'),
    ]
    
    tier = models.CharField(_('Fiyatlandırma Kademesi'), max_length=20, choices=PRICING_TIERS)
    requests_per_month = models.IntegerField(_('Aylık İstek Limiti'))
    price_per_request = models.DecimalField(_('İstek Başı Ücret'), max_digits=10, decimal_places=4)
    base_price = models.DecimalField(_('Temel Ücret'), max_digits=10, decimal_places=2)
    features = models.JSONField(_('Özellikler'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('API Fiyatlandırması')
        verbose_name_plural = _('API Fiyatlandırmaları')
    
    def __str__(self):
        return f"{self.get_tier_display()} - {self.requests_per_month} istek/ay"

