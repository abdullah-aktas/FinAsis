# -*- coding: utf-8 -*-
"""
Çek/Senet modülü için veritabanı modelleri.

Bu modül, çek ve senet takibi için temel veritabanı modellerini içerir.
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from apps.core.models import BaseModel, AuditableMixin
from apps.company.models import Company
from apps.finance.accounting.models import Account, Currency, Voucher
from apps.finance.banking.models import BankAccount
from apps.customers.models import Customer, Supplier


class CheckStatus(models.TextChoices):
    """Çek/senet durumu için seçenekler."""
    PORTFOLIO = 'portfolio', _('Portföyde')
    ENDORSED = 'endorsed', _('Ciro Edildi')
    CASHED = 'cashed', _('Tahsil Edildi')
    DEPOSITED = 'deposited', _('Bankaya Verildi')
    DISHONORED = 'dishonored', _('Karşılıksız')
    CANCELLED = 'cancelled', _('İptal Edildi')


class Check(BaseModel, AuditableMixin):
    """
    Çek modeli.
    
    Alınan (müşteriden) ve verilen (tedarikçiye) çekleri temsil eder.
    """
    # Çek türü
    is_incoming = models.BooleanField(_('Alınan Çek'), default=True, help_text=_('Alınan çek için True, verilen çek için False'))
    
    # Temel bilgiler
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='checks',
        verbose_name=_('Şirket')
    )
    check_number = models.CharField(_('Çek Numarası'), max_length=50)
    amount = models.DecimalField(
        _('Tutar'), 
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.PROTECT,
        related_name='checks',
        verbose_name=_('Para Birimi')
    )
    issue_date = models.DateField(_('Düzenleme Tarihi'))
    due_date = models.DateField(_('Vade Tarihi'))
    
    # Banka bilgileri
    bank_name = models.CharField(_('Banka Adı'), max_length=100)
    branch_name = models.CharField(_('Şube Adı'), max_length=100, blank=True, null=True)
    account_number = models.CharField(_('Hesap Numarası'), max_length=50, blank=True, null=True)
    drawer_name = models.CharField(_('Keşideci Adı'), max_length=100)
    
    # İlgili taraflar
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT,
        related_name='customer_checks',
        verbose_name=_('Müşteri'),
        blank=True, 
        null=True,
        help_text=_('Alınan çekler için')
    )
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT,
        related_name='supplier_checks',
        verbose_name=_('Tedarikçi'),
        blank=True, 
        null=True,
        help_text=_('Verilen çekler için')
    )
    
    # Muhasebe bilgileri
    status = models.CharField(
        _('Durum'), 
        max_length=20, 
        choices=CheckStatus.choices,
        default=CheckStatus.PORTFOLIO
    )
    portfolio_entry_date = models.DateField(_('Portföye Giriş Tarihi'))
    accounting_account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT,
        related_name='checks',
        verbose_name=_('Muhasebe Hesabı')
    )
    voucher = models.ForeignKey(
        Voucher, 
        on_delete=models.SET_NULL,
        related_name='checks',
        verbose_name=_('Muhasebe Fişi'),
        blank=True, 
        null=True
    )
    
    # İlave bilgiler
    bank_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.SET_NULL,
        related_name='deposited_checks',
        verbose_name=_('Yatırılan Banka Hesabı'),
        blank=True, 
        null=True,
        help_text=_('Bankaya yatırılan çekler için')
    )
    deposit_date = models.DateField(_('Bankaya Yatırma Tarihi'), blank=True, null=True)
    endorsement_date = models.DateField(_('Ciro Tarihi'), blank=True, null=True)
    endorsement_to = models.CharField(_('Ciro Edilen'), max_length=100, blank=True, null=True)
    collection_date = models.DateField(_('Tahsilat Tarihi'), blank=True, null=True)
    dishonor_date = models.DateField(_('Karşılıksız Tarihi'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Çek')
        verbose_name_plural = _('Çekler')
        ordering = ['due_date', 'check_number']
        unique_together = ['company', 'check_number', 'bank_name']
    
    def __str__(self):
        direction = _('Alınan') if self.is_incoming else _('Verilen')
        return f"{direction} Çek: {self.check_number} - {self.amount} {self.currency.code} ({self.due_date})"
    
    def mark_as_endorsed(self):
        """Çeki ciro edildi olarak işaretler."""
        self.status = CheckStatus.ENDORSED
        self.save(update_fields=['status'])
    
    def mark_as_cashed(self):
        """Çeki tahsil edildi olarak işaretler."""
        self.status = CheckStatus.CASHED
        self.collection_date = models.functions.Now()
        self.save(update_fields=['status', 'collection_date'])
    
    def mark_as_deposited(self):
        """Çeki bankaya verildi olarak işaretler."""
        self.status = CheckStatus.DEPOSITED
        self.deposit_date = models.functions.Now()
        self.save(update_fields=['status', 'deposit_date'])
    
    def mark_as_dishonored(self):
        """Çeki karşılıksız olarak işaretler."""
        self.status = CheckStatus.DISHONORED
        self.dishonor_date = models.functions.Now()
        self.save(update_fields=['status', 'dishonor_date'])


class Bill(BaseModel, AuditableMixin):
    """
    Senet modeli.
    
    Alınan (müşteriden) ve verilen (tedarikçiye) senetleri temsil eder.
    """
    # Senet türü
    is_incoming = models.BooleanField(_('Alınan Senet'), default=True, help_text=_('Alınan senet için True, verilen senet için False'))
    
    # Temel bilgiler
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='bills',
        verbose_name=_('Şirket')
    )
    bill_number = models.CharField(_('Senet Numarası'), max_length=50)
    amount = models.DecimalField(
        _('Tutar'), 
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.PROTECT,
        related_name='bills',
        verbose_name=_('Para Birimi')
    )
    issue_date = models.DateField(_('Düzenleme Tarihi'))
    due_date = models.DateField(_('Vade Tarihi'))
    
    # İlgili taraflar
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT,
        related_name='customer_bills',
        verbose_name=_('Müşteri'),
        blank=True, 
        null=True,
        help_text=_('Alınan senetler için')
    )
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT,
        related_name='supplier_bills',
        verbose_name=_('Tedarikçi'),
        blank=True, 
        null=True,
        help_text=_('Verilen senetler için')
    )
    drawer_name = models.CharField(_('Keşideci Adı'), max_length=100)
    
    # Muhasebe bilgileri
    status = models.CharField(
        _('Durum'), 
        max_length=20, 
        choices=CheckStatus.choices,  # Aynı durum seçeneklerini kullanıyoruz
        default=CheckStatus.PORTFOLIO
    )
    portfolio_entry_date = models.DateField(_('Portföye Giriş Tarihi'))
    accounting_account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT,
        related_name='bills',
        verbose_name=_('Muhasebe Hesabı')
    )
    voucher = models.ForeignKey(
        Voucher, 
        on_delete=models.SET_NULL,
        related_name='bills',
        verbose_name=_('Muhasebe Fişi'),
        blank=True, 
        null=True
    )
    
    # İlave bilgiler
    endorsement_date = models.DateField(_('Ciro Tarihi'), blank=True, null=True)
    endorsement_to = models.CharField(_('Ciro Edilen'), max_length=100, blank=True, null=True)
    collection_date = models.DateField(_('Tahsilat Tarihi'), blank=True, null=True)
    dishonor_date = models.DateField(_('Protesto Tarihi'), blank=True, null=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Senet')
        verbose_name_plural = _('Senetler')
        ordering = ['due_date', 'bill_number']
        unique_together = ['company', 'bill_number']
    
    def __str__(self):
        direction = _('Alınan') if self.is_incoming else _('Verilen')
        return f"{direction} Senet: {self.bill_number} - {self.amount} {self.currency.code} ({self.due_date})"
    
    def mark_as_endorsed(self):
        """Seneti ciro edildi olarak işaretler."""
        self.status = CheckStatus.ENDORSED
        self.save(update_fields=['status'])
    
    def mark_as_cashed(self):
        """Seneti tahsil edildi olarak işaretler."""
        self.status = CheckStatus.CASHED
        self.collection_date = models.functions.Now()
        self.save(update_fields=['status', 'collection_date'])
    
    def mark_as_dishonored(self):
        """Seneti protesto edildi olarak işaretler."""
        self.status = CheckStatus.DISHONORED
        self.dishonor_date = models.functions.Now()
        self.save(update_fields=['status', 'dishonor_date']) 