# -*- coding: utf-8 -*-
"""
FinAsis - KOBİ Finansal Analiz ve Raporlama Modülleri
Küçük ve Orta Büyüklükteki İşletmeler için özelleştirilmiş finansal analiz araçları
"""

from decimal import Decimal
from typing import TYPE_CHECKING
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum

from accounting.models import Company


class KOBIFinancialAnalysis(models.Model):
    """
    KOBİ Finansal Analiz Modeli
    Otomatik finansal oran hesaplamaları ve trend analizleri
    """

    ANALYSIS_PERIODS = [
        ("MONTHLY", _("Aylık")),
        ("QUARTERLY", _("Çeyrek Yıl")),
        ("YEARLY", _("Yıllık")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="financial_analyses"
    )
    analysis_date = models.DateField(_("Analiz Tarihi"))
    period_type = models.CharField(
        _("Dönem Tipi"), max_length=20, choices=ANALYSIS_PERIODS
    )
    start_date = models.DateField(_("Başlangıç Tarihi"))
    end_date = models.DateField(_("Bitiş Tarihi"))

    # Likidite Oranları
    current_ratio = models.DecimalField(
        _("Cari Oran"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    quick_ratio = models.DecimalField(
        _("Asit Test Oranı"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    cash_ratio = models.DecimalField(
        _("Nakit Oranı"), max_digits=8, decimal_places=4, null=True, blank=True
    )

    # Karlılık Oranları
    gross_profit_margin = models.DecimalField(
        _("Brüt Kar Marjı %"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    net_profit_margin = models.DecimalField(
        _("Net Kar Marjı %"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    return_on_assets = models.DecimalField(
        _("Aktif Karlılığı %"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    return_on_equity = models.DecimalField(
        _("Özkaynak Karlılığı %"), max_digits=8, decimal_places=4, null=True, blank=True
    )

    # Faaliyet Oranları
    asset_turnover = models.DecimalField(
        _("Aktif Devir Hızı"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    inventory_turnover = models.DecimalField(
        _("Stok Devir Hızı"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    receivables_turnover = models.DecimalField(
        _("Alacak Devir Hızı"), max_digits=8, decimal_places=4, null=True, blank=True
    )

    # Kaldıraç Oranları
    debt_to_equity = models.DecimalField(
        _("Borç/Özkaynak Oranı"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    debt_to_assets = models.DecimalField(
        _("Borç/Aktif Oranı"), max_digits=8, decimal_places=4, null=True, blank=True
    )
    equity_multiplier = models.DecimalField(
        _("Özkaynak Çarpanı"), max_digits=8, decimal_places=4, null=True, blank=True
    )

    # Toplam değerler (hesaplamalar için)
    total_assets = models.DecimalField(
        _("Toplam Aktif"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    total_liabilities = models.DecimalField(
        _("Toplam Borç"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    total_equity = models.DecimalField(
        _("Toplam Özkaynak"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    total_revenue = models.DecimalField(
        _("Toplam Gelir"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    net_income = models.DecimalField(
        _("Net Kar"), max_digits=15, decimal_places=2, default=Decimal("0")
    )

    # Analiz sonuçları
    financial_health_score = models.DecimalField(
        _("Mali Sağlık Skoru"),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    risk_level = models.CharField(
        _("Risk Seviyesi"),
        max_length=20,
        choices=[
            ("LOW", _("Düşük Risk")),
            ("MEDIUM", _("Orta Risk")),
            ("HIGH", _("Yüksek Risk")),
            ("CRITICAL", _("Kritik Risk")),
        ],
        null=True,
        blank=True,
    )

    recommendations = models.JSONField(_("Öneriler"), default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("KOBİ Finansal Analizi")
        verbose_name_plural = _("KOBİ Finansal Analizleri")
        unique_together = [["company", "analysis_date", "period_type"]]
        ordering = ["-analysis_date"]

    def __str__(self):
        return f"{self.company.name} - {self.analysis_date} ({self.get_period_type_display()})"

    if TYPE_CHECKING:
        # Django tarafından runtime'da eklenen display helper
        def get_period_type_display(self) -> str:
            ...  # pragma: no cover

    def calculate_all_ratios(self):
        """Tüm finansal oranları hesapla"""
        from .enhanced_accounting_models import FinancialStatementGenerator

        # Mali tablo verilerini al
        generator = FinancialStatementGenerator(
            self.company, self.start_date, self.end_date
        )
        balance_sheet = generator.generate_balance_sheet()
        income_statement = generator.generate_income_statement()

        # Temel değerleri ayarla
        self.total_assets = balance_sheet["aktif"]["toplam_aktif"]
        self.total_liabilities = balance_sheet["pasif"]["kisa_vadeli_borclar"].get(
            "total", 0
        ) + balance_sheet["pasif"]["uzun_vadeli_borclar"].get("total", 0)
        self.total_equity = balance_sheet["pasif"]["ozkaynaklar"].get("total", 0)
        self.total_revenue = income_statement["toplam_gelir"]
        self.net_income = income_statement["net_kar_zarar"]

        # Likidite oranları
        self._calculate_liquidity_ratios()

        # Karlılık oranları
        self._calculate_profitability_ratios()

        # Faaliyet oranları
        self._calculate_activity_ratios()

        # Kaldıraç oranları
        self._calculate_leverage_ratios()

        # Mali sağlık skoru
        self._calculate_financial_health_score()

        # Risk seviyesi belirleme
        self._determine_risk_level()

        # Önerileri oluştur
        self._generate_recommendations()

        self.save()

    def _calculate_liquidity_ratios(self):
        """Likidite oranlarını hesapla"""
        # Cari oran = Dönen Varlıklar / Kısa Vadeli Borçlar
        donen_varliklar = self._get_account_group_balance("1")
        kisa_vadeli_borclar = self._get_account_group_balance("3")

        if kisa_vadeli_borclar > Decimal("0"):
            self.current_ratio = donen_varliklar / kisa_vadeli_borclar

        # Asit test oranı = (Dönen Varlıklar - Stoklar) / Kısa Vadeli Borçlar
        stoklar = self._get_account_balance(
            ["15"]
        )  # Stok hesapları genelde 15 ile başlar
        if kisa_vadeli_borclar > Decimal("0"):
            self.quick_ratio = (donen_varliklar - stoklar) / kisa_vadeli_borclar

        # Nakit oranı = Nakit ve Nakit Benzerleri / Kısa Vadeli Borçlar
        nakit = self._get_account_balance(["10", "11"])  # Kasa ve Banka hesapları
        if kisa_vadeli_borclar > Decimal("0"):
            self.cash_ratio = nakit / kisa_vadeli_borclar

    def _calculate_profitability_ratios(self):
        """Karlılık oranlarını hesapla"""
        satislar = self._get_account_group_balance("6")  # Gelir hesapları
        satis_maliyeti = self._get_account_group_balance("7")  # Maliyet hesapları

        # Brüt kar marjı
        if satislar > Decimal("0"):
            brut_kar = satislar - satis_maliyeti
            self.gross_profit_margin = (brut_kar / satislar) * 100

        # Net kar marjı
        if satislar > Decimal("0") and self.net_income:
            self.net_profit_margin = (self.net_income / satislar) * 100

        # Aktif karlılığı (ROA)
        if self.total_assets > Decimal("0") and self.net_income:
            self.return_on_assets = (self.net_income / self.total_assets) * 100

        # Özkaynak karlılığı (ROE)
        if self.total_equity > Decimal("0") and self.net_income:
            self.return_on_equity = (self.net_income / self.total_equity) * 100

    def _calculate_activity_ratios(self):
        """Faaliyet oranlarını hesapla"""
        # Aktif devir hızı = Satışlar / Ortalama Toplam Aktif
        if self.total_assets > Decimal("0"):
            self.asset_turnover = self.total_revenue / self.total_assets

        # Stok devir hızı = Satılan Malın Maliyeti / Ortalama Stok
        ortalama_stok = self._get_account_balance(["15"])
        if ortalama_stok > Decimal("0"):
            satis_maliyeti = self._get_account_group_balance("7")
            self.inventory_turnover = satis_maliyeti / ortalama_stok

        # Alacak devir hızı = Satışlar / Ortalama Alacaklar
        alacaklar = self._get_account_balance(["12"])  # Ticari alacaklar
        if alacaklar > Decimal("0"):
            self.receivables_turnover = self.total_revenue / alacaklar

    def _calculate_leverage_ratios(self):
        """Kaldıraç oranlarını hesapla"""
        # Borç/Özkaynak oranı
        if self.total_equity > Decimal("0"):
            self.debt_to_equity = self.total_liabilities / self.total_equity

        # Borç/Aktif oranı
        if self.total_assets > Decimal("0"):
            self.debt_to_assets = self.total_liabilities / self.total_assets

        # Özkaynak çarpanı
        if self.total_equity > Decimal("0"):
            self.equity_multiplier = self.total_assets / self.total_equity

    def _calculate_financial_health_score(self):
        """Mali sağlık skorunu hesapla (0-100 arası)"""
        score = Decimal("50")  # Başlangıç skoru

        # Likidite skoru (25 puan)
        if self.current_ratio:
            if self.current_ratio >= Decimal("2"):
                score += Decimal("25")
            elif self.current_ratio >= Decimal("1.5"):
                score += Decimal("20")
            elif self.current_ratio >= Decimal("1"):
                score += Decimal("15")
            elif self.current_ratio >= Decimal("0.5"):
                score += Decimal("10")

        # Karlılık skoru (25 puan)
        if self.net_profit_margin:
            if self.net_profit_margin >= Decimal("15"):
                score += Decimal("25")
            elif self.net_profit_margin >= Decimal("10"):
                score += Decimal("20")
            elif self.net_profit_margin >= Decimal("5"):
                score += Decimal("15")
            elif self.net_profit_margin >= Decimal("0"):
                score += Decimal("10")
            else:
                score -= Decimal("10")

        # Kaldıraç skoru (25 puan)
        if self.debt_to_equity:
            if self.debt_to_equity <= Decimal("0.5"):
                score += Decimal("25")
            elif self.debt_to_equity <= Decimal("1"):
                score += Decimal("20")
            elif self.debt_to_equity <= Decimal("2"):
                score += Decimal("15")
            elif self.debt_to_equity <= Decimal("3"):
                score += Decimal("10")
            else:
                score -= Decimal("10")

        # Faaliyet skoru (25 puan)
        if self.asset_turnover:
            if self.asset_turnover >= Decimal("2"):
                score += Decimal("25")
            elif self.asset_turnover >= Decimal("1.5"):
                score += Decimal("20")
            elif self.asset_turnover >= Decimal("1"):
                score += Decimal("15")
            elif self.asset_turnover >= Decimal("0.5"):
                score += Decimal("10")

        self.financial_health_score = max(Decimal("0"), min(score, Decimal("100")))

    def _determine_risk_level(self):
        """Risk seviyesini belirle"""
        if self.financial_health_score:
            if self.financial_health_score >= Decimal("80"):
                self.risk_level = "LOW"
            elif self.financial_health_score >= Decimal("60"):
                self.risk_level = "MEDIUM"
            elif self.financial_health_score >= Decimal("40"):
                self.risk_level = "HIGH"
            else:
                self.risk_level = "CRITICAL"

    def _generate_recommendations(self):
        """Finansal duruma göre önerileri oluştur"""
        recommendations = []

        # Likidite önerileri
        if self.current_ratio and self.current_ratio < Decimal("1"):
            recommendations.append(
                {
                    "type": "liquidity",
                    "priority": "high",
                    "title": "Likidite Sorunu",
                    "description": "Cari oranınız 1'in altında. Kısa vadeli borç ödeme gücünüz düşük.",
                    "action": "Alacak tahsilatını hızlandırın, stok devrini artırın veya kısa vadeli finansman sağlayın.",
                }
            )
        elif self.current_ratio and self.current_ratio > Decimal("3"):
            recommendations.append(
                {
                    "type": "liquidity",
                    "priority": "medium",
                    "title": "Fazla Likidite",
                    "description": "Cari oranınız çok yüksek. Nakitinizi daha verimli kullanabilirsiniz.",
                    "action": "Yatırım fırsatları değerlendirin veya borçları erkenden kapatın.",
                }
            )

        # Karlılık önerileri
        if self.net_profit_margin and self.net_profit_margin < Decimal("5"):
            recommendations.append(
                {
                    "type": "profitability",
                    "priority": "high",
                    "title": "Düşük Karlılık",
                    "description": "Net kar marjınız %5'in altında. Karlılığınızı artırmanız gerekiyor.",
                    "action": "Maliyetlerinizi gözden geçirin, fiyatlandırmanızı optimize edin.",
                }
            )

        # Borç önerileri
        if self.debt_to_equity and self.debt_to_equity > Decimal("2"):
            recommendations.append(
                {
                    "type": "leverage",
                    "priority": "high",
                    "title": "Yüksek Borçluluk",
                    "description": "Borç/Özkaynak oranınız yüksek. Mali riskiniz artmış durumda.",
                    "action": "Borç azaltma planı yapın, özkaynak artırıcı önlemler alın.",
                }
            )

        # Faaliyet önerileri
        if self.inventory_turnover and self.inventory_turnover < Decimal("4"):
            recommendations.append(
                {
                    "type": "operations",
                    "priority": "medium",
                    "title": "Yavaş Stok Devri",
                    "description": "Stok devir hızınız düşük. Stoklarınız çok uzun süre bekliyor.",
                    "action": "Stok yönetimini optimize edin, eski stokları temizleyin.",
                }
            )

        self.recommendations = recommendations

    def _get_account_group_balance(self, group_code):
        """Hesap grubu bakiyesini al"""
        from .enhanced_accounting_models import ChartOfAccounts

        accounts = ChartOfAccounts.objects.filter(
            company=self.company, account_type=group_code, is_detail_account=True
        )

        total = Decimal("0")
        for account in accounts:
            balance = account.get_balance(self.start_date, self.end_date)
            total += abs(balance) if balance else Decimal("0")

        return total

    def _get_account_balance(self, account_codes):
        """Belirli hesap kodlarının bakiyesini al"""
        from .enhanced_accounting_models import ChartOfAccounts

        total = Decimal("0")
        for code in account_codes:
            accounts = ChartOfAccounts.objects.filter(
                company=self.company, code__startswith=code, is_detail_account=True
            )
            for account in accounts:
                balance = account.get_balance(self.start_date, self.end_date)
                total += abs(balance) if balance else Decimal("0")

        return total


class BudgetPlan(models.Model):
    """
    KOBİ Bütçe Planlama Modeli
    Aylık/yıllık bütçe planlaması ve gerçekleşen karşılaştırması
    """

    BUDGET_TYPES = [
        ("REVENUE", _("Gelir Bütçesi")),
        ("EXPENSE", _("Gider Bütçesi")),
        ("CAPITAL", _("Yatırım Bütçesi")),
        ("CASH_FLOW", _("Nakit Akış Bütçesi")),
        ("MASTER", _("Ana Bütçe")),
    ]

    PERIODS = [
        ("MONTHLY", _("Aylık")),
        ("QUARTERLY", _("Üç Aylık")),
        ("YEARLY", _("Yıllık")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="budget_plans"
    )
    name = models.CharField(_("Bütçe Adı"), max_length=100)
    budget_type = models.CharField(_("Bütçe Tipi"), max_length=20, choices=BUDGET_TYPES)
    period_type = models.CharField(_("Dönem"), max_length=20, choices=PERIODS)

    start_date = models.DateField(_("Başlangıç Tarihi"))
    end_date = models.DateField(_("Bitiş Tarihi"))

    total_budgeted_amount = models.DecimalField(
        _("Toplam Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    total_actual_amount = models.DecimalField(
        _("Toplam Gerçekleşen"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    variance_amount = models.DecimalField(
        _("Sapma Tutarı"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    variance_percentage = models.DecimalField(
        _("Sapma Yüzdesi"), max_digits=8, decimal_places=4, default=Decimal("0")
    )

    status = models.CharField(
        _("Durum"),
        max_length=20,
        choices=[
            ("DRAFT", _("Taslak")),
            ("APPROVED", _("Onaylandı")),
            ("ACTIVE", _("Aktif")),
            ("COMPLETED", _("Tamamlandı")),
            ("CANCELLED", _("İptal Edildi")),
        ],
        default="DRAFT",
    )

    notes = models.TextField(_("Notlar"), blank=True)

    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_budgets",
    )
    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_budgets",
    )
    approved_at = models.DateTimeField(_("Onay Zamanı"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Bütçe Planı")
        verbose_name_plural = _("Bütçe Planları")
        ordering = ["-start_date"]

    if TYPE_CHECKING:
        from django.db.models.manager import RelatedManager

        budget_lines: "RelatedManager[BudgetLine]"

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def calculate_variance(self):
        """Bütçe sapmalarını hesapla"""
        self.variance_amount = self.total_actual_amount - self.total_budgeted_amount
        if self.total_budgeted_amount != 0:
            self.variance_percentage = (
                self.variance_amount / self.total_budgeted_amount
            ) * 100
        self.save(update_fields=["variance_amount", "variance_percentage"])

    def update_actuals(self):
        """Gerçekleşen tutarları güncelle"""
        total_actual = self.budget_lines.aggregate(total=Sum("actual_amount"))[
            "total"
        ] or Decimal("0")

        self.total_actual_amount = total_actual
        self.calculate_variance()


class BudgetLine(models.Model):
    """Bütçe Kalemi"""

    budget_plan = models.ForeignKey(
        BudgetPlan,
        on_delete=models.CASCADE,
        related_name="budget_lines",
        verbose_name=_("Bütçe Planı"),
    )
    account = models.ForeignKey(
        "finance.ChartOfAccounts",
        on_delete=models.PROTECT,
        related_name="budget_lines",
        verbose_name=_("Hesap"),
    )
    cost_center = models.ForeignKey(
        "finance.CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Masraf Merkezi"),
    )

    line_number = models.PositiveIntegerField(_("Sıra No"))
    description = models.CharField(_("Açıklama"), max_length=255)

    budgeted_amount = models.DecimalField(
        _("Bütçe Tutarı"), max_digits=15, decimal_places=2
    )
    actual_amount = models.DecimalField(
        _("Gerçekleşen Tutar"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    variance_amount = models.DecimalField(
        _("Sapma Tutarı"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    variance_percentage = models.DecimalField(
        _("Sapma %"), max_digits=8, decimal_places=4, default=Decimal("0")
    )

    # Aylık detay (12 aylık dağılım için)
    january_budget = models.DecimalField(
        _("Ocak Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    february_budget = models.DecimalField(
        _("Şubat Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    march_budget = models.DecimalField(
        _("Mart Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    april_budget = models.DecimalField(
        _("Nisan Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    may_budget = models.DecimalField(
        _("Mayıs Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    june_budget = models.DecimalField(
        _("Haziran Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    july_budget = models.DecimalField(
        _("Temmuz Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    august_budget = models.DecimalField(
        _("Ağustos Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    september_budget = models.DecimalField(
        _("Eylül Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    october_budget = models.DecimalField(
        _("Ekim Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    november_budget = models.DecimalField(
        _("Kasım Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    december_budget = models.DecimalField(
        _("Aralık Bütçe"), max_digits=15, decimal_places=2, default=Decimal("0")
    )

    class Meta:
        verbose_name = _("Bütçe Kalemi")
        verbose_name_plural = _("Bütçe Kalemleri")
        unique_together = [["budget_plan", "line_number"]]
        ordering = ["line_number"]

    def __str__(self):
        return f"{self.budget_plan.name} - {self.description}"

    def calculate_variance(self):
        """Sapmaları hesapla"""
        self.variance_amount = self.actual_amount - self.budgeted_amount
        if self.budgeted_amount != 0:
            self.variance_percentage = (
                self.variance_amount / self.budgeted_amount
            ) * 100
        self.save(update_fields=["variance_amount", "variance_percentage"])


class CashFlowForecast(models.Model):
    """
    Nakit Akış Tahmini
    KOBİ'ler için 13 haftalık rulman nakit akış tahmini
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="cash_flow_forecasts"
    )
    forecast_date = models.DateField(_("Tahmin Tarihi"))
    forecast_name = models.CharField(_("Tahmin Adı"), max_length=100)

    # 13 haftalık projeksiyon
    week_1_net_flow = models.DecimalField(
        _("1. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_2_net_flow = models.DecimalField(
        _("2. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_3_net_flow = models.DecimalField(
        _("3. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_4_net_flow = models.DecimalField(
        _("4. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_5_net_flow = models.DecimalField(
        _("5. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_6_net_flow = models.DecimalField(
        _("6. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_7_net_flow = models.DecimalField(
        _("7. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_8_net_flow = models.DecimalField(
        _("8. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_9_net_flow = models.DecimalField(
        _("9. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_10_net_flow = models.DecimalField(
        _("10. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_11_net_flow = models.DecimalField(
        _("11. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_12_net_flow = models.DecimalField(
        _("12. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    week_13_net_flow = models.DecimalField(
        _("13. Hafta Net Akış"), max_digits=15, decimal_places=2, default=Decimal("0")
    )

    opening_cash_balance = models.DecimalField(
        _("Açılış Nakit Bakiyesi"), max_digits=15, decimal_places=2
    )
    minimum_cash_required = models.DecimalField(
        _("Minimum Nakit Gereksinimi"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
    )

    # Analiz sonuçları
    lowest_cash_balance = models.DecimalField(
        _("En Düşük Nakit Bakiyesi"), max_digits=15, decimal_places=2, null=True
    )
    lowest_cash_week = models.PositiveIntegerField(
        _("En Düşük Bakiye Haftası"), null=True
    )
    cash_shortage_weeks = models.JSONField(
        _("Nakit Sıkıntısı Haftaları"), default=list, blank=True
    )

    # Öneriler ve uyarılar
    recommendations = models.JSONField(_("Öneriler"), default=list, blank=True)
    alerts = models.JSONField(_("Uyarılar"), default=list, blank=True)

    accuracy_score = models.DecimalField(
        _("Doğruluk Skoru %"),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Geçmiş tahminlerin doğruluk oranı",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Nakit Akış Tahmini")
        verbose_name_plural = _("Nakit Akış Tahminleri")
        ordering = ["-forecast_date"]

    def __str__(self):
        return f"{self.company.name} - {self.forecast_name} ({self.forecast_date})"

    def calculate_weekly_balances(self):
        """Haftalık nakit bakiyelerini hesapla ve analiz et"""
        weekly_flows = [
            self.week_1_net_flow,
            self.week_2_net_flow,
            self.week_3_net_flow,
            self.week_4_net_flow,
            self.week_5_net_flow,
            self.week_6_net_flow,
            self.week_7_net_flow,
            self.week_8_net_flow,
            self.week_9_net_flow,
            self.week_10_net_flow,
            self.week_11_net_flow,
            self.week_12_net_flow,
            self.week_13_net_flow,
        ]

        running_balance = self.opening_cash_balance
        lowest_balance = running_balance
        lowest_week = 0
        shortage_weeks = []

        for week, net_flow in enumerate(weekly_flows, 1):
            running_balance += net_flow

            if running_balance < lowest_balance:
                lowest_balance = running_balance
                lowest_week = week

            if running_balance < self.minimum_cash_required:
                shortage_weeks.append(
                    {
                        "week": week,
                        "balance": float(running_balance),
                        "shortage": float(self.minimum_cash_required - running_balance),
                    }
                )

        self.lowest_cash_balance = lowest_balance
        self.lowest_cash_week = lowest_week
        self.cash_shortage_weeks = shortage_weeks

        self._generate_cash_flow_recommendations()
        self._generate_cash_flow_alerts()

        self.save()

    def _generate_cash_flow_recommendations(self):
        """Nakit akış önerilerini oluştur"""
        recommendations = []

        if self.cash_shortage_weeks:
            recommendations.append(
                {
                    "type": "cash_shortage",
                    "priority": "critical",
                    "title": "Nakit Sıkıntısı Uyarısı",
                    "description": f"{len(self.cash_shortage_weeks)} haftada nakit sıkıntısı yaşanabilir.",
                    "action": "Acil finansman planı yapın, alacak tahsilatını hızlandırın.",
                }
            )

        if self.lowest_cash_balance and self.lowest_cash_balance < (
            self.minimum_cash_required * Decimal("1.5")
        ):
            recommendations.append(
                {
                    "type": "low_cash",
                    "priority": "high",
                    "title": "Düşük Nakit Bakiyesi",
                    "description": "Nakit bakiyeniz kritik seviyelere yaklaşıyor.",
                    "action": "Ödeme planlarını gözden geçirin, kredi limiti sağlayın.",
                }
            )

        self.recommendations = recommendations

    def _generate_cash_flow_alerts(self):
        """Nakit akış uyarılarını oluştur"""
        alerts = []

        if self.lowest_cash_balance and self.lowest_cash_balance < 0:
            alerts.append(
                {
                    "type": "negative_balance",
                    "severity": "critical",
                    "message": f"{self.lowest_cash_week}. haftada nakit bakiyesi negatife dönecek.",
                    "amount": float(self.lowest_cash_balance),
                }
            )

        # Büyük nakit çıkışları tespit et
        weekly_flows = [
            self.week_1_net_flow,
            self.week_2_net_flow,
            self.week_3_net_flow,
            self.week_4_net_flow,
            self.week_5_net_flow,
            self.week_6_net_flow,
            self.week_7_net_flow,
            self.week_8_net_flow,
            self.week_9_net_flow,
            self.week_10_net_flow,
            self.week_11_net_flow,
            self.week_12_net_flow,
            self.week_13_net_flow,
        ]

        # Decimal ile karışık tür hatasını önlemek için Decimal toplam ve bölen kullan
        total_flow = sum(weekly_flows, start=Decimal("0"))
        average_flow = (
            (total_flow / Decimal(str(len(weekly_flows))))
            if weekly_flows
            else Decimal("0")
        )
        for week, flow in enumerate(weekly_flows, 1):
            if flow < (average_flow * Decimal("2")) and flow < Decimal(
                "0"
            ):  # %200'den fazla negatif sapma
                alerts.append(
                    {
                        "type": "large_outflow",
                        "severity": "high",
                        "message": f"{week}. haftada büyük nakit çıkışı bekleniyor.",
                        "amount": float(flow),
                    }
                )

        self.alerts = alerts


class ProfitabilityAnalysis(models.Model):
    """
    Karlılık Analizi - Ürün/Hizmet bazlı karlılık takibi
    """

    ANALYSIS_TYPES = [
        ("PRODUCT", _("Ürün Bazlı")),
        ("SERVICE", _("Hizmet Bazlı")),
        ("CUSTOMER", _("Müşteri Bazlı")),
        ("DEPARTMENT", _("Departman Bazlı")),
        ("PROJECT", _("Proje Bazlı")),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="profitability_analyses"
    )
    analysis_name = models.CharField(_("Analiz Adı"), max_length=100)
    analysis_type = models.CharField(
        _("Analiz Tipi"), max_length=20, choices=ANALYSIS_TYPES
    )
    analysis_date = models.DateField(_("Analiz Tarihi"))
    start_date = models.DateField(_("Başlangıç Tarihi"))
    end_date = models.DateField(_("Bitiş Tarihi"))

    # Genel totaller
    total_revenue = models.DecimalField(
        _("Toplam Gelir"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    total_direct_costs = models.DecimalField(
        _("Toplam Direkt Maliyetler"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
    )
    total_indirect_costs = models.DecimalField(
        _("Toplam Endirekt Maliyetler"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
    )
    gross_profit = models.DecimalField(
        _("Brüt Kar"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    net_profit = models.DecimalField(
        _("Net Kar"), max_digits=15, decimal_places=2, default=Decimal("0")
    )

    # Karlılık oranları
    gross_margin_percentage = models.DecimalField(
        _("Brüt Kar Marjı %"), max_digits=8, decimal_places=4, default=Decimal("0")
    )
    net_margin_percentage = models.DecimalField(
        _("Net Kar Marjı %"), max_digits=8, decimal_places=4, default=Decimal("0")
    )

    # En karlı ve en az karlı kalemler
    most_profitable_item = models.JSONField(
        _("En Karlı Kalem"), default=dict, blank=True
    )
    least_profitable_item = models.JSONField(
        _("En Az Karlı Kalem"), default=dict, blank=True
    )

    # Öneriler
    optimization_suggestions = models.JSONField(
        _("Optimizasyon Önerileri"), default=list, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Karlılık Analizi")
        verbose_name_plural = _("Karlılık Analizleri")
        ordering = ["-analysis_date"]

    if TYPE_CHECKING:
        # Django reverse relation (related_name='profitability_lines')
        from django.db.models.manager import RelatedManager

        profitability_lines: "RelatedManager[ProfitabilityLine]"

    def __str__(self):
        return f"{self.analysis_name} - {self.analysis_date}"

    def calculate_totals(self):
        """Toplam değerleri hesapla"""
        lines = self.profitability_lines.all()

        self.total_revenue = lines.aggregate(total=Sum("revenue"))["total"] or Decimal(
            "0"
        )
        self.total_direct_costs = lines.aggregate(total=Sum("direct_costs"))[
            "total"
        ] or Decimal("0")
        self.total_indirect_costs = lines.aggregate(total=Sum("indirect_costs"))[
            "total"
        ] or Decimal("0")

        self.gross_profit = self.total_revenue - self.total_direct_costs
        self.net_profit = self.gross_profit - self.total_indirect_costs

        if self.total_revenue > 0:
            self.gross_margin_percentage = (
                self.gross_profit / self.total_revenue
            ) * 100
            self.net_margin_percentage = (self.net_profit / self.total_revenue) * 100

        self._find_most_least_profitable()
        self._generate_optimization_suggestions()

        self.save()

    def _find_most_least_profitable(self):
        """En karlı ve en az karlı kalemleri bul"""
        lines = self.profitability_lines.all().order_by("-net_margin_percentage")

        if lines.exists():
            most_profitable = lines.first()
            if most_profitable is not None:
                self.most_profitable_item = {
                    "name": most_profitable.item_name,
                    "net_margin": float(most_profitable.net_margin_percentage),
                    "net_profit": float(most_profitable.net_profit),
                }
            least_profitable = lines.last()
            if least_profitable is not None:
                self.least_profitable_item = {
                    "name": least_profitable.item_name,
                    "net_margin": float(least_profitable.net_margin_percentage),
                    "net_profit": float(least_profitable.net_profit),
                }

    def _generate_optimization_suggestions(self):
        """Optimizasyon önerilerini oluştur"""
        suggestions = []

        # Düşük karlılık uyarıları
        low_margin_lines = self.profitability_lines.filter(net_margin_percentage__lt=10)
        if low_margin_lines.exists():
            suggestions.append(
                {
                    "type": "low_margin",
                    "priority": "high",
                    "title": "Düşük Karlılık",
                    "description": f"{low_margin_lines.count()} kalem %10'un altında kar marjına sahip.",
                    "action": "Bu kalemlerin fiyatlandırmasını gözden geçirin veya maliyetlerini azaltın.",
                }
            )

        # Zarar eden kalemler
        loss_making_lines = self.profitability_lines.filter(net_profit__lt=0)
        if loss_making_lines.exists():
            suggestions.append(
                {
                    "type": "loss_making",
                    "priority": "critical",
                    "title": "Zarar Eden Kalemler",
                    "description": f"{loss_making_lines.count()} kalem zarar ediyor.",
                    "action": "Bu kalemleri portföyünüzden çıkarmayı veya ciddi maliyet düşürmeyi değerlendirin.",
                }
            )

        self.optimization_suggestions = suggestions


class ProfitabilityLine(models.Model):
    """Karlılık Analizi Detay Satırları"""

    analysis = models.ForeignKey(
        ProfitabilityAnalysis,
        on_delete=models.CASCADE,
        related_name="profitability_lines",
        verbose_name=_("Analiz"),
    )
    item_code = models.CharField(_("Kalem Kodu"), max_length=50)
    item_name = models.CharField(_("Kalem Adı"), max_length=200)

    quantity_sold = models.DecimalField(
        _("Satılan Miktar"), max_digits=15, decimal_places=3, default=Decimal("0")
    )
    revenue = models.DecimalField(_("Gelir"), max_digits=15, decimal_places=2)
    direct_costs = models.DecimalField(
        _("Direkt Maliyetler"), max_digits=15, decimal_places=2
    )
    indirect_costs = models.DecimalField(
        _("Endirekt Maliyetler"), max_digits=15, decimal_places=2, default=Decimal("0")
    )

    gross_profit = models.DecimalField(
        _("Brüt Kar"), max_digits=15, decimal_places=2, default=Decimal("0")
    )
    net_profit = models.DecimalField(
        _("Net Kar"), max_digits=15, decimal_places=2, default=Decimal("0")
    )

    gross_margin_percentage = models.DecimalField(
        _("Brüt Kar Marjı %"), max_digits=8, decimal_places=4, default=Decimal("0")
    )
    net_margin_percentage = models.DecimalField(
        _("Net Kar Marjı %"), max_digits=8, decimal_places=4, default=Decimal("0")
    )

    # Ek bilgiler
    cost_center = models.CharField(_("Masraf Merkezi"), max_length=50, blank=True)
    customer_segment = models.CharField(
        _("Müşteri Segmenti"), max_length=50, blank=True
    )

    class Meta:
        verbose_name = _("Karlılık Detayı")
        verbose_name_plural = _("Karlılık Detayları")
        ordering = ["-net_margin_percentage"]

    def __str__(self):
        return f"{self.item_name} - %{self.net_margin_percentage}"

    def calculate_margins(self):
        """Kar marjlarını hesapla"""
        self.gross_profit = self.revenue - self.direct_costs
        self.net_profit = self.gross_profit - self.indirect_costs

        if self.revenue > 0:
            self.gross_margin_percentage = (self.gross_profit / self.revenue) * 100
            self.net_margin_percentage = (self.net_profit / self.revenue) * 100

        self.save(
            update_fields=[
                "gross_profit",
                "net_profit",
                "gross_margin_percentage",
                "net_margin_percentage",
            ]
        )
