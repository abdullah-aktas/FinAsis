# -*- coding: utf-8 -*-
"""
E-Fatura modülü için veritabanı modelleri.

Bu modül, elektronik fatura işlemleri için gerekli temel bileşenleri içerir.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import BaseModel, AuditableMixin, CompanyMixin
from finance.accounting.models import Account, Voucher
from apps.customers.models import Customer, Supplier


class EInvoice(BaseModel, AuditableMixin, CompanyMixin):
    """E-Fatura modelidir. Hem gelen hem giden faturaları temsil eder."""
    
    class InvoiceType(models.TextChoices):
        SALES = 'sales', _('Satış Faturası')
        PURCHASE = 'purchase', _('Alış Faturası')
        RETURN = 'return', _('İade Faturası')
    
    class InvoiceStatus(models.TextChoices):
        DRAFT = 'draft', _('Taslak')
        SENT = 'sent', _('Gönderildi')
        ACCEPTED = 'accepted', _('Kabul Edildi')
        REJECTED = 'rejected', _('Reddedildi')
        CANCELLED = 'cancelled', _('İptal Edildi')
    
    # Temel fatura bilgileri
    invoice_type = models.CharField(
        _('Fatura Tipi'),
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.SALES
    )
    status = models.CharField(
        _('Durum'),
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT
    )
    invoice_number = models.CharField(_('Fatura Numarası'), max_length=50)
    invoice_date = models.DateField(_('Fatura Tarihi'))
    due_date = models.DateField(_('Vade Tarihi'), blank=True, null=True)
    
    # İlişkili taraflar
    customer = models.ForeignKey(
        Customer,
        verbose_name=_('Müşteri'),
        on_delete=models.PROTECT,
        related_name='einvoices',
        blank=True,
        null=True
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name=_('Tedarikçi'),
        on_delete=models.PROTECT,
        related_name='einvoices',
        blank=True,
        null=True
    )
    
    # Fatura içeriği
    subtotal = models.DecimalField(
        _('Ara Toplam'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        _('Vergi Tutarı'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        _('Toplam Tutar'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(_('Para Birimi'), max_length=3, default='TRY')
    
    # E-Fatura özellikleri
    uuid = models.UUIDField(_('UUID'), blank=True, null=True)
    
    # Muhasebe entegrasyonu
    voucher = models.ForeignKey(
        Voucher,
        verbose_name=_('Fiş/Dekont'),
        on_delete=models.SET_NULL,
        related_name='einvoices',
        blank=True,
        null=True
    )
    is_posted = models.BooleanField(_('Muhasebeleşti mi?'), default=False)
    
    # Meta veriler
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('E-Fatura')
        verbose_name_plural = _('E-Faturalar')
        ordering = ['-invoice_date', '-invoice_number']
        indexes = [
            models.Index(fields=['company', 'invoice_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.get_invoice_type_display()}"
    
    def calculate_totals(self):
        """Fatura satırlarına göre toplamları hesaplar."""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.tax_amount = sum(item.tax_amount for item in items)
        self.total_amount = self.subtotal + self.tax_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total_amount'])
    
    def post_to_accounting(self):
        """Faturayı muhasebeleştirir."""
        if not self.is_posted and not self.voucher:
            self.is_posted = True
            self.save(update_fields=['is_posted'])
            return True
        return False
    
    def cancel_invoice(self):
        """Faturayı iptal eder."""
        if self.status not in [self.InvoiceStatus.CANCELLED]:
            self.status = self.InvoiceStatus.CANCELLED
            self.save(update_fields=['status'])
            return True
        return False


class EInvoiceItem(BaseModel):
    """E-Fatura kalemlerini temsil eder."""
    
    invoice = models.ForeignKey(
        EInvoice, 
        verbose_name=_('Fatura'),
        on_delete=models.CASCADE,
        related_name='items'
    )
    line_number = models.PositiveIntegerField(_('Satır Numarası'))
    description = models.CharField(_('Açıklama'), max_length=255)
    quantity = models.DecimalField(
        _('Miktar'),
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    unit = models.CharField(_('Birim'), max_length=10, default='ADET')
    unit_price = models.DecimalField(
        _('Birim Fiyat'),
        max_digits=15,
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.000001'))]
    )
    line_total = models.DecimalField(
        _('Satır Toplamı'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_rate = models.DecimalField(
        _('Vergi Oranı (%)'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    tax_amount = models.DecimalField(
        _('Vergi Tutarı'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Meta veriler
    product_code = models.CharField(_('Ürün Kodu'), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _('E-Fatura Kalemi')
        verbose_name_plural = _('E-Fatura Kalemleri')
        ordering = ['invoice', 'line_number']
        unique_together = ['invoice', 'line_number']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.line_number}: {self.description}"
    
    def save(self, *args, **kwargs):
        # Satır toplamı ve vergi tutarı hesaplama
        self.line_total = self.quantity * self.unit_price
        self.tax_amount = self.line_total * (self.tax_rate / Decimal('100.00'))
        super().save(*args, **kwargs)
        
        # Fatura toplamlarını güncelle
        self.invoice.calculate_totals() 