# -*- coding: utf-8 -*-
"""
Finance app models module.
Contains database models for financial operations.
"""
from django.db import models
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True) 
    is_active = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        abstract = True

class AuditableMixin(models.Model):
    # Audit alanları eklenebilir
    class Meta:
        abstract = True

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    class Meta:
        app_label = 'finance'
    
    def __str__(self):
        return self.name

class Transaction(BaseModel):
    """Finansal işlem modeli"""
    TRANSACTION_TYPES = [
        ('INCOME', _('Gelir')),
        ('EXPENSE', _('Gider')),
        ('TRANSFER', _('Transfer')),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', _('Taslak')),
        ('POSTED', _('Kaydedildi')),
        ('CANCELLED', _('İptal Edildi')),
    ]
    
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name=_('İşlem Tipi'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name=_('Durum'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Tutar'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    transaction_date = models.DateTimeField(verbose_name=_('İşlem Tarihi'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Finansal İşlem')
        verbose_name_plural = _('Finansal İşlemler')
        ordering = ['-transaction_date']

class Invoice(BaseModel):
    """Fatura modeli"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('Fatura Numarası'))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name=_('Müşteri'))
    issue_date = models.DateField(verbose_name=_('Düzenleme Tarihi'))
    due_date = models.DateField(verbose_name=_('Vade Tarihi'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Toplam Tutar'))
    
    class Meta:  # type: ignore[override]
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

    class Meta:  # type: ignore[override]
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
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Bakiye'))
    currency = models.CharField(max_length=3, default='TRY', verbose_name=_('Para Birimi'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:  # type: ignore[override]
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
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Gerçekleşen Tutar'))
    category = models.CharField(max_length=50, verbose_name=_('Kategori'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:  # type: ignore[override]
        verbose_name = _('Bütçe')
        verbose_name_plural = _('Bütçeler')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class FinancialReport(BaseModel):
    """Finansal rapor modeli"""
    TYPE_CHOICES = [
        ('BALANCE_SHEET', _('Bilanço')),
        ('INCOME_STATEMENT', _('Gelir Tablosu')),
        ('CASH_FLOW', _('Nakit Akışı')),
        ('BUDGET_VS_ACTUAL', _('Bütçe vs Gerçekleşen')),
    ]
    STATUS_CHOICES = [
        ('DRAFT', _('Taslak')),
        ('GENERATED', _('Oluşturuldu')),
        ('APPROVED', _('Onaylandı')),
    ]
    name = models.CharField(max_length=100, verbose_name=_('Rapor Adı'))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_('Rapor Tipi'))
    start_date = models.DateField(verbose_name=_('Başlangıç Tarihi'))
    end_date = models.DateField(verbose_name=_('Bitiş Tarihi'))
    parameters = models.JSONField(default=dict, verbose_name=_('Parametreler'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name=_('Durum'))

    class Meta:  # type: ignore[override]
        verbose_name = _('Finansal Rapor')
        verbose_name_plural = _('Finansal Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class Tax(BaseModel):
    """Vergi modeli"""
    TYPE_CHOICES = [
        ('VAT', _('KDV')),
        ('INCOME', _('Gelir Vergisi')),
        ('CORPORATE', _('Kurumlar Vergisi')),
        ('OTHER', _('Diğer')),
    ]
    name = models.CharField(max_length=100, verbose_name=_('Vergi Adı'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Vergi Kodu'))
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ], verbose_name=_('Vergi Oranı'))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_('Vergi Tipi'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))

    class Meta:  # type: ignore[override]
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
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Nakit Akışı')
        verbose_name_plural = _('Nakit Akışları')
        ordering = ['-start_date']
        app_label = 'finance'

    def __str__(self):
        return f"{self.period} - {self.start_date} - {self.end_date}"

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
    
    class Meta:  # type: ignore[override]
        verbose_name = 'Gelir Tablosu'
        verbose_name_plural = 'Gelir Tabloları'
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.period} - {self.start_date} - {self.end_date}"

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
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Bakiye'))
    currency = models.CharField(max_length=3, default='TRY', verbose_name=_('Para Birimi'))

    class Meta:  # type: ignore[override]
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
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='einvoices',
        verbose_name=_('Müşteri')
    )
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
    
    class Meta:  # type: ignore[override]
        verbose_name = _('E-Fatura')
        verbose_name_plural = _('E-Faturalar')
        ordering = ['-issue_date', '-created_at']

    if TYPE_CHECKING:  # pragma: no cover
        items: 'models.Manager["EInvoiceItem"]'

    def __str__(self):
        return f"{self.invoice_number} - {getattr(self.customer, 'name', '')}"
        
    def calculate_totals(self):
        """Fatura toplamlarını hesaplar"""
        items = self.items.all()  # related_name='items' ile erişim
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

    class Meta:  # type: ignore[override]
        verbose_name = _('E-Fatura Kalemi')
        verbose_name_plural = _('E-Fatura Kalemleri')
        ordering = ['invoice', 'id']

    def __str__(self):
        return f"{self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        # Satır tutarlarını hesapla
        self.line_total = self.quantity * self.unit_price
        self.tax_amount = self.line_total * (self.tax_rate / 100)
        
        super().save(*args, **kwargs)
        
        # Fatura toplamlarını güncelle
        self.invoice.calculate_totals()

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.user.get_full_name()

class Voucher(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Multi-tenancy (nullable for backfill; later enforce not null)
    tenant = models.ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=models.PROTECT, related_name='finance_vouchers')
    
    def __str__(self):
        return f"{self.employee} - {self.amount}"

class InvoiceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=models.PROTECT, related_name='finance_invoice_records')

    def __str__(self):
        return f"{self.user} - {self.month} - {self.amount}₺"

class CreditCardStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    debt = models.DecimalField(max_digits=10, decimal_places=2)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def usage_percent(self):
        return int((self.debt / self.limit) * 100) if self.limit else 0

    def __str__(self):
        return f"{self.user} - {self.name}"

class InvestmentAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    return_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.name}"

class AIConfig(models.Model):
    key = models.CharField(max_length=255, verbose_name=_('OpenAI API Anahtarı'))
    active = models.BooleanField(default=True, verbose_name=_('Aktif'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AIConfig ({'Aktif' if self.active else 'Pasif'})"


# Yeni modeller için ayrı uygulamalar oluşturulacak


# ============================================================================
# GENİŞLETİLMİŞ FİNANSAL YÖNETİM MODELLERİ
# ============================================================================

class PaymentTerm(BaseModel):
    """Ödeme vadesi/koşulları"""
    TERM_TYPES = [
        ('NET', _('Net')),
        ('EOM', _('Ay Sonu')),
        ('COD', _('Teslimatta Ödeme')),
        ('CBD', _('Nakit İndirimli')),
        ('INSTALLMENT', _('Taksitli')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('Vade Adı'))
    term_type = models.CharField(max_length=20, choices=TERM_TYPES, verbose_name=_('Vade Tipi'))
    days = models.IntegerField(default=0, verbose_name=_('Gün'))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name=_('İndirim Oranı'))
    discount_days = models.IntegerField(default=0, verbose_name=_('İndirim Günü'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Ödeme Vadesi')
        verbose_name_plural = _('Ödeme Vadeleri')
        ordering = ['days']
    
    def __str__(self):
        return f"{self.name} ({self.days} gün)"


class RecurringTransaction(BaseModel):
    """Tekrarlayan işlemler - abonelikler, kiralar vb."""
    FREQUENCY_CHOICES = [
        ('daily', _('Günlük')),
        ('weekly', _('Haftalık')),
        ('biweekly', _('2 Haftada Bir')),
        ('monthly', _('Aylık')),
        ('quarterly', _('3 Aylık')),
        ('semiannually', _('6 Aylık')),
        ('annually', _('Yıllık')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('İşlem Adı'))
    transaction_type = models.CharField(max_length=20, choices=Transaction.TRANSACTION_TYPES, verbose_name=_('İşlem Tipi'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Tutar'))
    account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name=_('Hesap'))
    category = models.ForeignKey(TransactionCategory, on_delete=models.PROTECT, verbose_name=_('Kategori'))
    
    # Tekrarlama ayarları
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name=_('Sıklık'))
    start_date = models.DateField(verbose_name=_('Başlangıç Tarihi'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('Bitiş Tarihi'))
    next_occurrence = models.DateField(verbose_name=_('Sonraki Oluşum'))
    
    # Durum
    is_paused = models.BooleanField(default=False, verbose_name=_('Duraklatıldı'))
    last_executed = models.DateField(null=True, blank=True, verbose_name=_('Son Çalıştırma'))
    execution_count = models.IntegerField(default=0, verbose_name=_('Çalıştırma Sayısı'))
    
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Tekrarlayan İşlem')
        verbose_name_plural = _('Tekrarlayan İşlemler')
        ordering = ['next_occurrence']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


class FinancialMetric(BaseModel):
    """Finansal oranlar ve metrikler"""
    METRIC_TYPES = [
        ('LIQUIDITY', _('Likidite')),
        ('PROFITABILITY', _('Karlılık')),
        ('EFFICIENCY', _('Verimlilik')),
        ('LEVERAGE', _('Kaldıraç')),
        ('MARKET', _('Piyasa')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('Metrik Adı'))
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name=_('Metrik Tipi'))
    value = models.DecimalField(max_digits=15, decimal_places=4, verbose_name=_('Değer'))
    benchmark_value = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, verbose_name=_('Referans Değer'))
    
    period_start = models.DateField(verbose_name=_('Dönem Başlangıç'))
    period_end = models.DateField(verbose_name=_('Dönem Bitiş'))
    
    # Hesaplama detayları
    formula = models.TextField(blank=True, verbose_name=_('Formül'))
    calculation_data = models.JSONField(default=dict, blank=True, verbose_name=_('Hesaplama Verisi'))
    
    notes = models.TextField(blank=True, verbose_name=_('Notlar'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Finansal Metrik')
        verbose_name_plural = _('Finansal Metrikler')
        ordering = ['-period_end', 'metric_type']
    
    def __str__(self):
        return f"{self.name} - {self.value}"


class AssetDepreciation(BaseModel):
    """Amortisman yönetimi"""
    DEPRECIATION_METHODS = [
        ('STRAIGHT_LINE', _('Doğrusal Amortisman')),
        ('DECLINING_BALANCE', _('Azalan Bakiyeler')),
        ('SUM_OF_YEARS', _('Yıllar Toplamı')),
        ('UNITS_OF_PRODUCTION', _('Üretim Miktarı')),
    ]
    
    asset_name = models.CharField(max_length=200, verbose_name=_('Varlık Adı'))
    asset_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='asset_depreciation', verbose_name=_('Varlık Hesabı'))
    accumulated_depreciation_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='accumulated_depreciation', verbose_name=_('Birikmiş Amortisman Hesabı'))
    
    # Amortisman detayları
    purchase_date = models.DateField(verbose_name=_('Satın Alma Tarihi'))
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Satın Alma Maliyeti'))
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Hurda Değeri'))
    useful_life_years = models.IntegerField(verbose_name=_('Faydalı Ömür (Yıl)'))
    
    method = models.CharField(max_length=30, choices=DEPRECIATION_METHODS, default='STRAIGHT_LINE', verbose_name=_('Amortisman Yöntemi'))
    
    # Hesaplanan değerler
    annual_depreciation = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Yıllık Amortisman'))
    accumulated_depreciation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Birikmiş Amortisman'))
    book_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Net Defter Değeri'))
    
    # Durum
    is_fully_depreciated = models.BooleanField(default=False, verbose_name=_('Tamamen Amortismana Tabi Tutuldu'))
    last_depreciation_date = models.DateField(null=True, blank=True, verbose_name=_('Son Amortisman Tarihi'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Amortisman')
        verbose_name_plural = _('Amortismanlar')
        ordering = ['purchase_date']
    
    def __str__(self):
        return f"{self.asset_name}"


class Loan(BaseModel):
    """Kredi/Borç yönetimi"""
    LOAN_TYPES = [
        ('BUSINESS', _('İşletme Kredisi')),
        ('INVESTMENT', _('Yatırım Kredisi')),
        ('MORTGAGE', _('İpotek')),
        ('PERSONAL', _('Tüketici Kredisi')),
        ('CREDIT_LINE', _('Kredi Limiti')),
        ('OTHER', _('Diğer')),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', _('Aktif')),
        ('PAID', _('Ödendi')),
        ('DEFAULTED', _('Temerrüt')),
        ('RESTRUCTURED', _('Yeniden Yapılandırıldı')),
    ]
    
    loan_name = models.CharField(max_length=200, verbose_name=_('Kredi Adı'))
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES, verbose_name=_('Kredi Tipi'))
    lender = models.CharField(max_length=200, verbose_name=_('Borç Veren'))
    
    # Kredi detayları
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Ana Para'))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Faiz Oranı (%)'))
    loan_date = models.DateField(verbose_name=_('Kredi Tarihi'))
    maturity_date = models.DateField(verbose_name=_('Vade Tarihi'))
    
    # Ödeme planı
    payment_frequency = models.CharField(max_length=20, choices=RecurringTransaction.FREQUENCY_CHOICES, verbose_name=_('Ödeme Sıklığı'))
    installment_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Taksit Tutarı'))
    
    # Güncel durum
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Kalan Bakiye'))
    total_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Ödenen'))
    total_interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Ödenen Faiz'))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name=_('Durum'))
    
    # İlişkili hesap
    liability_account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name=_('Borç Hesabı'))
    
    notes = models.TextField(blank=True, verbose_name=_('Notlar'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Kredi')
        verbose_name_plural = _('Krediler')
        ordering = ['-loan_date']
    
    def __str__(self):
        return f"{self.loan_name} - {self.lender}"


class Investment(BaseModel):
    """Yatırım portföyü yönetimi"""
    INVESTMENT_TYPES = [
        ('STOCK', _('Hisse Senedi')),
        ('BOND', _('Tahvil')),
        ('MUTUAL_FUND', _('Yatırım Fonu')),
        ('REAL_ESTATE', _('Gayrimenkul')),
        ('COMMODITY', _('Emtia')),
        ('CRYPTO', _('Kripto Para')),
        ('DEPOSIT', _('Mevduat')),
        ('OTHER', _('Diğer')),
    ]
    
    investment_name = models.CharField(max_length=200, verbose_name=_('Yatırım Adı'))
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES, verbose_name=_('Yatırım Tipi'))
    
    # Yatırım detayları
    purchase_date = models.DateField(verbose_name=_('Alım Tarihi'))
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Alım Fiyatı'))
    quantity = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('1.00'), verbose_name=_('Miktar'))
    current_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Güncel Fiyat'))
    
    # Hesaplanan değerler
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Toplam Maliyet'))
    current_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Güncel Değer'))
    unrealized_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Gerçekleşmemiş Kar/Zarar'))
    return_percentage = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Getiri (%)'))
    
    # İlişkili hesap
    investment_account = models.ForeignKey(Account, on_delete=models.PROTECT, verbose_name=_('Yatırım Hesabı'))
    
    # Satış bilgisi (eğer satıldıysa)
    sale_date = models.DateField(null=True, blank=True, verbose_name=_('Satış Tarihi'))
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_('Satış Fiyatı'))
    realized_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_('Gerçekleşen Kar/Zarar'))
    
    notes = models.TextField(blank=True, verbose_name=_('Notlar'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Yatırım')
        verbose_name_plural = _('Yatırımlar')
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.investment_name}"
    
    def save(self, *args, **kwargs):
        # Hesaplamaları yap
        self.total_cost = self.purchase_price * self.quantity
        self.current_value = self.current_price * self.quantity
        self.unrealized_gain_loss = self.current_value - self.total_cost
        if self.total_cost > 0:
            self.return_percentage = (self.unrealized_gain_loss / self.total_cost) * 100
        super().save(*args, **kwargs)


class Reconciliation(BaseModel):
    """Mutabakat kayıtları"""
    RECONCILIATION_TYPES = [
        ('BANK', _('Banka Mutabakatı')),
        ('SUPPLIER', _('Tedarikçi Mutabakatı')),
        ('CUSTOMER', _('Müşteri Mutabakatı')),
        ('INVENTORY', _('Stok Mutabakatı')),
        ('ACCOUNT', _('Hesap Mutabakatı')),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', _('Beklemede')),
        ('IN_PROGRESS', _('Devam Ediyor')),
        ('COMPLETED', _('Tamamlandı')),
        ('DISCREPANCY', _('Uyuşmazlık')),
    ]
    
    reconciliation_type = models.CharField(max_length=20, choices=RECONCILIATION_TYPES, verbose_name=_('Mutabakat Tipi'))
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('Hesap'))
    
    # Dönem
    period_start = models.DateField(verbose_name=_('Dönem Başlangıç'))
    period_end = models.DateField(verbose_name=_('Dönem Bitiş'))
    
    # Bakiyeler
    system_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Sistem Bakiyesi'))
    statement_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Ekstre Bakiyesi'))
    difference = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Fark'))
    
    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name=_('Durum'))
    
    # Detaylar
    reconciliation_data = models.JSONField(default=dict, blank=True, verbose_name=_('Mutabakat Verisi'))
    notes = models.TextField(blank=True, verbose_name=_('Notlar'))
    
    # Onay
    reconciled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Mutabakat Yapan'))
    reconciled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Mutabakat Tarihi'))
    
    class Meta:  # type: ignore[override]
        verbose_name = _('Mutabakat')
        verbose_name_plural = _('Mutabakatlar')
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.get_reconciliation_type_display()} - {self.period_end}"
    
    def save(self, *args, **kwargs):
        # Farkı hesapla
        self.difference = self.system_balance - self.statement_balance
        super().save(*args, **kwargs)