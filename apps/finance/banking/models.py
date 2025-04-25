# -*- coding: utf-8 -*-
"""
Bankacılık modülü için veritabanı modelleri.

Bu modül, bankacılık işlemleri için temel veritabanı modellerini içerir.
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from core.models import BaseModel, AuditableMixin
from apps.company.models import Company
from finance.accounting.models import Account, Currency, Voucher


class Bank(BaseModel):
    """Banka bilgilerini içeren model."""
    
    code = models.CharField(_("Banka Kodu"), max_length=10)
    name = models.CharField(_("Banka Adı"), max_length=100)
    swift_code = models.CharField(_("SWIFT Kodu"), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_("Aktif"), default=True)
    logo = models.ImageField(_("Logo"), upload_to="banks/", blank=True, null=True)
    
    class Meta:
        verbose_name = _("Banka")
        verbose_name_plural = _("Bankalar")
        ordering = ["name"]
    
    def __str__(self):
        return self.name


class BankAccount(BaseModel, AuditableMixin):
    """Banka hesap bilgilerini içeren model."""
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name=_("Şirket")
    )
    bank = models.ForeignKey(
        Bank, 
        on_delete=models.PROTECT,
        related_name="accounts",
        verbose_name=_("Banka")
    )
    account_number = models.CharField(_("Hesap Numarası"), max_length=50)
    iban = models.CharField(_("IBAN"), max_length=50)
    branch_code = models.CharField(_("Şube Kodu"), max_length=20, blank=True, null=True)
    branch_name = models.CharField(_("Şube Adı"), max_length=100, blank=True, null=True)
    currency = models.ForeignKey(
        Currency, 
        on_delete=models.PROTECT,
        related_name="bank_accounts",
        verbose_name=_("Para Birimi")
    )
    accounting_account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT,
        related_name="bank_accounts",
        verbose_name=_("Muhasebe Hesabı")
    )
    is_active = models.BooleanField(_("Aktif"), default=True)
    
    class Meta:
        verbose_name = _("Banka Hesabı")
        verbose_name_plural = _("Banka Hesapları")
        ordering = ["company", "bank", "currency"]
        unique_together = [("company", "iban")]
    
    def __str__(self):
        return f"{self.bank.name} - {self.iban[-4:]}"
    
    @property
    def current_balance(self):
        """Hesabın güncel bakiyesini hesaplar."""
        incoming = sum(t.amount for t in self.incoming_transactions.filter(is_reconciled=True))
        outgoing = sum(t.amount for t in self.outgoing_transactions.filter(is_reconciled=True))
        return incoming - outgoing


class BankTransaction(BaseModel, AuditableMixin):
    """Banka işlemlerini içeren model."""
    
    TRANSACTION_TYPES = (
        ("deposit", _("Yatırma")),
        ("withdrawal", _("Çekme")),
        ("transfer", _("Havale/EFT")),
        ("payment", _("Ödeme")),
        ("interest", _("Faiz")),
        ("fee", _("Komisyon/Masraf")),
        ("other", _("Diğer")),
    )
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name="bank_transactions",
        verbose_name=_("Şirket")
    )
    transaction_date = models.DateField(_("İşlem Tarihi"))
    reference_number = models.CharField(_("Referans No"), max_length=50, blank=True, null=True)
    description = models.CharField(_("Açıklama"), max_length=255)
    transaction_type = models.CharField(_("İşlem Tipi"), max_length=20, choices=TRANSACTION_TYPES)
    
    source_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.PROTECT,
        related_name="outgoing_transactions",
        verbose_name=_("Kaynak Hesap"),
        blank=True, 
        null=True
    )
    destination_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.PROTECT,
        related_name="incoming_transactions",
        verbose_name=_("Hedef Hesap"),
        blank=True, 
        null=True
    )
    
    amount = models.DecimalField(
        _("Tutar"), 
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    
    is_reconciled = models.BooleanField(_("Mutabakatlı"), default=False)
    voucher = models.ForeignKey(
        Voucher, 
        on_delete=models.SET_NULL,
        related_name="bank_transactions",
        verbose_name=_("Muhasebe Fişi"),
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _("Banka İşlemi")
        verbose_name_plural = _("Banka İşlemleri")
        ordering = ["-transaction_date", "-created_at"]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.transaction_date} - {self.amount}"
    
    def reconcile(self):
        """İşlemi mutabakata alır."""
        self.is_reconciled = True
        self.save(update_fields=["is_reconciled"])
    
    def create_voucher(self):
        """İşlem için muhasebe fişi oluşturur."""
        # Burada muhasebe fişi oluşturma mantığı yer alacak
        pass 