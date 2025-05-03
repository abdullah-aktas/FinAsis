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


class SaleItem(models.Model):
    """Satış kalemi modeli"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name=_('Satış'))
    product_name = models.CharField(_('Ürün Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    quantity = models.DecimalField(_('Miktar'), max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('Vergi Oranı (%)'), max_digits=5, decimal_places=2, default=18.0)
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('Vergi Tutarı'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_('Toplam Tutar'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('Satış Kalemi')
        verbose_name_plural = _('Satış Kalemleri')
    
    def __str__(self):
        return f"{self.product_name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Tutarları hesapla
        self.amount = self.quantity * self.unit_price
        self.tax_amount = self.amount * (self.tax_rate / 100)
        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)


