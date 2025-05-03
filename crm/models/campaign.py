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


class Campaign(models.Model):
    CAMPAIGN_TYPES = [
        ('student', 'Öğrenci İndirimi'),
        ('startup', 'Startup Paketi'),
        ('referral', 'Referans Programı'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('expired', 'Süresi Dolmuş'),
    ]
    
    name = models.CharField(_('Kampanya Adı'), max_length=100)
    campaign_type = models.CharField(_('Kampanya Tipi'), max_length=20, choices=CAMPAIGN_TYPES)
    description = models.TextField(_('Açıklama'))
    discount_rate = models.DecimalField(_('İndirim Oranı'), max_digits=5, decimal_places=2, null=True, blank=True)
    bonus_amount = models.DecimalField(_('Bonus Miktarı'), max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Kampanya')
        verbose_name_plural = _('Kampanyalar')
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    def calculate_discount(self, amount):
        if self.discount_rate:
            return amount * (self.discount_rate / Decimal('100'))
        return Decimal('0')

