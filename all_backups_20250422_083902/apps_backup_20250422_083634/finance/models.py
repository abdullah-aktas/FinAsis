from django.db import models
from django.conf import settings
from accounting.models import BaseModel
from decimal import Decimal

class Transaction(BaseModel):
    """Finansal işlem modeli"""
    TRANSACTION_TYPES = [
        ('income', 'Gelir'),
        ('expense', 'Gider'),
        ('transfer', 'Transfer'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='İşlem Tipi')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Tutar')
    description = models.TextField(verbose_name='Açıklama')
    date = models.DateField(verbose_name='İşlem Tarihi')
    category = models.CharField(max_length=100, verbose_name='Kategori')
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referans')
    
    class Meta:
        verbose_name = 'İşlem'
        verbose_name_plural = 'İşlemler'
        ordering = ['-date']
        app_label = 'finance'
        
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} {self.currency}"

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