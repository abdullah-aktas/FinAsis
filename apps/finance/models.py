from django.db import models
from django.conf import settings
from accounting.models import BaseModel
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class BaseModel(models.Model):
    """Temel model sınıfı"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    is_active = models.BooleanField(default=True, verbose_name=_('Aktif'))
    
    class Meta:
        abstract = True

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

class Transaction(BaseModel):
    """İşlem modeli"""
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions', verbose_name=_('Hesap'))
    date = models.DateField(verbose_name=_('İşlem Tarihi'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('Tutar'))
    type = models.CharField(max_length=10, choices=[
        ('DEBIT', _('Borç')),
        ('CREDIT', _('Alacak')),
    ], verbose_name=_('İşlem Tipi'))
    description = models.TextField(verbose_name=_('Açıklama'))
    reference = models.CharField(max_length=50, blank=True, verbose_name=_('Referans'))
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', _('Taslak')),
        ('POSTED', _('Kaydedildi')),
        ('CANCELLED', _('İptal Edildi')),
    ], default='DRAFT', verbose_name=_('Durum'))
    
    class Meta:
        verbose_name = _('İşlem')
        verbose_name_plural = _('İşlemler')
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f"{self.date} - {self.account} - {self.amount} {self.type}"

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
        ('daily', 'Günlük'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('quarterly', '3 Aylık'),
        ('yearly', 'Yıllık'),
    ]
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name='Dönem')
    start_date = models.DateField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateField(verbose_name='Bitiş Tarihi')
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Açılış Bakiyesi')
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Kapanış Bakiyesi')
    total_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Toplam Gelir')
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Toplam Gider')
    net_cash_flow = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Net Nakit Akışı')
    
    class Meta:
        verbose_name = 'Nakit Akışı'
        verbose_name_plural = 'Nakit Akışları'
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