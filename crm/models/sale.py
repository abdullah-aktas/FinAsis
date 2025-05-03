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


class Sale(models.Model):
    """Müşteri satış kaydı modeli"""
    
    STATUS_CHOICES = (
        ('draft', _('Taslak')),
        ('confirmed', _('Onaylandı')),
        ('cancelled', _('İptal Edildi')),
    )
    
    PAYMENT_CHOICES = (
        ('cash', _('Nakit')),
        ('credit', _('Kredi Kartı')),
        ('bank', _('Banka Transferi')),
        ('other', _('Diğer')),
    )
    
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='sales', verbose_name=_('Müşteri'))
    date = models.DateField(_('Satış Tarihi'), default=timezone.now)
    number = models.CharField(_('Satış Numarası'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('Vergi Tutarı'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_('Toplam Tutar'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('Ödeme Yöntemi'), max_length=20, choices=PAYMENT_CHOICES, default='cash')
    payment_date = models.DateField(_('Ödeme Tarihi'), blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='draft')
    invoice_created = models.BooleanField(_('Fatura Oluşturuldu'), default=False)
    accounting_synced = models.BooleanField(_('Muhasebe Entegrasyonu'), default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sales', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Satış')
        verbose_name_plural = _('Satışlar')
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"{self.number} - {self.customer.company_name}"
    
    def save(self, *args, **kwargs):
        # Satış numarası otomatik oluşturma
        if not self.number:
            last_sale = Sale.objects.order_by('-id').first()
            if last_sale:
                last_number = int(last_sale.number.split('-')[1])
                self.number = f"SLS-{last_number + 1:05d}"
            else:
                self.number = "SLS-00001"
        super().save(*args, **kwargs)
    
    @property
    def is_editable(self):
        return self.status == 'draft'
    
    @property
    def is_confirmed(self):
        return self.status == 'confirmed'


