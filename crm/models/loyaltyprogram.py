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


class LoyaltyProgram(models.Model):
    """Müşteri sadakat programı modeli"""
    LEVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    name = models.CharField(_('Program Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    points_per_purchase = models.DecimalField(_('Alışveriş Başına Puan'), max_digits=10, decimal_places=2)
    points_to_currency = models.DecimalField(_('Puan/TL Oranı'), max_digits=10, decimal_places=2)
    min_purchase_for_points = models.DecimalField(_('Minimum Alışveriş Tutarı'), max_digits=10, decimal_places=2)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sadakat Programı')
        verbose_name_plural = _('Sadakat Programları')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name

