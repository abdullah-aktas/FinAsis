# -*- coding: utf-8 -*-
"""
KOBİ Financial Analysis Models
Django modelleri for SME financial analysis and management
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json
from datetime import date, datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Company modelini import et
from ..accounting.models import Company


class KOBIFinancialAnalysis(models.Model):
    """
    KOBİ (SME) Financial Analysis Model
    Comprehensive financial health assessment for small and medium enterprises
    """
    
    ANALYSIS_TYPE_CHOICES = [
        ('MONTHLY', _('Aylık Analiz')),
        ('QUARTERLY', _('Çeyreklik Analiz')),
        ('ANNUAL', _('Yıllık Analiz')),
        ('CUSTOM', _('Özel Dönem')),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('EXCELLENT', _('Mükemmel')),
        ('GOOD', _('İyi')),
        ('FAIR', _('Orta')),
        ('POOR', _('Zayıf')),
        ('CRITICAL', _('Kritik')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Şirket'))
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, default='MONTHLY', verbose_name=_('Analiz Türü'))
    analysis_period_start = models.DateField(verbose_name=_('Analiz Başlangıç Tarihi'))
    analysis_period_end = models.DateField(verbose_name=_('Analiz Bitiş Tarihi'))
    
    # Temel finansal veriler
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Gelir'))
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Gider'))
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Net Kar'))
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Varlık'))
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Borç'))
    
    # Finansal rasyolar
    current_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Cari Oran'))
    quick_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Asit Test Oranı'))
    debt_to_equity_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Borç/Özkaynak Oranı'))
    profit_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Kar Marjı'))
    roa = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Aktif Karlılığı (ROA)'))
    roe = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Özkaynak Karlılığı (ROE)'))
    
    # Skor ve durum
    financial_health_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_('Finansal Sağlık Skoru'))
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, null=True, blank=True, verbose_name=_('Sağlık Durumu'))
    
    # Öneriler ve notlar
    recommendations = models.TextField(null=True, blank=True, verbose_name=_('Öneriler'))
    analysis_notes = models.TextField(null=True, blank=True, verbose_name=_('Analiz Notları'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    
    class Meta:
        verbose_name = _('KOBİ Finansal Analizi')
        verbose_name_plural = _('KOBİ Finansal Analizleri')
        ordering = ['-created_at']
        unique_together = ['company', 'analysis_period_start', 'analysis_period_end']
    
    def __str__(self):
        return f"{self.company.name} - {self.analysis_type} - {self.analysis_period_start}"
    
    def calculate_financial_ratios(self):
        """Finansal rasyoları otomatik hesapla"""
        try:
            # Cari oran hesaplama (varsayılan olarak aktif/pasif oranı)
            if self.total_liabilities > 0:
                self.current_ratio = self.total_assets / self.total_liabilities
            
            # Kar marjı hesaplama
            if self.total_revenue > 0:
                self.profit_margin = (self.net_profit / self.total_revenue) * 100
            
            # ROA hesaplama
            if self.total_assets > 0:
                self.roa = (self.net_profit / self.total_assets) * 100
            
            # Borç/Özkaynak oranı
            equity = self.total_assets - self.total_liabilities
            if equity > 0:
                self.debt_to_equity_ratio = self.total_liabilities / equity
                self.roe = (self.net_profit / equity) * 100
                
        except Exception as e:
            pass  # Hata durumunda sessizce geç
    
    def calculate_health_score(self):
        """Finansal sağlık skorunu hesapla"""
        score = 0
        max_score = 100
        
        # Karlılık kontrolü (30 puan)
        if self.profit_margin:
            if self.profit_margin >= 20:
                score += 30
            elif self.profit_margin >= 10:
                score += 20
            elif self.profit_margin >= 5:
                score += 10
        
        # Likidite kontrolü (25 puan)
        if self.current_ratio:
            if self.current_ratio >= 2.0:
                score += 25
            elif self.current_ratio >= 1.5:
                score += 20
            elif self.current_ratio >= 1.0:
                score += 10
        
        # Borç yönetimi (25 puan)
        if self.debt_to_equity_ratio is not None:
            if self.debt_to_equity_ratio <= 0.5:
                score += 25
            elif self.debt_to_equity_ratio <= 1.0:
                score += 20
            elif self.debt_to_equity_ratio <= 2.0:
                score += 10
        
        # Varlık verimliliği (20 puan)
        if self.roa:
            if self.roa >= 15:
                score += 20
            elif self.roa >= 10:
                score += 15
            elif self.roa >= 5:
                score += 10
        
        self.financial_health_score = Decimal(str(score))
        
        # Sağlık durumu belirleme
        if score >= 90:
            self.health_status = 'EXCELLENT'
        elif score >= 75:
            self.health_status = 'GOOD'
        elif score >= 60:
            self.health_status = 'FAIR'
        elif score >= 40:
            self.health_status = 'POOR'
        else:
            self.health_status = 'CRITICAL'
    
    def save(self, *args, **kwargs):
        """Model kaydedilirken otomatik hesaplamalar yap"""
        self.calculate_financial_ratios()
        self.calculate_health_score()
        super().save(*args, **kwargs)


class BudgetPlan(models.Model):
    """
    Budget Planning Model for SMEs
    """
    
    BUDGET_TYPE_CHOICES = [
        ('OPERATIONAL', _('Operasyonel Bütçe')),
        ('INVESTMENT', _('Yatırım Bütçesi')),
        ('CASH_FLOW', _('Nakit Akış Bütçesi')),
        ('MASTER', _('Ana Bütçe')),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', _('Taslak')),
        ('APPROVED', _('Onaylandı')),
        ('ACTIVE', _('Aktif')),
        ('COMPLETED', _('Tamamlandı')),
        ('CANCELLED', _('İptal Edildi')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Şirket'))
    budget_name = models.CharField(max_length=200, verbose_name=_('Bütçe Adı'))
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES, verbose_name=_('Bütçe Türü'))
    fiscal_year = models.IntegerField(verbose_name=_('Mali Yıl'))
    period_start = models.DateField(verbose_name=_('Dönem Başlangıcı'))
    period_end = models.DateField(verbose_name=_('Dönem Sonu'))
    
    # Bütçe tutarları
    planned_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Planlanan Gelir'))
    planned_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Planlanan Gider'))
    planned_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Planlanan Kar'))
    
    # Gerçekleşen tutarlar  
    actual_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Gerçekleşen Gelir'))
    actual_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Gerçekleşen Gider'))
    actual_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Gerçekleşen Kar'))
    
    # Varyans analizi
    revenue_variance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Gelir Varyansı'))
    expense_variance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Gider Varyansı'))
    profit_variance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Kar Varyansı'))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name=_('Durum'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notlar'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_budgets', verbose_name=_('Onaylayan'))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Onay Tarihi'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    
    class Meta:
        verbose_name = _('Bütçe Planı')
        verbose_name_plural = _('Bütçe Planları')
        ordering = ['-fiscal_year', '-created_at']
        unique_together = ['company', 'budget_name', 'fiscal_year']
    
    def __str__(self):
        return f"{self.company.name} - {self.budget_name} ({self.fiscal_year})"
    
    def calculate_variance(self):
        """Varyans hesapla"""
        self.revenue_variance = self.actual_revenue - self.planned_revenue
        self.expense_variance = self.actual_expenses - self.planned_expenses
        self.profit_variance = self.actual_profit - self.planned_profit
        self.save()
    
    def get_variance_percentage(self, field):
        """Varyans yüzdesini hesapla"""
        planned_value = getattr(self, f'planned_{field}')
        actual_value = getattr(self, f'actual_{field}')
        
        if planned_value != 0:
            return ((actual_value - planned_value) / planned_value) * 100
        return 0


class CashFlowForecast(models.Model):
    """
    Cash Flow Forecasting Model
    """
    
    FORECAST_TYPE_CHOICES = [
        ('WEEKLY', _('Haftalık')),
        ('MONTHLY', _('Aylık')),
        ('QUARTERLY', _('Çeyreklik')),
        ('ANNUAL', _('Yıllık')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Şirket'))
    forecast_name = models.CharField(max_length=200, verbose_name=_('Tahmin Adı'))
    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPE_CHOICES, verbose_name=_('Tahmin Türü'))
    forecast_date = models.DateField(verbose_name=_('Tahmin Tarihi'))
    
    # Nakit giriş kaynakları
    cash_from_sales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Satışlardan Nakit'))
    cash_from_receivables = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Alacaklardan Nakit'))
    cash_from_investments = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Yatırımlardan Nakit'))
    cash_from_loans = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Kredilerden Nakit'))
    other_cash_inflows = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Diğer Nakit Girişleri'))
    
    # Nakit çıkış kalemleri
    cash_for_operations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Operasyonel Giderler'))
    cash_for_payroll = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Bordro Ödemeleri'))
    cash_for_suppliers = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Tedarikçi Ödemeleri'))
    cash_for_taxes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Vergi Ödemeleri'))
    cash_for_investments = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Yatırım Harcamaları'))
    cash_for_loan_payments = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Kredi Ödemeleri'))
    other_cash_outflows = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Diğer Nakit Çıkışları'))
    
    # Hesaplanan değerler
    total_cash_inflows = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Nakit Girişi'))
    total_cash_outflows = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Nakit Çıkışı'))
    net_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Net Nakit Akışı'))
    opening_cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Açılış Nakit Bakiyesi'))
    closing_cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Kapanış Nakit Bakiyesi'))
    
    # Risk analizi
    cash_shortage_risk = models.BooleanField(default=False, verbose_name=_('Nakit Sıkışıklığı Riski'))
    minimum_cash_threshold = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'), verbose_name=_('Minimum Nakit Eşiği'))
    
    notes = models.TextField(null=True, blank=True, verbose_name=_('Notlar'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    
    class Meta:
        verbose_name = _('Nakit Akış Tahmini')
        verbose_name_plural = _('Nakit Akış Tahminleri')
        ordering = ['-forecast_date', '-created_at']
        unique_together = ['company', 'forecast_date', 'forecast_type']
    
    def __str__(self):
        return f"{self.company.name} - {self.forecast_name} ({self.forecast_date})"
    
    def calculate_cash_flow(self):
        """Nakit akışını hesapla"""
        # Toplam girişleri hesapla
        self.total_cash_inflows = (
            self.cash_from_sales + 
            self.cash_from_receivables + 
            self.cash_from_investments + 
            self.cash_from_loans + 
            self.other_cash_inflows
        )
        
        # Toplam çıkışları hesapla
        self.total_cash_outflows = (
            self.cash_for_operations +
            self.cash_for_payroll +
            self.cash_for_suppliers +
            self.cash_for_taxes +
            self.cash_for_investments +
            self.cash_for_loan_payments +
            self.other_cash_outflows
        )
        
        # Net nakit akışını hesapla
        self.net_cash_flow = self.total_cash_inflows - self.total_cash_outflows
        
        # Kapanış bakiyesini hesapla
        self.closing_cash_balance = self.opening_cash_balance + self.net_cash_flow
        
        # Risk analizi
        self.cash_shortage_risk = self.closing_cash_balance < self.minimum_cash_threshold
    
    def save(self, *args, **kwargs):
        """Model kaydedilirken otomatik hesaplamalar yap"""
        self.calculate_cash_flow()
        super().save(*args, **kwargs)


class ProfitabilityAnalysis(models.Model):
    """
    Profitability Analysis Model
    Detailed profitability analysis by product, service, customer segment
    """
    
    ANALYSIS_DIMENSION_CHOICES = [
        ('PRODUCT', _('Ürün Bazlı')),
        ('SERVICE', _('Hizmet Bazlı')),
        ('CUSTOMER', _('Müşteri Bazlı')),
        ('REGION', _('Bölge Bazlı')),
        ('CHANNEL', _('Kanal Bazlı')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Şirket'))
    analysis_name = models.CharField(max_length=200, verbose_name=_('Analiz Adı'))
    analysis_dimension = models.CharField(max_length=20, choices=ANALYSIS_DIMENSION_CHOICES, verbose_name=_('Analiz Boyutu'))
    dimension_value = models.CharField(max_length=200, verbose_name=_('Boyut Değeri'))  # Ürün adı, müşteri adı vs.
    
    analysis_period_start = models.DateField(verbose_name=_('Analiz Başlangıç Tarihi'))
    analysis_period_end = models.DateField(verbose_name=_('Analiz Bitiş Tarihi'))
    
    # Gelir kalemleri
    gross_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Brüt Gelir'))
    discounts = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('İndirimler'))
    returns = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('İadeler'))
    net_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Net Gelir'))
    
    # Maliyet kalemleri
    direct_costs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Direkt Maliyetler'))
    indirect_costs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Endirekt Maliyetler'))
    total_costs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Toplam Maliyetler'))
    
    # Karlılık metrikleri
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Brüt Kar'))
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Net Kar'))
    gross_profit_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Brüt Kar Marjı %'))
    net_profit_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Net Kar Marjı %'))
    
    # Birim ekonomisi
    units_sold = models.IntegerField(default=0, verbose_name=_('Satılan Birim'))
    revenue_per_unit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Birim Başına Gelir'))
    cost_per_unit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Birim Başına Maliyet'))
    profit_per_unit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Birim Başına Kar'))
    
    # Analiz notları ve öneriler
    analysis_notes = models.TextField(null=True, blank=True, verbose_name=_('Analiz Notları'))
    improvement_recommendations = models.TextField(null=True, blank=True, verbose_name=_('İyileştirme Önerileri'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    
    class Meta:
        verbose_name = _('Karlılık Analizi')
        verbose_name_plural = _('Karlılık Analizleri')
        ordering = ['-created_at']
        unique_together = ['company', 'analysis_dimension', 'dimension_value', 'analysis_period_start', 'analysis_period_end']
    
    def __str__(self):
        return f"{self.company.name} - {self.analysis_dimension} - {self.analysis_date}"
    
    def calculate_profitability_metrics(self):
        """Karlılık metriklerini hesapla"""
        # Net gelir hesapla
        self.net_revenue = self.gross_revenue - self.discounts - self.returns
        
        # Toplam maliyet hesapla
        self.total_costs = self.direct_costs + self.indirect_costs
        
        # Kar hesaplamaları
        self.gross_profit = self.net_revenue - self.direct_costs
        self.net_profit = self.net_revenue - self.total_costs
        
        # Kar marjları
        if self.net_revenue > 0:
            self.gross_profit_margin = (self.gross_profit / self.net_revenue) * 100
            self.net_profit_margin = (self.net_profit / self.net_revenue) * 100
        
        # Birim ekonomisi
        if self.units_sold > 0:
            self.revenue_per_unit = self.net_revenue / self.units_sold
            self.cost_per_unit = self.total_costs / self.units_sold
            self.profit_per_unit = self.net_profit / self.units_sold
    
    def save(self, *args, **kwargs):
        """Model kaydedilirken otomatik hesaplamalar yap"""
        self.calculate_profitability_metrics()
        super().save(*args, **kwargs)


class FinancialRatio(models.Model):
    """
    Financial Ratios Model
    Comprehensive financial ratios calculation and tracking
    """
    
    RATIO_CATEGORY_CHOICES = [
        ('LIQUIDITY', _('Likidite Oranları')),
        ('ACTIVITY', _('Faaliyet Oranları')),
        ('LEVERAGE', _('Kaldıraç Oranları')),
        ('PROFITABILITY', _('Karlılık Oranları')),
        ('MARKET', _('Piyasa Oranları')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Şirket'))
    ratio_category = models.CharField(max_length=20, choices=RATIO_CATEGORY_CHOICES, verbose_name=_('Oran Kategorisi'))
    calculation_date = models.DateField(verbose_name=_('Hesaplama Tarihi'))
    
    # Likidite oranları
    current_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Cari Oran'))
    quick_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Asit Test Oranı'))
    cash_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Nakit Oranı'))
    
    # Faaliyet oranları
    inventory_turnover = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Stok Devir Hızı'))
    receivables_turnover = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Alacak Devir Hızı'))
    asset_turnover = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Aktif Devir Hızı'))
    
    # Kaldıraç oranları
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Borç/Özkaynak'))
    debt_to_assets = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Borç/Aktif'))
    equity_multiplier = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Özkaynak Çarpanı'))
    
    # Karlılık oranları
    gross_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Brüt Kar Marjı'))
    operating_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Faaliyet Kar Marjı'))
    net_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Net Kar Marjı'))
    roa = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Aktif Karlılığı'))
    roe = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Özkaynak Karlılığı'))
    
    # Benchmark veriler
    industry_benchmark = models.JSONField(null=True, blank=True, verbose_name=_('Sektör Benchmarkı'))
    peer_comparison = models.JSONField(null=True, blank=True, verbose_name=_('Rakip Karşılaştırması'))
    
    # Analiz notları
    analysis_notes = models.TextField(null=True, blank=True, verbose_name=_('Analiz Notları'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    
    class Meta:
        verbose_name = _('Finansal Oran')
        verbose_name_plural = _('Finansal Oranlar')
        ordering = ['-calculation_date', '-created_at']
        unique_together = ['company', 'ratio_category', 'calculation_date']
    
    def __str__(self):
        return f"{self.company.name} - {self.ratio_category} - {self.calculation_date}"


class SMEBenchmark(models.Model):
    """
    SME Benchmark Data Model
    Industry benchmarks for small and medium enterprises
    """
    
    industry_code = models.CharField(max_length=20, verbose_name=_('Sektör Kodu'))
    industry_name = models.CharField(max_length=200, verbose_name=_('Sektör Adı'))
    company_size_category = models.CharField(max_length=50, verbose_name=_('Şirket Büyüklük Kategorisi'))  # Mikro, Küçük, Orta
    
    # Benchmark oranlar
    benchmark_current_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Benchmark Cari Oran'))
    benchmark_quick_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Benchmark Asit Test'))
    benchmark_debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Benchmark Borç/Özkaynak'))
    benchmark_profit_margin = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Benchmark Kar Marjı'))
    benchmark_roa = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Benchmark ROA'))
    benchmark_roe = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Benchmark ROE'))
    
    # İstatistiksel veriler
    sample_size = models.IntegerField(verbose_name=_('Örneklem Büyüklüğü'))
    data_year = models.IntegerField(verbose_name=_('Veri Yılı'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('Son Güncelleme'))
    
    class Meta:
        verbose_name = _('KOBİ Benchmark Verisi')
        verbose_name_plural = _('KOBİ Benchmark Verileri')
        ordering = ['industry_name', 'company_size_category']
        unique_together = ['industry_code', 'company_size_category', 'data_year']
    
    def __str__(self):
        return f"{self.industry_name} - {self.company_size_category} ({self.data_year})"
