# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - Modeller

Bu modül, muhasebe işlemleri için gerekli veritabanı modellerini içerir.
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from apps.core.models import BaseModel, AuditableMixin
from apps.company.models import Company, FiscalYear


class AccountType(models.Model):
    """
    Hesap Türü
    
    Muhasebe hesap planı içindeki hesap türlerini tanımlar 
    (Aktif, Pasif, Gelir, Gider, vb.)
    """
    code = models.CharField(_("Kod"), max_length=10, unique=True)
    name = models.CharField(_("Ad"), max_length=100)
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    is_active = models.BooleanField(_("Aktif"), default=True)
    
    class Meta:
        verbose_name = _("Hesap Tipi")
        verbose_name_plural = _("Hesap Tipleri")
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Account(models.Model):
    """
    Muhasebe Hesabı
    
    Tek düzen hesap planına uygun hesap yapısını tanımlar.
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name=_("Şirket")
    )
    code = models.CharField(_("Hesap Kodu"), max_length=20)
    name = models.CharField(_("Hesap Adı"), max_length=150)
    type = models.ForeignKey(
        AccountType, 
        on_delete=models.PROTECT,
        related_name='accounts',
        verbose_name=_("Hesap Tipi")
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='sub_accounts',
        verbose_name=_("Üst Hesap")
    )
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    is_tax_account = models.BooleanField(_("Vergi Hesabı"), default=False)
    is_bank_account = models.BooleanField(_("Banka Hesabı"), default=False)
    is_cash_account = models.BooleanField(_("Kasa Hesabı"), default=False)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)
    created_by = models.ForeignKey(
        "apps.hr_management.User", 
        on_delete=models.SET_NULL, 
        verbose_name=_("Oluşturan"),
        related_name="created_accounts",
        blank=True, 
        null=True
    )
    updated_by = models.ForeignKey(
        "apps.hr_management.User", 
        on_delete=models.SET_NULL, 
        verbose_name=_("Güncelleyen"),
        related_name="updated_accounts",
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _("Hesap")
        verbose_name_plural = _("Hesaplar")
        ordering = ['company', 'code']
        unique_together = [('company', 'code')]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def full_name(self):
        """Hesap kodu ve adını birlikte döndürür"""
        return f"{self.code} - {self.name}"
    
    @property
    def is_leaf(self):
        """Hesabın alt hesapları olup olmadığını kontrol eder"""
        return not self.sub_accounts.exists()
    
    @property
    def level(self):
        """Hesabın hiyerarşideki seviyesini döndürür"""
        if not self.parent:
            return 1
        return self.parent.level + 1

    def get_balance(self, start_date=None, end_date=None):
        """
        Hesabın belirtilen tarih aralığındaki bakiyesini hesaplar.
        """
        from apps.finance.accounting.models import VoucherLine
        
        query = VoucherLine.objects.filter(account=self)
        
        if start_date:
            query = query.filter(voucher__date__gte=start_date)
        
        if end_date:
            query = query.filter(voucher__date__lte=end_date)
        
        totals = query.aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount')
        )
        
        total_debit = totals['total_debit'] or Decimal('0')
        total_credit = totals['total_credit'] or Decimal('0')
        
        return total_debit - total_credit


class VoucherType(models.Model):
    """
    Fiş Türü
    
    Muhasebe fişlerinin türlerini tanımlar (Tahsilat, Tediye, Mahsup, vb.)
    """
    code = models.CharField(_("Kod"), max_length=10, unique=True)
    name = models.CharField(_("Ad"), max_length=100)
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    prefix = models.CharField(_("Önek"), max_length=5, blank=True, null=True)
    is_active = models.BooleanField(_("Aktif"), default=True)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)
    
    class Meta:
        verbose_name = _("Fiş Tipi")
        verbose_name_plural = _("Fiş Tipleri")
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Currency(models.Model):
    """Para Birimi"""
    code = models.CharField(_("Kod"), max_length=3, unique=True)
    name = models.CharField(_("Ad"), max_length=50)
    symbol = models.CharField(_("Sembol"), max_length=5)
    is_default = models.BooleanField(_("Varsayılan"), default=False)
    is_active = models.BooleanField(_("Aktif"), default=True)
    
    class Meta:
        verbose_name = _("Para Birimi")
        verbose_name_plural = _("Para Birimleri")
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Voucher(models.Model):
    """
    Muhasebe Fişi
    
    Muhasebe kayıtlarının ana belgesi. Her fiş, bir veya daha fazla fiş satırı içerir.
    """
    STATE_CHOICES = (
        ('draft', _('Taslak')),
        ('posted', _('Kaydedildi')),
        ('cancelled', _('İptal Edildi')),
    )
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='vouchers',
        verbose_name=_("Şirket")
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, 
        on_delete=models.PROTECT,
        related_name='vouchers',
        verbose_name=_("Mali Yıl")
    )
    type = models.ForeignKey(
        VoucherType, 
        on_delete=models.PROTECT,
        related_name='vouchers',
        verbose_name=_("Fiş Tipi")
    )
    number = models.CharField(_("Fiş Numarası"), max_length=20)
    date = models.DateField(_("Fiş Tarihi"), default=timezone.now)
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    reference = models.CharField(_("Referans"), max_length=100, blank=True, null=True)
    state = models.CharField(_("Durum"), max_length=10, choices=STATE_CHOICES, default='draft')
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)
    created_by = models.ForeignKey(
        "apps.hr_management.User", 
        on_delete=models.SET_NULL, 
        verbose_name=_("Oluşturan"),
        related_name="created_vouchers",
        blank=True, 
        null=True
    )
    updated_by = models.ForeignKey(
        "apps.hr_management.User", 
        on_delete=models.SET_NULL, 
        verbose_name=_("Güncelleyen"),
        related_name="updated_vouchers",
        blank=True, 
        null=True
    )
    
    # Para birimi bilgisi
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='vouchers',
        verbose_name=_("Para Birimi")
    )
    exchange_rate = models.DecimalField(
        _("Kur"), 
        max_digits=18, 
        decimal_places=6, 
        default=Decimal('1.000000'),
        help_text=_("1 birim döviz = ? TL")
    )
    
    class Meta:
        verbose_name = _("Fiş")
        verbose_name_plural = _("Fişler")
        ordering = ['company', 'fiscal_year', '-date', '-number']
        unique_together = [('company', 'fiscal_year', 'type', 'number')]
    
    def __str__(self):
        return f"{self.type.prefix or ''}{self.number} - {self.date}"
    
    @property
    def total_amount(self):
        """Fişin toplam tutarını hesaplar (borç veya alacak toplamı)"""
        debit_total = self.lines.aggregate(Sum('debit_amount'))['debit_amount__sum'] or Decimal('0')
        credit_total = self.lines.aggregate(Sum('credit_amount'))['credit_amount__sum'] or Decimal('0')
        
        return max(debit_total, credit_total)
    
    def is_balanced(self):
        """Fişin dengeli olup olmadığını kontrol eder"""
        debit_total = self.lines.aggregate(Sum('debit_amount'))['debit_amount__sum'] or Decimal('0')
        credit_total = self.lines.aggregate(Sum('credit_amount'))['credit_amount__sum'] or Decimal('0')
        
        return debit_total == credit_total
    
    def post(self):
        """Fişi kaydeder ve ilgili hesaplara işler"""
        if not self.is_balanced():
            raise ValidationError(_("Fiş borç ve alacak toplamları eşit değil."))
        
        self.state = 'posted'
        self.save()
    
    def cancel(self):
        """Fişi iptal eder"""
        if self.state != 'posted':
            raise ValidationError(_("Sadece kaydedilmiş fişler iptal edilebilir."))
        
        self.state = 'cancelled'
        self.save()


class VoucherLine(models.Model):
    """
    Muhasebe Fişi Satırı
    
    Muhasebe fişinin her bir satırını temsil eder.
    Her satır, bir borç ve bir alacak hesabı içerir.
    """
    voucher = models.ForeignKey(
        Voucher, 
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_("Fiş")
    )
    line_no = models.PositiveSmallIntegerField(_("Satır No"))
    account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT,
        related_name='voucher_lines',
        verbose_name=_("Hesap")
    )
    description = models.CharField(_("Açıklama"), max_length=255, blank=True, null=True)
    debit_amount = models.DecimalField(
        _("Borç Tutarı"), 
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    credit_amount = models.DecimalField(
        _("Alacak Tutarı"), 
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Döviz tutarları
    foreign_debit_amount = models.DecimalField(
        _("Döviz Borç"), 
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    foreign_credit_amount = models.DecimalField(
        _("Döviz Alacak"), 
        max_digits=18, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        verbose_name = _("Fiş Satırı")
        verbose_name_plural = _("Fiş Satırları")
        ordering = ['voucher', 'line_no']
        unique_together = [('voucher', 'line_no')]
    
    def __str__(self):
        return f"{self.voucher.number} - {self.line_no} - {self.account.code}"
    
    def clean(self):
        """Validasyon kontrolleri"""
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError(_("Bir satırda hem borç hem alacak olamaz."))
        
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError(_("Borç veya alacak tutarından biri doldurulmalıdır."))
        
    def save(self, *args, **kwargs):
        """Kayıt öncesi validasyon"""
        self.clean()
        super().save(*args, **kwargs)
        
    @property
    def amount(self):
        """Satırın tutarını döndürür (borç veya alacak)"""
        return self.debit_amount or self.credit_amount


# Finansal Raporlama
class FinancialReport(models.Model):
    """
    Mali raporları temsil eden model (Bilanço, Gelir Tablosu vb.)
    """
    
    TYPE_CHOICES = (
        ('balance_sheet', _('Bilanço')),
        ('income_statement', _('Gelir Tablosu')),
        ('cash_flow', _('Nakit Akışı')),
        ('trial_balance', _('Mizan')),
        ('custom', _('Özel Rapor')),
    )
    
    name = models.CharField(_("Rapor Adı"), max_length=100)
    type = models.CharField(_("Rapor Tipi"), max_length=20, choices=TYPE_CHOICES)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='financial_reports',
        verbose_name=_("Şirket")
    )
    start_date = models.DateField(_("Başlangıç Tarihi"))
    end_date = models.DateField(_("Bitiş Tarihi"))
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)
    created_by = models.ForeignKey(
        "apps.hr_management.User", 
        on_delete=models.SET_NULL, 
        verbose_name=_("Oluşturan"),
        related_name="created_financial_reports",
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _("Mali Rapor")
        verbose_name_plural = _("Mali Raporlar")
    
    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')})" 