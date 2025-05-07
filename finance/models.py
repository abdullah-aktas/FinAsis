# -*- coding: utf-8 -*-
"""
Finance app models module.
Contains database models for financial operations.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True) 
    is_active = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        abstract = True

class Transaction(BaseModel):
    """Finansal işlem modeli"""
    TRANSACTION_TYPES = [
        ('INCOME', _('Gelir')),
        ('EXPENSE', _('Gider')),
        ('TRANSFER', _('Transfer')),
    ]
    
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name=_('İşlem Tipi'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Tutar'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    transaction_date = models.DateTimeField(verbose_name=_('İşlem Tarihi'))
    
    class Meta:
        verbose_name = _('Finansal İşlem')
        verbose_name_plural = _('Finansal İşlemler')
        ordering = ['-transaction_date']

class Invoice(BaseModel):
    """Fatura modeli"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('Fatura Numarası'))
    customer = models.ForeignKey('crm.Customer', on_delete=models.PROTECT, verbose_name=_('Müşteri'))
    issue_date = models.DateField(verbose_name=_('Düzenleme Tarihi'))
    due_date = models.DateField(verbose_name=_('Vade Tarihi'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Toplam Tutar'))
    
    class Meta:
        verbose_name = _('Fatura') 
        verbose_name_plural = _('Faturalar')
        ordering = ['-issue_date']

class TransactionCategory(BaseModel):
    """İşlem kategorisi modeli"""
    name = models.CharField(max_length=100, verbose_name=_('Kategori Adı'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Kategori Kodu'))
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, 
                             related_name='children', verbose_name=_('Üst Kategori'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:
        verbose_name = _('İşlem Kategorisi')
        verbose_name_plural = _('İşlem Kategorileri')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Account(BaseModel):
    """Hesap modeli"""
    name = models.CharField(max_length=100, verbose_name=_('Hesap Adı'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Hesap Kodu'))
    type = models.CharField(max_length=20, choices=[
        ('ASSET', _('Varlık')),
        ('LIABILITY', _('Borç')),
        ('EQUITY', _('Özkaynak')),
        ('REVENUE', _('Gelir')),
        ('EXPENSE', _('Gider')),
    ], verbose_name=_('Hesap Tipi'))
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('Bakiye'))
    currency = models.CharField(max_length=3, default='TRY', verbose_name=_('Para Birimi'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:
        verbose_name = _('Hesap')
        verbose_name_plural = _('Hesaplar')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Budget(BaseModel):
    """Bütçe modeli"""
    name = models.CharField(max_length=100, verbose_name=_('Bütçe Adı'))
    start_date = models.DateField(verbose_name=_('Başlangıç Tarihi'))
    end_date = models.DateField(verbose_name=_('Bitiş Tarihi'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Bütçe Tutarı'))
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('Gerçekleşen Tutar'))
    category = models.CharField(max_length=50, verbose_name=_('Kategori'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:
        verbose_name = _('Bütçe')
        verbose_name_plural = _('Bütçeler')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class FinancialReport(BaseModel):
    """Finansal rapor modeli"""
    name = models.CharField(max_length=100, verbose_name=_('Rapor Adı'))
    type = models.CharField(max_length=20, choices=[
        ('BALANCE_SHEET', _('Bilanço')),
        ('INCOME_STATEMENT', _('Gelir Tablosu')),
        ('CASH_FLOW', _('Nakit Akışı')),
        ('BUDGET_VS_ACTUAL', _('Bütçe vs Gerçekleşen')),
    ], verbose_name=_('Rapor Tipi'))
    start_date = models.DateField(verbose_name=_('Başlangıç Tarihi'))
    end_date = models.DateField(verbose_name=_('Bitiş Tarihi'))
    parameters = models.JSONField(default=dict, verbose_name=_('Parametreler'))
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', _('Taslak')),
        ('GENERATED', _('Oluşturuldu')),
        ('APPROVED', _('Onaylandı')),
    ], default='DRAFT', verbose_name=_('Durum'))

    class Meta:
        verbose_name = _('Finansal Rapor')
        verbose_name_plural = _('Finansal Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class Tax(BaseModel):
    """Vergi modeli"""
    name = models.CharField(max_length=100, verbose_name=_('Vergi Adı'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Vergi Kodu'))
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ], verbose_name=_('Vergi Oranı'))
    type = models.CharField(max_length=20, choices=[
        ('VAT', _('KDV')),
        ('INCOME', _('Gelir Vergisi')),
        ('CORPORATE', _('Kurumlar Vergisi')),
        ('OTHER', _('Diğer')),
    ], verbose_name=_('Vergi Tipi'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:
        verbose_name = _('Vergi')
        verbose_name_plural = _('Vergiler')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.rate}%)"

class CashFlow(BaseModel):
    """Nakit akışı modeli"""
    PERIOD_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('monthly', _('Aylık')),
        ('quarterly', _('3 Aylık')),
        ('yearly', _('Yıllık')),
    ]
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name=_('Dönem'))
    start_date = models.DateField(verbose_name=_('Başlangıç Tarihi'))
    end_date = models.DateField(verbose_name=_('Bitiş Tarihi'))
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Açılış Bakiyesi'))
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Kapanış Bakiyesi'))
    total_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Toplam Gelir'))
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Toplam Gider'))
    net_cash_flow = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Net Nakit Akışı'))
    
    class Meta:
        verbose_name = _('Nakit Akışı')
        verbose_name_plural = _('Nakit Akışları')
        ordering = ['-start_date']
        app_label = 'finance'

    def __str__(self):
        return f"{self.get_period_display()} - {self.start_date} - {self.end_date}"

class IncomeStatement(BaseModel):
    """Gelir tablosu modeli"""
    PERIOD_CHOICES = [
        ('monthly', 'Aylık'),
        ('quarterly', '3 Aylık'),
        ('yearly', 'Yıllık'),
    ]
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name='Dönem')
    start_date = models.DateField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateField(verbose_name='Bitiş Tarihi')
    revenue = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Gelir')
    cost_of_goods_sold = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Satılan Malın Maliyeti')
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Brüt Kar')
    operating_expenses = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='İşletme Giderleri')
    operating_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='İşletme Karı')
    other_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Diğer Gelirler')
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Diğer Giderler')
    net_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Net Kar')
    
    class Meta:
        verbose_name = 'Gelir Tablosu'
        verbose_name_plural = 'Gelir Tabloları'
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.get_period_display()} - {self.start_date} - {self.end_date}"

    def save(self, *args, **kwargs):
        # Brüt kar hesaplama
        self.gross_profit = self.revenue - self.cost_of_goods_sold
        
        # İşletme karı hesaplama
        self.operating_income = self.gross_profit - self.operating_expenses
        
        # Net kar hesaplama
        self.net_income = self.operating_income + self.other_income - self.other_expenses
        
        super().save(*args, **kwargs)

class BankAccount(BaseModel):
    """Banka hesabı modeli"""
    account_name = models.CharField(max_length=100, verbose_name=_('Hesap Adı'))
    account_number = models.CharField(max_length=50, verbose_name=_('Hesap Numarası'))
    bank_name = models.CharField(max_length=100, verbose_name=_('Banka Adı'))
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('Bakiye'))
    currency = models.CharField(max_length=3, default='TRY', verbose_name=_('Para Birimi'))

    class Meta:
        verbose_name = _('Banka Hesabı')
        verbose_name_plural = _('Banka Hesapları')
        ordering = ['bank_name', 'account_name']

    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"

class EInvoice(BaseModel):
    """E-Fatura modeli"""
    INVOICE_TYPE_CHOICES = [
        ('SALES', _('Satış Faturası')),
        ('PURCHASE', _('Alış Faturası')),
        ('RETURN', _('İade Faturası'))
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', _('Taslak')),
        ('PENDING', _('Beklemede')), 
        ('SENT', _('Gönderildi')),
        ('ACCEPTED', _('Kabul Edildi')),
        ('REJECTED', _('Reddedildi')),
        ('CANCELLED', _('İptal Edildi'))
    ]

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('Fatura Numarası'))
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, verbose_name=_('Fatura Tipi'))
    issue_date = models.DateField(verbose_name=_('Düzenleme Tarihi'))
    due_date = models.DateField(verbose_name=_('Vade Tarihi'))
    
    # customer = models.ForeignKey(
    #     'customers.Customer',  # <-- Doğru import path'i ekledik
    #     on_delete=models.PROTECT,
    #     related_name='einvoices',
    #     verbose_name=_('Müşteri')
    # )
    
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Ara Toplam'))
    tax_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Vergi Toplamı'))
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Genel Toplam'))
    currency = models.CharField(max_length=3, default='TRY', verbose_name=_('Para Birimi'))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name=_('Durum'))
    note = models.TextField(blank=True, null=True, verbose_name=_('Not'))
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_('UUID'))
    xml_content = models.TextField(blank=True, null=True, verbose_name=_('XML İçeriği'))
    
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Gönderim Zamanı'))
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Kabul Zamanı'))
    
    class Meta:
        verbose_name = _('E-Fatura')
        verbose_name_plural = _('E-Faturalar')
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"
        
    def calculate_totals(self):
        """Fatura toplamlarını hesaplar"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.tax_total = sum(item.tax_amount for item in items)
        self.total = self.subtotal + self.tax_total
        self.save()

class EInvoiceItem(BaseModel):
    """E-Fatura kalemlerini temsil eder"""
    invoice = models.ForeignKey(
        EInvoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Fatura')
    )
    # product = models.ForeignKey(
    #     'products.Product',
    #     on_delete=models.PROTECT,
    #     related_name='einvoice_items',
    #     verbose_name=_('Ürün')
    # )
    quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name=_('Miktar'))
    unit = models.CharField(max_length=10, default='ADET', verbose_name=_('Birim'))
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Birim Fiyat'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Vergi Oranı (%)'))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Vergi Tutarı'))
    line_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Satır Toplamı'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('Açıklama'))

    class Meta:
        verbose_name = _('E-Fatura Kalemi')
        verbose_name_plural = _('E-Fatura Kalemleri')
        ordering = ['invoice', 'id']

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        # Satır tutarlarını hesapla
        self.line_total = self.quantity * self.unit_price
        self.tax_amount = self.line_total * (self.tax_rate / 100)
        
        super().save(*args, **kwargs)
        
        # Fatura toplamlarını güncelle
        self.invoice.calculate_totals()

class Employee(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.user.get_full_name()

class Voucher(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee} - {self.amount}"