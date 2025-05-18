# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
import logging
from django.db.models import Sum

logger = logging.getLogger(__name__)


class Customer(models.Model):
    """Müşteri modeli"""
    name = models.CharField(_('Adı'), max_length=255, default='')
    company_name = models.CharField(_('Şirket Adı'), max_length=255)
    tax_number = models.CharField(_('Vergi Numarası'), max_length=20, unique=True)
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100)
    address = models.TextField(_('Adres'))
    phone = models.CharField(_('Telefon'), max_length=20)
    email = models.EmailField(_('E-posta'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    is_deleted = models.BooleanField(_('Silindi'), default=False)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    credit_score = models.IntegerField(
        _('Kredi Skoru'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ],
        default=0
    )
    invoices = models.ManyToManyField('accounting.Invoice', related_name='customers', blank=True)

    class Meta:
        verbose_name = _('Müşteri')
        verbose_name_plural = _('Müşteriler')
        ordering = ['name']
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['tax_number']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tax_number})"

    def clean(self):
        if self.credit_score < 0 or self.credit_score > 1000:
            raise ValidationError(_('Kredi skoru 0-1000 arasında olmalıdır.'))

    @property
    def total_revenue(self):
        """Müşterinin toplam gelirini hesaplar"""
        return self.invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')

    def get_credit_status(self):
        """Müşterinin kredi durumunu değerlendirir"""
        if self.credit_score >= 700:
            return 'İYİ'
        elif self.credit_score >= 500:
            return 'ORTA'
        return 'RİSKLİ'

    def get_user(self):
        return get_user_model()

