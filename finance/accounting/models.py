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
# from crm.models.customer import Customer  # Doğru import yolu
# from .models import Customer  # Aynı dosyada tanımlıysa


# External model imports (doğru app yolları ile)
from finance.bank_integration.models import IntegratedBankAccount as FinanceBankAccount
from apps.company.models import Company, FiscalYear


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name


class AccountType(models.Model):
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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='accounts', verbose_name=_("Şirket"))
    code = models.CharField(_("Hesap Kodu"), max_length=20)
    name = models.CharField(_("Hesap Adı"), max_length=150)
    type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts', verbose_name=_("Hesap Tipi"))
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    is_tax_account = models.BooleanField(_("Vergi Hesabı"), default=False)
    is_bank_account = models.BooleanField(_("Banka Hesabı"), default=False)
    is_cash_account = models.BooleanField(_("Kasa Hesabı"), default=False)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00')
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
        return f"{self.code} - {self.name}"

    @property
    def is_leaf(self):
        # children related_name ile tanımlı olduğu için exists() direkt kullanılabilir
        return not Account.objects.filter(parent=self).exists()

    @property
    def level(self):
        level = 1
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def get_balance(self, start_date=None, end_date=None):
        from finance.accounting.models import VoucherLine
        query = VoucherLine.objects.filter(account=self)
        if start_date:
            query = query.filter(voucher__date__gte=start_date)
        if end_date:
            query = query.filter(voucher__date__lte=end_date)
        totals = query.aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount')
        )
        return (totals['total_debit'] or Decimal('0')) - (totals['total_credit'] or Decimal('0'))


class VoucherType(models.Model):
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
    STATE_CHOICES = (
        ('draft', _('Taslak')),
        ('posted', _('Kaydedildi')),
        ('cancelled', _('İptal Edildi')),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vouchers', verbose_name=_("Şirket"))
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='vouchers', verbose_name=_("Mali Yıl"))
    type = models.ForeignKey(VoucherType, on_delete=models.PROTECT, related_name='vouchers', verbose_name=_("Fiş Tipi"))
    number = models.CharField(_("Fiş Numarası"), max_length=20)
    date = models.DateField(_("Fiş Tarihi"), default=timezone.now)
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    reference = models.CharField(_("Referans"), max_length=100, blank=True, null=True)
    state = models.CharField(_("Durum"), max_length=10, choices=STATE_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True, related_name='vouchers')
    exchange_rate = models.DecimalField(_("Kur"), max_digits=18, decimal_places=6, default=Decimal('1.000000'))

    class Meta:
        verbose_name = _("Fiş")
        verbose_name_plural = _("Fişler")
        ordering = ['company', 'fiscal_year', '-date', '-number']
        unique_together = [('company', 'fiscal_year', 'type', 'number')]

    def __str__(self):
        return f"{self.type.prefix or ''}{self.number} - {self.date}"

    @property
    def total_amount(self):
        totals = VoucherLine.objects.filter(voucher=self).aggregate(
            debit_sum=Sum('debit_amount'),
            credit_sum=Sum('credit_amount')
        )
        debit_total = totals['debit_sum'] or Decimal('0')
        credit_total = totals['credit_sum'] or Decimal('0')
        return max(debit_total, credit_total)

    def is_balanced(self):
        totals = VoucherLine.objects.filter(voucher=self).aggregate(
            debit_sum=Sum('debit_amount'),
            credit_sum=Sum('credit_amount')
        )
        return (totals['debit_sum'] or Decimal('0')) == (totals['credit_sum'] or Decimal('0'))

    def post(self):
        if not self.is_balanced():
            raise ValidationError(_("Fiş borç ve alacak toplamları eşit değil."))
        self.state = 'posted'
        self.save()

    def cancel(self):
        if self.state != 'posted':
            raise ValidationError(_("Sadece kaydedilmiş fişler iptal edilebilir."))
        self.state = 'cancelled'
        self.save()


class VoucherLine(models.Model):
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='lines', verbose_name=_("Fiş"))
    line_no = models.PositiveSmallIntegerField(_("Satır No"))
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='voucher_lines', verbose_name=_("Hesap"))
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
    foreign_debit_amount = models.DecimalField(_("Döviz Borç"), max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    foreign_credit_amount = models.DecimalField(_("Döviz Alacak"), max_digits=18, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        verbose_name = _("Fiş Satırı")
        verbose_name_plural = _("Fiş Satırları")
        ordering = ['voucher', 'line_no']
        unique_together = [('voucher', 'line_no')]

    def __str__(self):
        return f"{self.voucher.number} - {self.line_no} - {self.account.code}"

    def clean(self):
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError(_("Bir satırda hem borç hem alacak olamaz."))
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError(_("Borç veya alacak tutarından biri doldurulmalıdır."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def amount(self):
        return self.debit_amount or self.credit_amount


class FinancialReport(models.Model):
    TYPE_CHOICES = (
        ('balance_sheet', _('Bilanço')),
        ('income_statement', _('Gelir Tablosu')),
        ('cash_flow', _('Nakit Akışı')),
        ('trial_balance', _('Mizan')),
        ('custom', _('Özel Rapor')),
    )
    name = models.CharField(_("Rapor Adı"), max_length=100)
    type = models.CharField(_("Rapor Tipi"), max_length=20, choices=TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='financial_reports', verbose_name=_("Şirket"))
    start_date = models.DateField(_("Başlangıç Tarihi"))
    end_date = models.DateField(_("Bitiş Tarihi"))
    description = models.TextField(_("Açıklama"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Mali Rapor")
        verbose_name_plural = _("Mali Raporlar")

    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')})"


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name=_('Müşteri'))
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('Fatura Numarası'))
    issue_date = models.DateField(verbose_name=_('Düzenleme Tarihi'))
    due_date = models.DateField(verbose_name=_('Vade Tarihi'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Toplam Tutar'))
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', _('Taslak')),
        ('APPROVED', _('Onaylandı')),
        ('PAID', _('Ödendi')),
        ('CANCELED', _('İptal Edildi'))
    ], default='DRAFT', verbose_name=_('Durum'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))

    class Meta:
        verbose_name = _('Fatura')
        verbose_name_plural = _('Faturalar')
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"
