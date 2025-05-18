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


class Opportunity(models.Model):
    """Fırsat modeli"""
    OPPORTUNITY_STATUS_CHOICES = [
        ('open', 'Açık'),
        ('won', 'Kazanıldı'),
        ('lost', 'Kaybedildi'),
        ('dormant', 'Uyuyan'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Fırsat Adı')
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='opportunities', verbose_name='Müşteri')
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Değer')
    expected_close_date = models.DateField(verbose_name='Tahmini Kapanış Tarihi')
    status = models.CharField(max_length=20, choices=OPPORTUNITY_STATUS_CHOICES, default='open', verbose_name='Durum')
    probability = models.IntegerField(default=50, verbose_name='Olasılık (%)')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_opportunities', verbose_name='Atanan Kişi')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Fırsat'
        verbose_name_plural = 'Fırsatlar'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

