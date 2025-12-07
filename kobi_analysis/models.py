# -*- coding: utf-8 -*-
"""
KOBİ Financial Analysis Models
Django modelleri for SME financial analysis and management
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Company modelini import et
from accounting.models import Company


class KOBIFinancialAnalysis(models.Model):
    """
    KOBİ (SME) Financial Analysis Model
    Comprehensive financial health assessment for small and medium enterprises
    """

    ANALYSIS_TYPE_CHOICES = [
        ("MONTHLY", _("Aylık Analiz")),
        ("QUARTERLY", _("Çeyreklik Analiz")),
        ("ANNUAL", _("Yıllık Analiz")),
        ("CUSTOM", _("Özel Dönem")),
    ]

    HEALTH_STATUS_CHOICES = [
        ("EXCELLENT", _("Mükemmel")),
        ("GOOD", _("İyi")),
        ("FAIR", _("Orta")),
        ("POOR", _("Zayıf")),
        ("CRITICAL", _("Kritik")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    analysis_type = models.CharField(
        max_length=20,
        choices=ANALYSIS_TYPE_CHOICES,
        default="MONTHLY",
        verbose_name=_("Analiz Türü"),
    )
    analysis_period_start = models.DateField(verbose_name=_("Analiz Başlangıç Tarihi"))
    analysis_period_end = models.DateField(verbose_name=_("Analiz Bitiş Tarihi"))

    # Temel finansal veriler
    total_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Gelir"),
    )
    total_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Gider"),
    )
    net_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Net Kar"),
    )
    total_assets = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Varlık"),
    )
    total_liabilities = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Borç"),
    )

    # Finansal rasyolar
    current_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Cari Oran"),
    )
    quick_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Asit Test Oranı"),
    )
    debt_to_equity_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Borç/Özkaynak Oranı"),
    )
    profit_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Kar Marjı"),
    )
    roa = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Aktif Karlılığı (ROA)"),
    )
    roe = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Özkaynak Karlılığı (ROE)"),
    )

    # Skor ve durum
    financial_health_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Finansal Sağlık Skoru"),
    )
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Sağlık Durumu"),
    )

    # Öneriler ve notlar
    recommendations = models.TextField(
        null=True, blank=True, verbose_name=_("Öneriler")
    )
    analysis_notes = models.TextField(
        null=True, blank=True, verbose_name=_("Analiz Notları")
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )

    class Meta:
        verbose_name = _("KOBİ Finansal Analizi")
        verbose_name_plural = _("KOBİ Finansal Analizleri")
        ordering = ["-created_at"]
        unique_together = ["company", "analysis_period_start", "analysis_period_end"]

    def __str__(self):
        return (
            f"{self.company.name} - {self.analysis_type} - {self.analysis_period_start}"
        )

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

        except Exception:
            pass  # Hata durumunda sessizce geç

    def calculate_health_score(self):
        """Finansal sağlık skorunu hesapla"""
        score = 0

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
            self.health_status = "EXCELLENT"
        elif score >= 75:
            self.health_status = "GOOD"
        elif score >= 60:
            self.health_status = "FAIR"
        elif score >= 40:
            self.health_status = "POOR"
        else:
            self.health_status = "CRITICAL"

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
        ("OPERATIONAL", _("Operasyonel Bütçe")),
        ("INVESTMENT", _("Yatırım Bütçesi")),
        ("CASH_FLOW", _("Nakit Akış Bütçesi")),
        ("MASTER", _("Ana Bütçe")),
    ]

    STATUS_CHOICES = [
        ("DRAFT", _("Taslak")),
        ("APPROVED", _("Onaylandı")),
        ("ACTIVE", _("Aktif")),
        ("COMPLETED", _("Tamamlandı")),
        ("CANCELLED", _("İptal Edildi")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    budget_name = models.CharField(max_length=200, verbose_name=_("Bütçe Adı"))
    budget_type = models.CharField(
        max_length=20, choices=BUDGET_TYPE_CHOICES, verbose_name=_("Bütçe Türü")
    )
    fiscal_year = models.IntegerField(verbose_name=_("Mali Yıl"))
    period_start = models.DateField(verbose_name=_("Dönem Başlangıcı"))
    period_end = models.DateField(verbose_name=_("Dönem Sonu"))

    # Bütçe tutarları
    planned_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Planlanan Gelir"),
    )
    planned_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Planlanan Gider"),
    )
    planned_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Planlanan Kar"),
    )

    # Gerçekleşen tutarlar
    actual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Gerçekleşen Gelir"),
    )
    actual_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Gerçekleşen Gider"),
    )
    actual_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Gerçekleşen Kar"),
    )

    # Varyans analizi
    revenue_variance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Gelir Varyansı"),
    )
    expense_variance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Gider Varyansı"),
    )
    profit_variance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Kar Varyansı"),
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="DRAFT", verbose_name=_("Durum")
    )
    notes = models.TextField(null=True, blank=True, verbose_name=_("Notlar"))

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_budgets",
        verbose_name=_("Onaylayan"),
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Onay Tarihi")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )

    class Meta:
        verbose_name = _("Bütçe Planı")
        verbose_name_plural = _("Bütçe Planları")
        ordering = ["-fiscal_year", "-created_at"]
        unique_together = ["company", "budget_name", "fiscal_year"]

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
        planned_value = getattr(self, f"planned_{field}")
        actual_value = getattr(self, f"actual_{field}")

        if planned_value != 0:
            return ((actual_value - planned_value) / planned_value) * 100
        return 0

    @property
    def variance_percentage(self):
        """Genel varyans yüzdesi"""
        if self.planned_revenue > 0:
            return (
                (self.actual_revenue - self.planned_revenue) / self.planned_revenue
            ) * 100
        return 0


class BudgetLineItem(models.Model):
    """
    Budget Line Item - Bütçe Detay Kalemleri
    """

    CATEGORY_CHOICES = [
        ("REVENUE", _("Gelir")),
        ("EXPENSE", _("Gider")),
        ("ASSET", _("Varlık")),
        ("LIABILITY", _("Borç")),
    ]

    budget = models.ForeignKey(
        BudgetPlan,
        on_delete=models.CASCADE,
        related_name="line_items",
        verbose_name=_("Bütçe"),
    )
    line_item_name = models.CharField(max_length=200, verbose_name=_("Kalem Adı"))
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("Kategori")
    )

    planned_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Planlanan Tutar"),
    )
    actual_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Gerçekleşen Tutar"),
    )
    variance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Varyans"),
    )

    notes = models.TextField(null=True, blank=True, verbose_name=_("Notlar"))

    class Meta:
        verbose_name = _("Bütçe Kalemi")
        verbose_name_plural = _("Bütçe Kalemleri")
        ordering = ["category", "line_item_name"]

    def __str__(self):
        return f"{self.line_item_name} - {self.budget.budget_name}"

    def calculate_variance(self):
        """Varyansı hesapla"""
        self.variance = self.actual_amount - self.planned_amount
        self.save()


class CashFlowForecast(models.Model):
    """
    Cash Flow Forecasting Model
    """

    FORECAST_TYPE_CHOICES = [
        ("WEEKLY", _("Haftalık")),
        ("MONTHLY", _("Aylık")),
        ("QUARTERLY", _("Çeyreklik")),
        ("ANNUAL", _("Yıllık")),
    ]

    CONFIDENCE_CHOICES = [
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    forecast_name = models.CharField(max_length=200, verbose_name=_("Tahmin Adı"))
    forecast_type = models.CharField(
        max_length=20, choices=FORECAST_TYPE_CHOICES, verbose_name=_("Tahmin Türü")
    )
    forecast_date = models.DateField(verbose_name=_("Tahmin Tarihi"))
    forecast_period_start = models.DateField(
        verbose_name=_("Tahmin Dönemi Başlangıç"), null=True, blank=True
    )
    forecast_period_end = models.DateField(
        verbose_name=_("Tahmin Dönemi Bitiş"), null=True, blank=True
    )
    confidence_level = models.CharField(
        max_length=10,
        choices=CONFIDENCE_CHOICES,
        default="MEDIUM",
        verbose_name=_("Güven Seviyesi"),
    )

    # Nakit giriş kaynakları
    cash_from_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Satışlardan Nakit"),
    )
    cash_from_receivables = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Alacaklardan Nakit"),
    )
    cash_from_investments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Yatırımlardan Nakit"),
    )
    cash_from_loans = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Kredilerden Nakit"),
    )
    other_cash_inflows = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Diğer Nakit Girişleri"),
    )

    # Nakit çıkış kalemleri
    cash_for_operations = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Operasyonel Giderler"),
    )
    cash_for_payroll = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Bordro Ödemeleri"),
    )
    cash_for_suppliers = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tedarikçi Ödemeleri"),
    )
    cash_for_taxes = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Vergi Ödemeleri"),
    )
    cash_for_investments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Yatırım Harcamaları"),
    )
    cash_for_loan_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Kredi Ödemeleri"),
    )
    other_cash_outflows = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Diğer Nakit Çıkışları"),
    )

    # Hesaplanan değerler
    total_cash_inflows = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Nakit Girişi"),
    )
    total_cash_outflows = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Nakit Çıkışı"),
    )
    net_cash_flow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Net Nakit Akışı"),
    )
    opening_cash_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Açılış Nakit Bakiyesi"),
    )
    closing_cash_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Kapanış Nakit Bakiyesi"),
    )

    # Risk analizi
    cash_shortage_risk = models.BooleanField(
        default=False, verbose_name=_("Nakit Sıkışıklığı Riski")
    )
    minimum_cash_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("10000.00"),
        verbose_name=_("Minimum Nakit Eşiği"),
    )

    notes = models.TextField(null=True, blank=True, verbose_name=_("Notlar"))

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )

    class Meta:
        verbose_name = _("Nakit Akış Tahmini")
        verbose_name_plural = _("Nakit Akış Tahminleri")
        ordering = ["-forecast_date", "-created_at"]
        unique_together = ["company", "forecast_date", "forecast_type"]

    def __str__(self):
        return f"{self.company.name} - {self.forecast_name} ({self.forecast_date})"

    def calculate_cash_flow(self):
        """Nakit akışını hesapla"""
        # Toplam girişleri hesapla
        self.total_cash_inflows = (
            self.cash_from_sales
            + self.cash_from_receivables
            + self.cash_from_investments
            + self.cash_from_loans
            + self.other_cash_inflows
        )

        # Toplam çıkışları hesapla
        self.total_cash_outflows = (
            self.cash_for_operations
            + self.cash_for_payroll
            + self.cash_for_suppliers
            + self.cash_for_taxes
            + self.cash_for_investments
            + self.cash_for_loan_payments
            + self.other_cash_outflows
        )

        # Net nakit akışını hesapla
        self.net_cash_flow = self.total_cash_inflows - self.total_cash_outflows

        # Kapanış bakiyesini hesapla
        self.closing_cash_balance = self.opening_cash_balance + self.net_cash_flow

        # Risk analizi
        self.cash_shortage_risk = (
            self.closing_cash_balance < self.minimum_cash_threshold
        )

    def save(self, *args, **kwargs):
        """Model kaydedilirken otomatik hesaplamalar yap"""
        self.calculate_cash_flow()
        super().save(*args, **kwargs)


class ForecastScenario(models.Model):
    """
    Forecast Scenarios - İyimser/Kötümser/Gerçekçi Senaryolar
    """

    SCENARIO_TYPE_CHOICES = [
        ("OPTIMISTIC", _("İyimser")),
        ("PESSIMISTIC", _("Kötümser")),
        ("REALISTIC", _("Gerçekçi")),
    ]

    forecast = models.ForeignKey(
        CashFlowForecast,
        on_delete=models.CASCADE,
        related_name="scenarios",
        verbose_name=_("Tahmin"),
    )
    scenario_name = models.CharField(max_length=100, verbose_name=_("Senaryo Adı"))
    scenario_type = models.CharField(
        max_length=20, choices=SCENARIO_TYPE_CHOICES, verbose_name=_("Senaryo Türü")
    )
    probability = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Olasılık %")
    )

    projected_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tahmini Gelir"),
    )
    projected_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tahmini Gider"),
    )
    projected_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Tahmini Kar"),
    )

    assumptions = models.TextField(null=True, blank=True, verbose_name=_("Varsayımlar"))

    class Meta:
        verbose_name = _("Tahmin Senaryosu")
        verbose_name_plural = _("Tahmin Senaryoları")

    def __str__(self):
        return f"{self.scenario_name} ({self.get_scenario_type_display()})"


class FinancialGoal(models.Model):
    """
    Financial Goals - Finansal Hedefler
    """

    GOAL_TYPE_CHOICES = [
        ("REVENUE", _("Gelir Hedefi")),
        ("PROFIT", _("Kar Hedefi")),
        ("COST_REDUCTION", _("Maliyet Azaltma")),
        ("GROWTH", _("Büyüme Hedefi")),
        ("EFFICIENCY", _("Verimlilik Hedefi")),
    ]

    STATUS_CHOICES = [
        ("NOT_STARTED", _("Başlanmadı")),
        ("IN_PROGRESS", _("Devam Ediyor")),
        ("COMPLETED", _("Tamamlandı")),
        ("FAILED", _("Başarısız")),
        ("CANCELLED", _("İptal Edildi")),
    ]

    PRIORITY_CHOICES = [
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
        ("CRITICAL", _("Kritik")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    goal_name = models.CharField(max_length=200, verbose_name=_("Hedef Adı"))
    goal_type = models.CharField(
        max_length=20, choices=GOAL_TYPE_CHOICES, verbose_name=_("Hedef Türü")
    )

    target_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Hedef Tutar")
    )
    current_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Mevcut Tutar"),
    )
    achievement_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Başarım %"),
    )

    start_date = models.DateField(verbose_name=_("Başlangıç Tarihi"))
    deadline = models.DateField(verbose_name=_("Termin"))

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NOT_STARTED",
        verbose_name=_("Durum"),
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="MEDIUM",
        verbose_name=_("Öncelik"),
    )

    description = models.TextField(null=True, blank=True, verbose_name=_("Açıklama"))

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )

    class Meta:
        verbose_name = _("Finansal Hedef")
        verbose_name_plural = _("Finansal Hedefler")
        ordering = ["-priority", "deadline"]

    def __str__(self):
        return f"{self.goal_name} - {self.company.name}"

    def update_achievement(self):
        """Başarım yüzdesini güncelle"""
        if self.target_amount > 0:
            self.achievement_percentage = (
                self.current_amount / self.target_amount
            ) * 100

            if self.achievement_percentage >= 100:
                self.status = "COMPLETED"
            elif self.achievement_percentage > 0:
                self.status = "IN_PROGRESS"

        self.save()


class GoalProgress(models.Model):
    """
    Goal Progress Tracking - Hedef İlerleme Takibi
    """

    goal = models.ForeignKey(
        FinancialGoal,
        on_delete=models.CASCADE,
        related_name="progress_records",
        verbose_name=_("Hedef"),
    )
    progress_date = models.DateField(verbose_name=_("İlerleme Tarihi"))
    current_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Mevcut Tutar")
    )
    achievement_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Başarım %")
    )

    notes = models.TextField(null=True, blank=True, verbose_name=_("Notlar"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Kayıt Tarihi"))

    class Meta:
        verbose_name = _("Hedef İlerlemesi")
        verbose_name_plural = _("Hedef İlerlemeleri")
        ordering = ["-progress_date"]

    def __str__(self):
        return f"{self.goal.goal_name} - {self.progress_date}"


class ProfitabilityAnalysis(models.Model):
    """
    Profitability Analysis Model
    Detailed profitability analysis by product, service, customer segment
    """

    ANALYSIS_DIMENSION_CHOICES = [
        ("PRODUCT", _("Ürün Bazlı")),
        ("SERVICE", _("Hizmet Bazlı")),
        ("CUSTOMER", _("Müşteri Bazlı")),
        ("REGION", _("Bölge Bazlı")),
        ("CHANNEL", _("Kanal Bazlı")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    analysis_name = models.CharField(max_length=200, verbose_name=_("Analiz Adı"))
    analysis_dimension = models.CharField(
        max_length=20,
        choices=ANALYSIS_DIMENSION_CHOICES,
        verbose_name=_("Analiz Boyutu"),
    )
    dimension_value = models.CharField(
        max_length=200, verbose_name=_("Boyut Değeri")
    )  # Ürün adı, müşteri adı vs.

    analysis_period_start = models.DateField(verbose_name=_("Analiz Başlangıç Tarihi"))
    analysis_period_end = models.DateField(verbose_name=_("Analiz Bitiş Tarihi"))

    # Gelir kalemleri
    gross_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Brüt Gelir"),
    )
    discounts = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("İndirimler"),
    )
    returns = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("İadeler"),
    )
    net_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Net Gelir"),
    )

    # Maliyet kalemleri
    direct_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Direkt Maliyetler"),
    )
    indirect_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Endirekt Maliyetler"),
    )
    total_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Maliyetler"),
    )

    # Karlılık metrikleri
    gross_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Brüt Kar"),
    )
    net_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Net Kar"),
    )
    gross_profit_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Brüt Kar Marjı %"),
    )
    net_profit_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Net Kar Marjı %"),
    )

    # Birim ekonomisi
    units_sold = models.IntegerField(default=0, verbose_name=_("Satılan Birim"))
    revenue_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Birim Başına Gelir"),
    )
    cost_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Birim Başına Maliyet"),
    )
    profit_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Birim Başına Kar"),
    )

    # Analiz notları ve öneriler
    analysis_notes = models.TextField(
        null=True, blank=True, verbose_name=_("Analiz Notları")
    )
    improvement_recommendations = models.TextField(
        null=True, blank=True, verbose_name=_("İyileştirme Önerileri")
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )

    class Meta:
        verbose_name = _("Karlılık Analizi")
        verbose_name_plural = _("Karlılık Analizleri")
        ordering = ["-created_at"]
        unique_together = [
            "company",
            "analysis_dimension",
            "dimension_value",
            "analysis_period_start",
            "analysis_period_end",
        ]

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
        ("LIQUIDITY", _("Likidite Oranları")),
        ("ACTIVITY", _("Faaliyet Oranları")),
        ("LEVERAGE", _("Kaldıraç Oranları")),
        ("PROFITABILITY", _("Karlılık Oranları")),
        ("MARKET", _("Piyasa Oranları")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    ratio_category = models.CharField(
        max_length=20, choices=RATIO_CATEGORY_CHOICES, verbose_name=_("Oran Kategorisi")
    )
    calculation_date = models.DateField(verbose_name=_("Hesaplama Tarihi"))

    # Likidite oranları
    current_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Cari Oran"),
    )
    quick_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Asit Test Oranı"),
    )
    cash_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Nakit Oranı"),
    )

    # Faaliyet oranları
    inventory_turnover = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Stok Devir Hızı"),
    )
    receivables_turnover = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Alacak Devir Hızı"),
    )
    asset_turnover = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Aktif Devir Hızı"),
    )

    # Kaldıraç oranları
    debt_to_equity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Borç/Özkaynak"),
    )
    debt_to_assets = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Borç/Aktif"),
    )
    equity_multiplier = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Özkaynak Çarpanı"),
    )

    # Karlılık oranları
    gross_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Brüt Kar Marjı"),
    )
    operating_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Faaliyet Kar Marjı"),
    )
    net_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Net Kar Marjı"),
    )
    roa = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Aktif Karlılığı"),
    )
    roe = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Özkaynak Karlılığı"),
    )

    # Benchmark veriler
    industry_benchmark = models.JSONField(
        null=True, blank=True, verbose_name=_("Sektör Benchmarkı")
    )
    peer_comparison = models.JSONField(
        null=True, blank=True, verbose_name=_("Rakip Karşılaştırması")
    )

    # Analiz notları
    analysis_notes = models.TextField(
        null=True, blank=True, verbose_name=_("Analiz Notları")
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )

    class Meta:
        verbose_name = _("Finansal Oran")
        verbose_name_plural = _("Finansal Oranlar")
        ordering = ["-calculation_date", "-created_at"]
        unique_together = ["company", "ratio_category", "calculation_date"]

    def __str__(self):
        return f"{self.company.name} - {self.ratio_category} - {self.calculation_date}"


class SMEBenchmark(models.Model):
    """
    SME Benchmark Data Model
    Industry benchmarks for small and medium enterprises
    """

    industry_code = models.CharField(max_length=20, verbose_name=_("Sektör Kodu"))
    industry_name = models.CharField(max_length=200, verbose_name=_("Sektör Adı"))
    company_size_category = models.CharField(
        max_length=50, verbose_name=_("Şirket Büyüklük Kategorisi")
    )  # Mikro, Küçük, Orta

    # Benchmark oranlar
    benchmark_current_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Benchmark Cari Oran"),
    )
    benchmark_quick_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Benchmark Asit Test"),
    )
    benchmark_debt_to_equity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Benchmark Borç/Özkaynak"),
    )
    benchmark_profit_margin = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Benchmark Kar Marjı"),
    )
    benchmark_roa = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Benchmark ROA"),
    )
    benchmark_roe = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Benchmark ROE"),
    )

    # İstatistiksel veriler
    sample_size = models.IntegerField(verbose_name=_("Örneklem Büyüklüğü"))
    data_year = models.IntegerField(verbose_name=_("Veri Yılı"))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("Son Güncelleme"))

    class Meta:
        verbose_name = _("KOBİ Benchmark Verisi")
        verbose_name_plural = _("KOBİ Benchmark Verileri")
        ordering = ["industry_name", "company_size_category"]
        unique_together = ["industry_code", "company_size_category", "data_year"]

    def __str__(self):
        return f"{self.industry_name} - {self.company_size_category} ({self.data_year})"


class IndustryBenchmark(models.Model):
    """Sektör Benchmark Verileri"""

    industry_sector = models.CharField(max_length=100, verbose_name=_("Sektör"))
    benchmark_year = models.IntegerField(verbose_name=_("Benchmark Yılı"))
    metric_name = models.CharField(max_length=100, verbose_name=_("Metrik Adı"))
    average_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Ortalama Değer")
    )
    top_quartile_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("En İyi %25")
    )

    class Meta:
        verbose_name = _("Sektör Benchmarkı")
        verbose_name_plural = _("Sektör Benchmarkları")
        unique_together = ["industry_sector", "benchmark_year", "metric_name"]

    def __str__(self):
        return f"{self.industry_sector} - {self.metric_name} ({self.benchmark_year})"


class CompetitorAnalysis(models.Model):
    """Rakip Analizi"""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    competitor_name = models.CharField(max_length=200, verbose_name=_("Rakip Adı"))
    analysis_date = models.DateField(verbose_name=_("Analiz Tarihi"))

    revenue = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Gelir")
    )
    market_share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Pazar Payı %"),
    )
    strengths = models.TextField(null=True, blank=True, verbose_name=_("Güçlü Yönler"))
    weaknesses = models.TextField(null=True, blank=True, verbose_name=_("Zayıf Yönler"))
    overall_rating = models.IntegerField(default=5, verbose_name=_("Genel Rating"))

    class Meta:
        verbose_name = _("Rakip Analizi")
        verbose_name_plural = _("Rakip Analizleri")

    def __str__(self):
        return f"{self.competitor_name} - {self.company.name}"


class SWOTAnalysis(models.Model):
    """SWOT Analizi"""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    analysis_date = models.DateField(verbose_name=_("Analiz Tarihi"))

    strengths = models.TextField(verbose_name=_("Güçlü Yönler"))
    weaknesses = models.TextField(verbose_name=_("Zayıf Yönler"))
    opportunities = models.TextField(verbose_name=_("Fırsatlar"))
    threats = models.TextField(verbose_name=_("Tehditler"))

    strategic_recommendations = models.TextField(
        null=True, blank=True, verbose_name=_("Stratejik Öneriler")
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("SWOT Analizi")
        verbose_name_plural = _("SWOT Analizleri")

    def __str__(self):
        return f"{self.company.name} SWOT - {self.analysis_date}"


class RiskAssessment(models.Model):
    """Risk Değerlendirmesi"""

    CATEGORY_CHOICES = [
        ("FINANCIAL", _("Finansal")),
        ("OPERATIONAL", _("Operasyonel")),
        ("STRATEGIC", _("Stratejik")),
        ("COMPLIANCE", _("Uyumluluk")),
        ("REPUTATION", _("İtibar")),
        ("TECHNOLOGY", _("Teknoloji")),
    ]

    LIKELIHOOD_CHOICES = [
        ("RARE", _("Çok Nadir")),
        ("UNLIKELY", _("Olası Değil")),
        ("POSSIBLE", _("Mümkün")),
        ("LIKELY", _("Muhtemel")),
        ("ALMOST_CERTAIN", _("Neredeyse Kesin")),
    ]

    IMPACT_CHOICES = [
        ("NEGLIGIBLE", _("İhmal Edilebilir")),
        ("MINOR", _("Küçük")),
        ("MODERATE", _("Orta")),
        ("MAJOR", _("Büyük")),
        ("CATASTROPHIC", _("Felaket")),
    ]

    STATUS_CHOICES = [
        ("IDENTIFIED", _("Tespit Edildi")),
        ("ASSESSING", _("Değerlendiriliyor")),
        ("MITIGATING", _("Önlem Alınıyor")),
        ("MONITORING", _("İzleniyor")),
        ("CLOSED", _("Kapatıldı")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    risk_name = models.CharField(max_length=200, verbose_name=_("Risk Adı"))
    risk_category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("Risk Kategorisi")
    )

    description = models.TextField(verbose_name=_("Açıklama"))

    likelihood = models.CharField(
        max_length=20, choices=LIKELIHOOD_CHOICES, verbose_name=_("Olasılık")
    )
    impact = models.CharField(
        max_length=20, choices=IMPACT_CHOICES, verbose_name=_("Etki")
    )
    risk_score = models.IntegerField(default=0, verbose_name=_("Risk Skoru"))

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="IDENTIFIED",
        verbose_name=_("Durum"),
    )

    identified_date = models.DateField(verbose_name=_("Tespit Tarihi"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kobi_risk_assessments",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Risk Değerlendirmesi")
        verbose_name_plural = _("Risk Değerlendirmeleri")

    def __str__(self):
        return f"{self.risk_name} - {self.company.name}"


class RiskMitigation(models.Model):
    """Risk Azaltma Planı"""

    STATUS_CHOICES = [
        ("PLANNED", _("Planlandı")),
        ("IN_PROGRESS", _("Devam Ediyor")),
        ("COMPLETED", _("Tamamlandı")),
        ("DEFERRED", _("Ertelendi")),
    ]

    EFFECTIVENESS_CHOICES = [
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
    ]

    risk = models.ForeignKey(
        RiskAssessment,
        on_delete=models.CASCADE,
        related_name="mitigation_plans",
        verbose_name=_("Risk"),
    )
    mitigation_action = models.CharField(
        max_length=200, verbose_name=_("Önlem Aksiyonu")
    )
    description = models.TextField(verbose_name=_("Açıklama"))

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PLANNED",
        verbose_name=_("Durum"),
    )
    effectiveness = models.CharField(
        max_length=10,
        choices=EFFECTIVENESS_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Etkinlik"),
    )

    deadline = models.DateField(null=True, blank=True, verbose_name=_("Termin"))
    cost_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Tahmini Maliyet"),
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Sorumlu"),
    )

    class Meta:
        verbose_name = _("Risk Önlemi")
        verbose_name_plural = _("Risk Önlemleri")

    def __str__(self):
        return f"{self.mitigation_action} - {self.risk.risk_name}"


class PerformanceMetric(models.Model):
    """Performans Metrikleri"""

    CATEGORY_CHOICES = [
        ("FINANCIAL", _("Finansal")),
        ("OPERATIONAL", _("Operasyonel")),
        ("CUSTOMER", _("Müşteri")),
        ("PROCESS", _("Süreç")),
        ("EMPLOYEE", _("Çalışan")),
    ]

    TREND_CHOICES = [
        ("UP", _("Yükseliş")),
        ("DOWN", _("Düşüş")),
        ("STABLE", _("Sabit")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    metric_name = models.CharField(max_length=100, verbose_name=_("Metrik Adı"))
    metric_category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("Kategori")
    )

    current_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Mevcut Değer")
    )
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Hedef Değer"),
    )

    trend = models.CharField(
        max_length=10,
        choices=TREND_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Trend"),
    )
    last_updated = models.DateField(verbose_name=_("Son Güncelleme"))

    class Meta:
        verbose_name = _("Performans Metriği")
        verbose_name_plural = _("Performans Metrikleri")

    def __str__(self):
        return f"{self.metric_name} - {self.company.name}"


class MetricTarget(models.Model):
    """Metrik Hedefleri"""

    metric = models.ForeignKey(
        PerformanceMetric,
        on_delete=models.CASCADE,
        related_name="targets",
        verbose_name=_("Metrik"),
    )
    target_period = models.DateField(verbose_name=_("Hedef Dönemi"))
    target_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Hedef Değer")
    )
    is_achieved = models.BooleanField(default=False, verbose_name=_("Başarıldı mı?"))

    class Meta:
        verbose_name = _("Metrik Hedefi")
        verbose_name_plural = _("Metrik Hedefleri")

    def __str__(self):
        return f"{self.metric.metric_name} - {self.target_period}"


class FinancialAlert(models.Model):
    """Finansal Uyarılar"""

    ALERT_TYPE_CHOICES = [
        ("CASH_LOW", _("Düşük Nakit")),
        ("PROFIT_DECLINE", _("Kar Düşüşü")),
        ("DEBT_HIGH", _("Yüksek Borç")),
        ("EXPENSE_SPIKE", _("Gider Artışı")),
        ("REVENUE_DROP", _("Gelir Düşüşü")),
    ]

    SEVERITY_CHOICES = [
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
        ("CRITICAL", _("Kritik")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    alert_type = models.CharField(
        max_length=20, choices=ALERT_TYPE_CHOICES, verbose_name=_("Uyarı Türü")
    )
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, verbose_name=_("Ciddiyet")
    )

    alert_message = models.TextField(verbose_name=_("Uyarı Mesajı"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif mi?"))

    triggered_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Tetiklenme Zamanı")
    )
    resolved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Çözüm Zamanı")
    )

    class Meta:
        verbose_name = _("Finansal Uyarı")
        verbose_name_plural = _("Finansal Uyarılar")
        ordering = ["-triggered_at"]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.company.name}"


class AdvisoryReport(models.Model):
    """Danışmanlık Raporları"""

    REPORT_TYPE_CHOICES = [
        ("MONTHLY", _("Aylık Rapor")),
        ("QUARTERLY", _("Çeyreklik Rapor")),
        ("ANNUAL", _("Yıllık Rapor")),
        ("CUSTOM", _("Özel Rapor")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    report_title = models.CharField(max_length=200, verbose_name=_("Rapor Başlığı"))
    report_type = models.CharField(
        max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name=_("Rapor Türü")
    )
    report_date = models.DateField(verbose_name=_("Rapor Tarihi"))

    content = models.TextField(verbose_name=_("Rapor İçeriği"))
    summary = models.TextField(null=True, blank=True, verbose_name=_("Özet"))
    recommendations = models.TextField(
        null=True, blank=True, verbose_name=_("Öneriler")
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Danışmanlık Raporu")
        verbose_name_plural = _("Danışmanlık Raporları")
        ordering = ["-report_date"]

    def __str__(self):
        return f"{self.report_title} - {self.company.name}"


class FinancialHealthSnapshot(models.Model):
    """Finansal Sağlık Snapshot"""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name=_("Şirket")
    )
    snapshot_date = models.DateField(verbose_name=_("Snapshot Tarihi"))

    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Genel Skor")
    )
    liquidity_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Likidite Skoru")
    )
    profitability_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Karlılık Skoru")
    )
    solvency_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Ödeme Gücü Skoru")
    )
    efficiency_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Verimlilik Skoru")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Sağlık Snapshot")
        verbose_name_plural = _("Sağlık Snapshots")
        ordering = ["-snapshot_date"]

    def __str__(self):
        return f"{self.company.name} - {self.snapshot_date}"


# ============================================================================
# GENİŞLETİLMİŞ KOBİ ANALİZ MODELLERİ
# ============================================================================


class FinancialRating(models.Model):
    """Finansal Derecelendirme - Kredi notu benzeri"""

    RATING_SCALE = [
        ("AAA", _("AAA - Mükemmel")),
        ("AA", _("AA - Çok İyi")),
        ("A", _("A - İyi")),
        ("BBB", _("BBB - Orta Üstü")),
        ("BB", _("BB - Orta")),
        ("B", _("B - Orta Altı")),
        ("CCC", _("CCC - Zayıf")),
        ("CC", _("CC - Çok Zayıf")),
        ("C", _("C - Kritik")),
        ("D", _("D - Temerrüt")),
    ]

    OUTLOOK_CHOICES = [
        ("POSITIVE", _("Pozitif")),
        ("STABLE", _("Durağan")),
        ("NEGATIVE", _("Negatif")),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="financial_ratings",
        verbose_name=_("Şirket"),
    )
    rating_date = models.DateField(verbose_name=_("Derecelendirme Tarihi"))

    # Derecelendirme
    overall_rating = models.CharField(
        max_length=5, choices=RATING_SCALE, verbose_name=_("Genel Derece")
    )
    financial_strength = models.CharField(
        max_length=5, choices=RATING_SCALE, verbose_name=_("Finansal Güç")
    )
    creditworthiness = models.CharField(
        max_length=5, choices=RATING_SCALE, verbose_name=_("Kredi Değerliliği")
    )

    outlook = models.CharField(
        max_length=20,
        choices=OUTLOOK_CHOICES,
        default="STABLE",
        verbose_name=_("Görünüm"),
    )

    # Puanlar (0-100)
    liquidity_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Likidite Puanı")
    )
    profitability_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Karlılık Puanı")
    )
    leverage_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Kaldıraç Puanı")
    )
    management_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Yönetim Puanı")
    )

    # Analiz detayları
    rating_rationale = models.TextField(verbose_name=_("Derecelendirme Gerekçesi"))
    key_strengths = models.JSONField(
        default=list, blank=True, verbose_name=_("Temel Güçlü Yönler")
    )
    key_weaknesses = models.JSONField(
        default=list, blank=True, verbose_name=_("Temel Zayıf Yönler")
    )

    # Önceki derecelendirme
    previous_rating = models.CharField(
        max_length=5,
        choices=RATING_SCALE,
        null=True,
        blank=True,
        verbose_name=_("Önceki Derece"),
    )
    rating_change = models.CharField(
        max_length=20, blank=True, verbose_name=_("Değişim")
    )

    # Metadata
    rated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Derecelendiren"),
    )
    valid_until = models.DateField(
        null=True, blank=True, verbose_name=_("Geçerlilik Tarihi")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Finansal Derecelendirme")
        verbose_name_plural = _("Finansal Derecelendirmeler")
        ordering = ["-rating_date"]

    def __str__(self):
        return f"{self.company.name} - {self.overall_rating} ({self.rating_date})"


class BusinessValuation(models.Model):
    """İşletme Değerlemesi"""

    VALUATION_METHODS = [
        ("DCF", _("İndirgenmiş Nakit Akışı (DCF)")),
        ("MULTIPLES", _("Çarpanlar Yöntemi")),
        ("ASSET_BASED", _("Varlık Bazlı")),
        ("INCOME", _("Gelir Yaklaşımı")),
        ("MARKET", _("Piyasa Yaklaşımı")),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="valuations",
        verbose_name=_("Şirket"),
    )
    valuation_date = models.DateField(verbose_name=_("Değerleme Tarihi"))
    valuation_method = models.CharField(
        max_length=20, choices=VALUATION_METHODS, verbose_name=_("Değerleme Yöntemi")
    )

    # Değerlemeler
    enterprise_value = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name=_("İşletme Değeri")
    )
    equity_value = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name=_("Özkaynak Değeri")
    )

    # Çarpanlar
    ev_ebitda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("EV/EBITDA"),
    )
    pe_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("F/K Oranı"),
    )
    pb_ratio = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("PD/DD")
    )

    # Varsayımlar
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("İskonto Oranı (%)"),
    )
    growth_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Büyüme Oranı (%)"),
    )

    # Detaylar
    assumptions = models.JSONField(
        default=dict, blank=True, verbose_name=_("Varsayımlar")
    )
    calculation_details = models.JSONField(
        default=dict, blank=True, verbose_name=_("Hesaplama Detayları")
    )
    methodology_notes = models.TextField(
        blank=True, verbose_name=_("Metodoloji Notları")
    )

    # Önceki değerleme ile karşılaştırma
    previous_valuation = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Önceki Değerleme"),
    )
    value_change_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Değer Değişimi (%)"),
    )

    # Metadata
    valued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Değerleyen")
    )
    report_file = models.FileField(
        upload_to="valuations/", null=True, blank=True, verbose_name=_("Rapor Dosyası")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("İşletme Değerlemesi")
        verbose_name_plural = _("İşletme Değerlemeleri")
        ordering = ["-valuation_date"]

    def __str__(self):
        return (
            f"{self.company.name} - {self.enterprise_value} TL ({self.valuation_date})"
        )


class WorkingCapitalAnalysis(models.Model):
    """İşletme Sermayesi Analizi"""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="working_capital_analyses",
        verbose_name=_("Şirket"),
    )
    analysis_date = models.DateField(verbose_name=_("Analiz Tarihi"))

    # Dönen varlıklar
    current_assets = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Dönen Varlıklar")
    )
    cash_and_equivalents = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Nakit ve Benzerleri")
    )
    accounts_receivable = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Alacaklar")
    )
    inventory = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Stoklar")
    )

    # Kısa vadeli yükümlülükler
    current_liabilities = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Kısa Vadeli Yükümlülükler")
    )
    accounts_payable = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Borçlar")
    )
    short_term_debt = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Kısa Vadeli Borç")
    )

    # Hesaplanan değerler
    working_capital = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("İşletme Sermayesi")
    )
    net_working_capital = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Net İşletme Sermayesi")
    )

    # Oranlar
    current_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, verbose_name=_("Cari Oran")
    )
    quick_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, verbose_name=_("Asit Test Oranı")
    )
    cash_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, verbose_name=_("Nakit Oranı")
    )

    # Dönem süreleri (gün)
    days_sales_outstanding = models.IntegerField(
        null=True, blank=True, verbose_name=_("Alacak Tahsil Süresi (Gün)")
    )
    days_inventory_outstanding = models.IntegerField(
        null=True, blank=True, verbose_name=_("Stok Devir Süresi (Gün)")
    )
    days_payable_outstanding = models.IntegerField(
        null=True, blank=True, verbose_name=_("Borç Ödeme Süresi (Gün)")
    )
    cash_conversion_cycle = models.IntegerField(
        null=True, blank=True, verbose_name=_("Nakit Dönüş Döngüsü (Gün)")
    )

    # Analiz ve öneriler
    analysis_summary = models.TextField(blank=True, verbose_name=_("Analiz Özeti"))
    recommendations = models.TextField(blank=True, verbose_name=_("Öneriler"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("İşletme Sermayesi Analizi")
        verbose_name_plural = _("İşletme Sermayesi Analizleri")
        ordering = ["-analysis_date"]

    def save(self, *args, **kwargs):
        # Otomatik hesaplamalar
        self.working_capital = self.current_assets - self.current_liabilities
        self.net_working_capital = self.working_capital

        if self.current_liabilities > 0:
            self.current_ratio = self.current_assets / self.current_liabilities
            quick_assets = self.current_assets - self.inventory
            self.quick_ratio = quick_assets / self.current_liabilities
            self.cash_ratio = self.cash_and_equivalents / self.current_liabilities

        # Nakit dönüş döngüsü
        if all(
            [
                self.days_sales_outstanding,
                self.days_inventory_outstanding,
                self.days_payable_outstanding,
            ]
        ):
            self.cash_conversion_cycle = (
                self.days_sales_outstanding
                + self.days_inventory_outstanding
                - self.days_payable_outstanding
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name} - İşletme Sermayesi ({self.analysis_date})"


class BreakEvenAnalysis(models.Model):
    """Başabaş Noktası Analizi"""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="breakeven_analyses",
        verbose_name=_("Şirket"),
    )
    analysis_date = models.DateField(verbose_name=_("Analiz Tarihi"))
    analysis_period = models.CharField(
        max_length=20,
        choices=[
            ("monthly", _("Aylık")),
            ("quarterly", _("Çeyreklik")),
            ("annual", _("Yıllık")),
        ],
        default="monthly",
        verbose_name=_("Analiz Dönemi"),
    )

    # Maliyet yapısı
    fixed_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Sabit Maliyetler"),
    )
    variable_costs_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Birim Değişken Maliyet"),
    )
    selling_price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Birim Satış Fiyatı"),
    )

    # Hesaplanan değerler
    contribution_margin_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Birim Katkı Marjı"),
    )
    contribution_margin_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Katkı Marjı Oranı (%)"),
    )

    breakeven_units = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Başabaş Satış Miktarı"),
    )
    breakeven_sales_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Başabaş Satış Geliri"),
    )

    # Mevcut durum
    current_sales_units = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Mevcut Satış Miktarı"),
    )
    current_sales_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Mevcut Satış Geliri"),
    )
    margin_of_safety_units = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Güvenlik Marjı (Adet)"),
    )
    margin_of_safety_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Güvenlik Marjı (%)"),
    )

    # Analiz
    analysis_notes = models.TextField(blank=True, verbose_name=_("Analiz Notları"))
    recommendations = models.TextField(blank=True, verbose_name=_("Öneriler"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Başabaş Noktası Analizi")
        verbose_name_plural = _("Başabaş Noktası Analizleri")
        ordering = ["-analysis_date"]

    def save(self, *args, **kwargs):
        # Katkı marjı hesapla
        self.contribution_margin_per_unit = (
            self.selling_price_per_unit - self.variable_costs_per_unit
        )

        if self.selling_price_per_unit > 0:
            self.contribution_margin_ratio = (
                self.contribution_margin_per_unit / self.selling_price_per_unit
            ) * 100

        # Başabaş noktası hesapla
        if self.contribution_margin_per_unit > 0:
            self.breakeven_units = self.fixed_costs / self.contribution_margin_per_unit
            self.breakeven_sales_revenue = (
                self.breakeven_units * self.selling_price_per_unit
            )

        # Güvenlik marjı hesapla
        if self.current_sales_units and self.breakeven_units:
            self.margin_of_safety_units = (
                self.current_sales_units - self.breakeven_units
            )
            if self.current_sales_units > 0:
                self.margin_of_safety_percentage = (
                    self.margin_of_safety_units / self.current_sales_units
                ) * 100

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name} - Başabaş ({self.analysis_date})"


class SensitivityAnalysis(models.Model):
    """Duyarlılık Analizi - Değişken etki analizi"""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="sensitivity_analyses",
        verbose_name=_("Şirket"),
    )
    analysis_date = models.DateField(verbose_name=_("Analiz Tarihi"))

    base_scenario_name = models.CharField(
        max_length=200, verbose_name=_("Baz Senaryo Adı")
    )

    # Analiz edilen değişkenler
    variable_name = models.CharField(max_length=100, verbose_name=_("Değişken Adı"))
    base_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Baz Değer")
    )

    # Senaryo değişimleri (JSON)
    scenarios = models.JSONField(
        default=list,
        verbose_name=_("Senaryolar"),
        help_text=_("Her senaryo: {change_percentage, new_value, impact}"),
    )

    # Etki metrikleri
    impact_on_revenue = models.JSONField(
        default=dict, blank=True, verbose_name=_("Gelir Etkisi")
    )
    impact_on_profit = models.JSONField(
        default=dict, blank=True, verbose_name=_("Kar Etkisi")
    )
    impact_on_cash_flow = models.JSONField(
        default=dict, blank=True, verbose_name=_("Nakit Akışı Etkisi")
    )

    # Kritik noktalar
    critical_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Kritik Eşik"),
    )
    sensitivity_coefficient = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Duyarlılık Katsayısı"),
    )

    # Analiz sonuçları
    analysis_summary = models.TextField(verbose_name=_("Analiz Özeti"))
    risk_assessment = models.TextField(
        blank=True, verbose_name=_("Risk Değerlendirmesi")
    )
    recommendations = models.TextField(blank=True, verbose_name=_("Öneriler"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Duyarlılık Analizi")
        verbose_name_plural = _("Duyarlılık Analizleri")
        ordering = ["-analysis_date"]

    def __str__(self):
        return f"{self.company.name} - {self.variable_name} Duyarlılık ({self.analysis_date})"


class ScenarioPlanning(models.Model):
    """Senaryo Planlama - Gelecek öngörüsü"""

    SCENARIO_TYPES = [
        ("BEST_CASE", _("En İyi Senaryo")),
        ("BASE_CASE", _("Baz Senaryo")),
        ("WORST_CASE", _("En Kötü Senaryo")),
        ("REALISTIC", _("Gerçekçi Senaryo")),
        ("CUSTOM", _("Özel Senaryo")),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="scenario_plans",
        verbose_name=_("Şirket"),
    )
    scenario_name = models.CharField(max_length=200, verbose_name=_("Senaryo Adı"))
    scenario_type = models.CharField(
        max_length=20, choices=SCENARIO_TYPES, verbose_name=_("Senaryo Tipi")
    )

    # Zaman aralığı
    planning_period_start = models.DateField(verbose_name=_("Planlama Başlangıç"))
    planning_period_end = models.DateField(verbose_name=_("Planlama Bitiş"))

    # Tahminler
    revenue_forecast = models.JSONField(
        default=list,
        verbose_name=_("Gelir Tahmini"),
        help_text=_("Aylık/çeyreklik tahminler"),
    )
    expense_forecast = models.JSONField(default=list, verbose_name=_("Gider Tahmini"))
    cash_flow_forecast = models.JSONField(
        default=list, verbose_name=_("Nakit Akışı Tahmini")
    )

    # Varsayımlar
    key_assumptions = models.JSONField(
        default=dict, verbose_name=_("Temel Varsayımlar")
    )
    growth_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Büyüme Oranı (%)"),
    )
    inflation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Enflasyon Oranı (%)"),
    )

    # Olasılık ve güven
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        verbose_name=_("Gerçekleşme Olasılığı (%)"),
    )
    confidence_level = models.CharField(
        max_length=20,
        choices=[("HIGH", _("Yüksek")), ("MEDIUM", _("Orta")), ("LOW", _("Düşük"))],
        default="MEDIUM",
        verbose_name=_("Güven Seviyesi"),
    )

    # Aksiyonlar
    action_plan = models.TextField(blank=True, verbose_name=_("Aksiyon Planı"))
    contingency_plan = models.TextField(blank=True, verbose_name=_("Acil Durum Planı"))

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Senaryo Planlama")
        verbose_name_plural = _("Senaryo Planlamaları")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.name} - {self.scenario_name}"
