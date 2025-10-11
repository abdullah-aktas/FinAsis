# -*- coding: utf-8 -*-
"""
FinAsis - Geliştirilmiş Muhasebe Modülleri
KOBİ gereksinimlerini karşılamak için kapsamlı muhasebe yapısı
"""

from decimal import Decimal
from django.db import models
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q, F
from django.db import transaction
from django.utils import timezone
from django.conf import settings as dj_settings
import uuid
# Use Django's built-in JSONField to avoid postgres-specific dependency

from src.apps.accounting.models import Company, Customer

# Tip denetleyicilerinin (pyright/mypy) Django'nun runtime'da eklediği reverse relation
# yöneticilerini (related_name ile gelen) tanıması için TYPE_CHECKING bloklarında
# stub alanlar tanımlanır. Bu, gerçek çalışmayı etkilemez (runtime'da yürütülmez) ancak
# "attr-defined" uyarılarını temizler.
if TYPE_CHECKING:  # pragma: no cover - sadece statik analiz için
    from django.db.models.manager import RelatedManager


class ChartOfAccounts(models.Model):
    """
    Türk Standart Hesap Planı (STHP) 
    KOBİ'ler için uyarlanmış hesap planı
    """
    ACCOUNT_TYPES = [
        ('1', _('Dönen Varlıklar')),
        ('2', _('Duran Varlıklar')),
        ('3', _('Kısa Vadeli Yabancı Kaynaklar')),
        ('4', _('Uzun Vadeli Yabancı Kaynaklar')),
        ('5', _('Özkaynaklar')),
        ('6', _('Gelir Hesapları')),
        ('7', _('Maliyet Hesapları')),
        ('8', _('Gider Hesapları')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='chart_of_accounts')
    code = models.CharField(_('Hesap Kodu'), max_length=20, help_text="Örn: 100, 120.01")
    name = models.CharField(_('Hesap Adı'), max_length=200)
    account_type = models.CharField(_('Ana Grup'), max_length=1, choices=ACCOUNT_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='sub_accounts', verbose_name=_('Ana Hesap'))
    level = models.PositiveIntegerField(_('Seviye'), default=1)
    is_detail_account = models.BooleanField(_('Detay Hesap'), default=False, 
                                          help_text="Bu hesaba doğrudan kayıt yapılabilir mi?")
    is_active = models.BooleanField(_('Aktif'), default=True)
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Hesap Planı')
        verbose_name_plural = _('Hesap Planları')
        unique_together = [['company', 'code']]
        ordering = ['code']

    if TYPE_CHECKING:  # pragma: no cover
        id: int  # Django PK
        sub_accounts: 'RelatedManager["ChartOfAccounts"]'
        journal_entries: 'RelatedManager["JournalEntry"]'
        
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        if self.parent and self.parent.company != self.company:
            raise ValidationError(_('Ana hesap aynı şirkete ait olmalıdır.'))
            
        if self.is_detail_account and self.sub_accounts.exists():
            raise ValidationError(_('Alt hesabı olan hesap detay hesap olamaz.'))
    
    def get_balance(self, start_date=None, end_date=None):
        """Hesabın belirli tarih aralığındaki bakiyesi.
        JournalEntry üzerinde is_posted veya date alanı yok; filtre voucher üzerinden yapılmalı.
        """
        entries = JournalEntry.objects.filter(account=self, voucher__is_posted=True)
        if start_date:
            entries = entries.filter(voucher__date__gte=start_date)
        if end_date:
            entries = entries.filter(voucher__date__lte=end_date)

        aggregated = entries.aggregate(
            debit_total=Sum('debit_amount'),
            credit_total=Sum('credit_amount')
        )
        debits = aggregated['debit_total'] or Decimal('0')
        credits = aggregated['credit_total'] or Decimal('0')

        # Aktif (varlık ve gider) hesaplar için Borç - Alacak, pasif ve gelir hesapları için Alacak - Borç
        return (debits - credits) if self.account_type in ['1', '2', '7', '8'] else (credits - debits)


class FiscalPeriod(models.Model):
    """Mali Dönem Yönetimi"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='fiscal_periods')
    name = models.CharField(_('Dönem Adı'), max_length=100, help_text="Örn: 2024 Mali Yılı")
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    is_closed = models.BooleanField(_('Kapalı'), default=False)
    closed_at = models.DateTimeField(_('Kapanış Zamanı'), null=True, blank=True)
    closed_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                 null=True, blank=True, verbose_name=_('Kapatan Kullanıcı'))
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('Mali Dönem')
        verbose_name_plural = _('Mali Dönemler')
        unique_together = [['company', 'start_date', 'end_date']]
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.company} - {self.name}"
    
    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError(_('Başlangıç tarihi bitiş tarihinden küçük olmalıdır.'))


class JournalVoucher(models.Model):
    """Yevmiye Fişi (Muhasebe Fişi)"""
    VOUCHER_TYPES = [
        ('GENERAL', _('Genel Yevmiye')),
        ('PURCHASE', _('Alış Faturası')),
        ('SALE', _('Satış Faturası')),
        ('CASH', _('Kasa')),
        ('BANK', _('Banka')),
        ('PAYROLL', _('Bordro')),
        ('DEPRECIATION', _('Amortisman')),
        ('ADJUSTMENT', _('Düzeltme')),
        ('CLOSING', _('Kapanış')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='journal_vouchers')
    voucher_number = models.CharField(_('Fiş Numarası'), max_length=20, help_text="Şirket bazında benzersiz")
    voucher_type = models.CharField(_('Fiş Tipi'), max_length=20, choices=VOUCHER_TYPES)
    date = models.DateField(_('Tarih'))
    fiscal_period = models.ForeignKey(FiscalPeriod, on_delete=models.PROTECT, 
                                     related_name='journal_vouchers', verbose_name=_('Mali Dönem'))
    description = models.TextField(_('Açıklama'))
    reference_number = models.CharField(_('Referans No'), max_length=100, blank=True,
                                       help_text="Fatura no, dekont no vb.")
    total_debit = models.DecimalField(_('Toplam Borç'), max_digits=15, decimal_places=2, default=Decimal('0'))
    total_credit = models.DecimalField(_('Toplam Alacak'), max_digits=15, decimal_places=2, default=Decimal('0'))
    is_posted = models.BooleanField(_('Kaydedildi'), default=False)
    is_balanced = models.BooleanField(_('Dengeli'), default=False)
    
    created_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, related_name='created_vouchers', verbose_name=_('Oluşturan'))
    posted_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name='posted_vouchers', 
                                 verbose_name=_('Kaydeden'))
    posted_at = models.DateTimeField(_('Kayıt Zamanı'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Yevmiye Fişi')
        verbose_name_plural = _('Yevmiye Fişleri')
        ordering = ['-date', '-voucher_number']
        unique_together = [['company', 'voucher_number']]
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['company', 'voucher_type']),
            models.Index(fields=['is_posted']),
        ]

    if TYPE_CHECKING:  # pragma: no cover
        journal_entries: 'RelatedManager["JournalEntry"]'
        
    def __str__(self):
        return f"{self.voucher_number} - {self.description[:50]}"
    
    def clean(self):
        # Mali dönem şirket uyumu
        if self.fiscal_period and self.fiscal_period.company != self.company:
            raise ValidationError(_('Mali dönem şirketle uyuşmuyor.'))

        # Tarih mali dönem içinde olmalı
        if self.fiscal_period and (self.date < self.fiscal_period.start_date or self.date > self.fiscal_period.end_date):
            raise ValidationError(_('Fiş tarihi seçili mali dönem içerisinde olmalıdır.'))

        # Kapalı dönem kontrolü
        if self.fiscal_period and self.fiscal_period.is_closed:
            raise ValidationError(_('Kapalı mali döneme fiş kaydedilemez.'))

        # Dengeli değilse post edilemez
        if self.is_posted and not self.is_balanced:
            raise ValidationError(_('Dengesiz fiş kaydedilemez.'))
    
    def calculate_totals(self, save=True):
        """Fiş toplamlarını hesapla ve dengesini güncelle."""
        aggregated = self.journal_entries.aggregate(
            debit_total=Sum('debit_amount'),
            credit_total=Sum('credit_amount')
        )
        self.total_debit = aggregated['debit_total'] or Decimal('0')
        self.total_credit = aggregated['credit_total'] or Decimal('0')
        self.is_balanced = self.total_debit == self.total_credit
        if save:
            self.save(update_fields=['total_debit', 'total_credit', 'is_balanced'])
    
    def post(self, user):
        """Fişi kaydet/onayla"""
        if self.is_posted:
            raise ValidationError(_('Fiş zaten kaydedilmiş.'))
            
        if not self.is_balanced:
            raise ValidationError(_('Fiş dengeli değil, kaydedilemez.'))
            
        self.is_posted = True
        self.posted_by = user
        self.posted_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):  # noqa: D401
        """Kapalı dönemde değişiklik engeli eklenmiş override."""
        if self.pk and self.fiscal_period and self.fiscal_period.is_closed:
            raise ValidationError(_('Kapalı dönemde fiş üzerinde değişiklik yapılamaz.'))
        super().save(*args, **kwargs)


class JournalEntry(models.Model):
    """Yevmiye Kaydı (Muhasebe Kaydının Satırları)"""
    voucher = models.ForeignKey(JournalVoucher, on_delete=models.CASCADE, 
                               related_name='journal_entries', verbose_name=_('Fiş'))
    line_number = models.PositiveIntegerField(_('Satır No'))
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, 
                               related_name='journal_entries', verbose_name=_('Hesap'))
    description = models.CharField(_('Açıklama'), max_length=255, blank=True)
    debit_amount = models.DecimalField(_('Borç Tutarı'), max_digits=15, decimal_places=2, 
                                      default=Decimal('0'), validators=[MinValueValidator(0)])
    credit_amount = models.DecimalField(_('Alacak Tutarı'), max_digits=15, decimal_places=2, 
                                       default=Decimal('0'), validators=[MinValueValidator(0)])
    
    # Ek bilgiler
    cost_center = models.CharField(_('Masraf Merkezi'), max_length=50, blank=True)
    project_code = models.CharField(_('Proje Kodu'), max_length=50, blank=True)
    currency_code = models.CharField(_('Para Birimi'), max_length=3, default='TRY')
    exchange_rate = models.DecimalField(_('Döviz Kuru'), max_digits=10, decimal_places=4, default=Decimal('1'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Yevmiye Kaydı')
        verbose_name_plural = _('Yevmiye Kayıtları')
        unique_together = [['voucher', 'line_number']]
        ordering = ['voucher', 'line_number']
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['voucher', 'account']),
        ]
        
    def __str__(self):
        return f"{self.voucher.voucher_number}/{self.line_number} - {self.account.code}"
    
    def clean(self):
        # Hem borç hem alacak dolu olamaz
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError(_('Bir kayıtta hem borç hem alacak tutar olamaz.'))
            
        # En az biri dolu olmalı
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError(_('Borç veya alacak tutarından en az biri girilmelidir.'))
            
        # Detay hesap kontrolü
        if not self.account.is_detail_account:
            raise ValidationError(_('Sadece detay hesaplara kayıt yapılabilir.'))

    def save(self, *args, **kwargs):
        """Kaydı kaydettikten sonra fiş toplamlarını güncelle.
        Transaction içinde çağrılırsa gereksiz ek sorgu minimize edilir.
        """
        super().save(*args, **kwargs)
        # Toplamların güncellenmesi
        self.voucher.calculate_totals(save=True)


class DepreciationMethod(models.Model):
    """Amortisman Yöntemleri"""
    METHODS = [
        ('STRAIGHT_LINE', _('Doğrusal (Normal) Amortisman')),
        ('DECLINING_BALANCE', _('Azalan Bakiye')),
        ('UNITS_OF_PRODUCTION', _('Üretim Miktarı')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='depreciation_methods')
    name = models.CharField(_('Yöntem Adı'), max_length=100)
    method_type = models.CharField(_('Yöntem Tipi'), max_length=20, choices=METHODS)
    rate_percentage = models.DecimalField(_('Oran %'), max_digits=5, decimal_places=2, 
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField(_('Açıklama'), blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    
    class Meta:
        verbose_name = _('Amortisman Yöntemi')
        verbose_name_plural = _('Amortisman Yöntemleri')
        
    def __str__(self):
        return f"{self.name} (%{self.rate_percentage})"


class FixedAsset(models.Model):
    """Demirbaş/Sabit Kıymet Yönetimi"""
    ASSET_STATUS = [
        ('ACTIVE', _('Aktif')),
        ('DISPOSED', _('Elden Çıkarılmış')),
        ('UNDER_CONSTRUCTION', _('Yapım Halinde')),
        ('IDLE', _('Atıl')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='fixed_assets')
    asset_code = models.CharField(_('Demirbaş Kodu'), max_length=50, unique=True)
    name = models.CharField(_('Demirbaş Adı'), max_length=200)
    description = models.TextField(_('Açıklama'), blank=True)
    
    # Mali bilgiler
    cost_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, 
                                    related_name='fixed_assets_cost', verbose_name=_('Maliyet Hesabı'))
    accumulated_depreciation_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT,
                                                        related_name='fixed_assets_depreciation',
                                                        verbose_name=_('Birikmiş Amortisman Hesabı'))
    
    purchase_date = models.DateField(_('Satın Alma Tarihi'))
    purchase_cost = models.DecimalField(_('Satın Alma Maliyeti'), max_digits=15, decimal_places=2)
    useful_life_years = models.PositiveIntegerField(_('Faydalı Ömür (Yıl)'))
    salvage_value = models.DecimalField(_('Hurda Değeri'), max_digits=15, decimal_places=2, default=Decimal('0'))
    
    depreciation_method = models.ForeignKey(DepreciationMethod, on_delete=models.PROTECT,
                                          verbose_name=_('Amortisman Yöntemi'))
    depreciation_start_date = models.DateField(_('Amortisman Başlangıç Tarihi'))
    
    status = models.CharField(_('Durum'), max_length=20, choices=ASSET_STATUS, default='ACTIVE')
    location = models.CharField(_('Konum'), max_length=100, blank=True)
    responsible_person = models.CharField(_('Sorumlu Kişi'), max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Sabit Kıymet')
        verbose_name_plural = _('Sabit Kıymetler')
        ordering = ['asset_code']

    if TYPE_CHECKING:  # pragma: no cover
        depreciation_entries: 'RelatedManager["DepreciationEntry"]'
        
    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    
    def calculate_annual_depreciation(self):
        """Yıllık amortisman tutarını hesapla"""
        if self.depreciation_method.method_type == 'STRAIGHT_LINE':
            return (self.purchase_cost - self.salvage_value) / self.useful_life_years
        elif self.depreciation_method.method_type == 'DECLINING_BALANCE':
            # Azalan bakiye yöntemi için
            rate = self.depreciation_method.rate_percentage / 100
            return self.get_book_value() * rate
        return Decimal('0')
    
    def get_book_value(self, as_of_date=None):
        """Net defter değerini hesapla"""
        if not as_of_date:
            as_of_date = timezone.now().date()
            
        total_depreciation = self.depreciation_entries.filter(
            date__lte=as_of_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        return self.purchase_cost - total_depreciation


class DepreciationEntry(models.Model):
    """Amortisman Kaydı"""
    fixed_asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, 
                                   related_name='depreciation_entries', verbose_name=_('Sabit Kıymet'))
    fiscal_period = models.ForeignKey(FiscalPeriod, on_delete=models.PROTECT, 
                                     related_name='depreciation_entries')
    date = models.DateField(_('Tarih'))
    amount = models.DecimalField(_('Amortisman Tutarı'), max_digits=15, decimal_places=2)
    voucher = models.ForeignKey(JournalVoucher, on_delete=models.PROTECT, null=True, blank=True,
                               verbose_name=_('Yevmiye Fişi'))
    
    notes = models.TextField(_('Notlar'), blank=True)
    is_automatic = models.BooleanField(_('Otomatik'), default=True, 
                                      help_text="Sistem tarafından otomatik hesaplanan")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Amortisman Kaydı')
        verbose_name_plural = _('Amortisman Kayıtları')
        unique_together = [['fixed_asset', 'fiscal_period', 'date']]
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.fixed_asset.asset_code} - {self.date} - {self.amount}"


class TaxRate(models.Model):
    """Vergi Oranları (KDV, ÖTV, vb.)"""
    TAX_TYPES = [
        ('VAT', _('KDV')),
        ('SCT', _('ÖTV')),  # Özel Tüketim Vergisi
        ('WHT', _('Stopaj')),  # Withholding Tax
        ('STAMP', _('Damga Vergisi')),
        ('OTHER', _('Diğer')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tax_rates')
    name = models.CharField(_('Vergi Adı'), max_length=100)
    tax_type = models.CharField(_('Vergi Tipi'), max_length=10, choices=TAX_TYPES)
    rate_percentage = models.DecimalField(_('Oran %'), max_digits=5, decimal_places=2)
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, 
                               related_name='tax_rates', verbose_name=_('Vergi Hesabı'))
    
    valid_from = models.DateField(_('Geçerlilik Başlangıcı'))
    valid_to = models.DateField(_('Geçerlilik Bitişi'), null=True, blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    
    description = models.TextField(_('Açıklama'), blank=True)
    
    class Meta:
        verbose_name = _('Vergi Oranı')
        verbose_name_plural = _('Vergi Oranları')
        ordering = ['tax_type', 'rate_percentage']
        
    def __str__(self):
        return f"{self.name} (%{self.rate_percentage})"


class CostCenter(models.Model):
    """Masraf Merkezi - Departman Bazlı Maliyet Takibi"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cost_centers')
    code = models.CharField(_('Masraf Merkezi Kodu'), max_length=20)
    name = models.CharField(_('Masraf Merkezi Adı'), max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='sub_centers', verbose_name=_('Ana Masraf Merkezi'))
    manager = models.CharField(_('Sorumlu'), max_length=100, blank=True)
    budget_account = models.ForeignKey(ChartOfAccounts, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name=_('Bütçe Hesabı'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    description = models.TextField(_('Açıklama'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Masraf Merkezi')
        verbose_name_plural = _('Masraf Merkezleri')
        unique_together = [['company', 'code']]
        ordering = ['code']
        
    def __str__(self):
        return f"{self.code} - {self.name}"


class InventoryItem(models.Model):
    """Stok Kalemi - KOBİ Stok Yönetimi"""
    INVENTORY_TYPES = [
        ('RAW_MATERIAL', _('Hammadde')),
        ('FINISHED_GOODS', _('Mamul')),
        ('MERCHANDISE', _('Ticari Mal')),
        ('CONSUMABLES', _('Sarf Malzemesi')),
        ('PACKAGING', _('Ambalaj')),
    ]
    
    VALUATION_METHODS = [
        ('FIFO', _('İlk Giren İlk Çıkar')),
        ('LIFO', _('Son Giren İlk Çıkar')),
        ('WEIGHTED_AVERAGE', _('Ağırlıklı Ortalama')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inventory_items')
    item_code = models.CharField(_('Stok Kodu'), max_length=50)
    name = models.CharField(_('Stok Adı'), max_length=200)
    description = models.TextField(_('Açıklama'), blank=True)
    
    inventory_type = models.CharField(_('Stok Tipi'), max_length=20, choices=INVENTORY_TYPES)
    unit_of_measure = models.CharField(_('Ölçü Birimi'), max_length=10, default='ADET',
                                      help_text="KG, LT, M2, ADET vb.")
    
    # Mali bilgiler
    inventory_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT,
                                         related_name='inventory_items', verbose_name=_('Stok Hesabı'))
    cost_of_sales_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT,
                                             related_name='inventory_costs', 
                                             verbose_name=_('Satılan Malın Maliyeti Hesabı'))
    
    valuation_method = models.CharField(_('Değerleme Yöntemi'), max_length=20, 
                                       choices=VALUATION_METHODS, default='WEIGHTED_AVERAGE')
    
    # Stok seviyeleri
    current_quantity = models.DecimalField(_('Mevcut Miktar'), max_digits=15, decimal_places=3, default=Decimal('0'))
    minimum_quantity = models.DecimalField(_('Minimum Miktar'), max_digits=15, decimal_places=3, default=Decimal('0'))
    maximum_quantity = models.DecimalField(_('Maksimum Miktar'), max_digits=15, decimal_places=3, default=Decimal('0'))
    
    # Fiyat bilgileri
    last_purchase_price = models.DecimalField(_('Son Alış Fiyatı'), max_digits=15, decimal_places=4, default=Decimal('0'))
    average_cost = models.DecimalField(_('Ortalama Maliyet'), max_digits=15, decimal_places=4, default=Decimal('0'))
    standard_selling_price = models.DecimalField(_('Standart Satış Fiyatı'), max_digits=15, decimal_places=4, default=Decimal('0'))
    
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Stok Kalemi')
        verbose_name_plural = _('Stok Kalemleri')
        unique_together = [['company', 'item_code']]
        ordering = ['item_code']

    if TYPE_CHECKING:  # pragma: no cover
        stock_movements: 'RelatedManager["StockMovement"]'
        
    def __str__(self):
        return f"{self.item_code} - {self.name}"
    
    def update_average_cost(self):
        """Ağırlıklı ortalama maliyet hesapla"""
        movements = self.stock_movements.filter(is_inbound=True)
        total_cost = movements.aggregate(
            total=Sum(models.F('quantity') * models.F('unit_cost'))
        )['total'] or Decimal('0')
        total_quantity = movements.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        if total_quantity > 0:
            self.average_cost = total_cost / total_quantity
            self.save(update_fields=['average_cost'])


class StockMovement(models.Model):
    """Stok Hareketi"""
    MOVEMENT_TYPES = [
        ('PURCHASE', _('Alış')),
        ('SALE', _('Satış')),
        ('PRODUCTION', _('Üretim')),
        ('ADJUSTMENT', _('Sayım Farkı')),
        ('TRANSFER', _('Transfer')),
        ('RETURN', _('İade')),
        ('WASTE', _('Fire')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_movements')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, 
                                      related_name='stock_movements', verbose_name=_('Stok Kalemi'))
    
    movement_type = models.CharField(_('Hareket Tipi'), max_length=20, choices=MOVEMENT_TYPES)
    date = models.DateField(_('Tarih'))
    quantity = models.DecimalField(_('Miktar'), max_digits=15, decimal_places=3)
    unit_cost = models.DecimalField(_('Birim Maliyet'), max_digits=15, decimal_places=4)
    total_cost = models.DecimalField(_('Toplam Maliyet'), max_digits=15, decimal_places=2)
    
    is_inbound = models.BooleanField(_('Giriş'), help_text="True: Giriş, False: Çıkış")
    reference_document = models.CharField(_('Referans Belge'), max_length=100, blank=True,
                                        help_text="Fatura no, irsaliye no vb.")
    
    voucher = models.ForeignKey(JournalVoucher, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name=_('Muhasebe Fişi'))
    
    description = models.TextField(_('Açıklama'), blank=True)
    created_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Stok Hareketi')
        verbose_name_plural = _('Stok Hareketleri')
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f"{self.inventory_item.item_code} - {self.movement_type} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Stok hareketi kaydı: toplam maliyet hesapla, miktarı güncelle ve ortalama maliyeti güncelle.
        Atomik transaction ile yarış koşullarını azaltır.
        """
        with transaction.atomic():
            self.total_cost = self.quantity * self.unit_cost
            super().save(*args, **kwargs)

            # Miktar güncelle (F expression ile yarış koşulu azaltılır)
            if self.is_inbound:
                InventoryItem.objects.filter(pk=self.inventory_item.pk).update(
                    current_quantity=F('current_quantity') + self.quantity,
                    last_purchase_price=self.unit_cost if self.movement_type == 'PURCHASE' else F('last_purchase_price')
                )
            else:
                InventoryItem.objects.filter(pk=self.inventory_item.pk).update(
                    current_quantity=F('current_quantity') - self.quantity
                )

            # Instance'ı tazele
            self.inventory_item.refresh_from_db(fields=['current_quantity', 'last_purchase_price'])

            # Ortalama maliyeti inbound hareketlerde güncelle
            if self.is_inbound:
                self.inventory_item.update_average_cost()


# Mali tablolar için yardımcı fonksiyonlar
class FinancialStatementGenerator:
    """Mali Tablo Üretici"""
    
    def __init__(self, company, start_date, end_date):
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
    
    def generate_balance_sheet(self):
        """Bilanço üret (tek agregasyon passı ile optimize)."""
        balance_sheet = {
            'aktif': {
                'donen_varliklar': {},
                'duran_varliklar': {},
                'toplam_aktif': Decimal('0')
            },
            'pasif': {
                'kisa_vadeli_borclar': {},
                'uzun_vadeli_borclar': {},
                'ozkaynaklar': {},
                'toplam_pasif': Decimal('0')
            }
        }

        detail_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            is_detail_account=True,
            account_type__in=['1', '2', '3', '4', '5']
        )

        # İlgili entry'leri tek seferde çekip hesap koduna göre gruplayalım
        entries = (JournalEntry.objects
                   .filter(voucher__company=self.company,
                           voucher__is_posted=True,
                           voucher__date__gte=self.start_date,
                           voucher__date__lte=self.end_date,
                           account__in=detail_accounts)
                   .values('account_id')
                   .annotate(debit_total=Sum('debit_amount'), credit_total=Sum('credit_amount')))

        # Hızlı lookup için dict
        totals_map = {row['account_id']: (row['debit_total'] or Decimal('0'), row['credit_total'] or Decimal('0'))
                      for row in entries}

        for acc in detail_accounts:
            debits, credits = totals_map.get(acc.id, (Decimal('0'), Decimal('0')))
            balance = (debits - credits) if acc.account_type in ['1', '2'] else (credits - debits)
            if acc.account_type == '1':
                balance_sheet['aktif']['donen_varliklar'][acc.code] = {'name': acc.name, 'balance': balance}
                balance_sheet['aktif']['toplam_aktif'] += balance
            elif acc.account_type == '2':
                balance_sheet['aktif']['duran_varliklar'][acc.code] = {'name': acc.name, 'balance': balance}
                balance_sheet['aktif']['toplam_aktif'] += balance
            elif acc.account_type == '3':
                balance_sheet['pasif']['kisa_vadeli_borclar'][acc.code] = {'name': acc.name, 'balance': balance}
                balance_sheet['pasif']['toplam_pasif'] += balance
            elif acc.account_type == '4':
                balance_sheet['pasif']['uzun_vadeli_borclar'][acc.code] = {'name': acc.name, 'balance': balance}
                balance_sheet['pasif']['toplam_pasif'] += balance
            elif acc.account_type == '5':
                balance_sheet['pasif']['ozkaynaklar'][acc.code] = {'name': acc.name, 'balance': balance}
                balance_sheet['pasif']['toplam_pasif'] += balance

        return balance_sheet
    
    def generate_income_statement(self):
        """Gelir Tablosu üret (optimize)."""
        income_statement = {
            'gelirler': {},
            'giderler': {},
            'net_kar_zarar': Decimal('0'),
            'toplam_gelir': Decimal('0'),
            'toplam_gider': Decimal('0')
        }

        accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            is_detail_account=True,
            account_type__in=['6', '7', '8']
        )

        entries = (JournalEntry.objects
                   .filter(voucher__company=self.company,
                           voucher__is_posted=True,
                           voucher__date__gte=self.start_date,
                           voucher__date__lte=self.end_date,
                           account__in=accounts)
                   .values('account_id')
                   .annotate(debit_total=Sum('debit_amount'), credit_total=Sum('credit_amount')))
        totals_map = {row['account_id']: (row['debit_total'] or Decimal('0'), row['credit_total'] or Decimal('0'))
                      for row in entries}

        for acc in accounts:
            debits, credits = totals_map.get(acc.id, (Decimal('0'), Decimal('0')))
            # Gelir (6) pasif yapıda -> Alacak - Borç; gider (7,8) aktif -> Borç - Alacak
            if acc.account_type == '6':
                balance = credits - debits
                income_statement['gelirler'][acc.code] = {'name': acc.name, 'balance': balance}
                income_statement['toplam_gelir'] += balance
            else:
                balance = debits - credits
                income_statement['giderler'][acc.code] = {'name': acc.name, 'balance': balance}
                income_statement['toplam_gider'] += balance

        income_statement['net_kar_zarar'] = income_statement['toplam_gelir'] - income_statement['toplam_gider']
        return income_statement


class TrialBalanceSnapshot(models.Model):
    """Genel Geçici Mizan Anlık Görüntüsü (Cache)
    Kapama sırasında performans için hesap bakiyeleri saklanır.
    account_balances JSON formatında: {account_code: {name: str, debit: str, credit: str, balance: str}}
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='trial_balance_snapshots')
    fiscal_period = models.ForeignKey(FiscalPeriod, on_delete=models.CASCADE, related_name='trial_balance_snapshots')
    as_of_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    account_balances = models.JSONField(default=dict)  # Django 3.1+ built-in JSONField
    total_debits = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0'))
    total_credits = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0'))

    class Meta:
        verbose_name = _('Mizan Anlık Görüntüsü')
        verbose_name_plural = _('Mizan Anlık Görüntüleri')
        unique_together = [('company', 'fiscal_period', 'as_of_date')]
        ordering = ['-as_of_date']
        indexes = [
            models.Index(fields=['company', 'as_of_date'])
        ]

    def __str__(self):  # pragma: no cover - basit
        return f"{self.company} - {self.fiscal_period} - {self.as_of_date}"

    @classmethod
    def build_snapshot(cls, company, fiscal_period, as_of_date=None, user=None):
        """Hızlı mizan üretip kayıt eder."""
        if as_of_date is None:
            as_of_date = fiscal_period.end_date

        # İlgili yevmiye kayıtları (post edilmiş) tek agregasyon passı
        entries = (JournalEntry.objects
                   .filter(voucher__company=company,
                           voucher__is_posted=True,
                           voucher__date__lte=as_of_date)
                   .values('account_id', 'account__code', 'account__name', 'account__account_type')
                   .annotate(debit_total=Sum('debit_amount'), credit_total=Sum('credit_amount')))

        account_balances = {}
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        for row in entries:
            debit = row['debit_total'] or Decimal('0')
            credit = row['credit_total'] or Decimal('0')
            balance = (debit - credit) if row['account__account_type'] in ['1','2','7','8'] else (credit - debit)
            account_balances[row['account__code']] = {
                'name': row['account__name'],
                'debit': str(debit),
                'credit': str(credit),
                'balance': str(balance)
            }
            total_debits += debit
            total_credits += credit

        snapshot, _ = cls.objects.update_or_create(
            company=company,
            fiscal_period=fiscal_period,
            as_of_date=as_of_date,
            defaults={
                'account_balances': account_balances,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'created_by': user
            }
        )
        return snapshot