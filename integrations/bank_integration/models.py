# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Bank(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    api_key = models.CharField(max_length=100, blank=True, null=True)
    api_secret = models.CharField(max_length=100, blank=True, null=True)
    base_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class IntegratedBankAccount(models.Model):
    ACCOUNT_TYPES = (
        ('CHECKING', 'Vadesiz Hesap'),
        ('SAVINGS', 'Vadeli Hesap'),
        ('CREDIT', 'Kredi Hesabı'),
        ('INVESTMENT', 'Yatırım Hesabı'),
    )

    CURRENCY_CHOICES = (
        ('TRY', 'Türk Lirası'),
        ('USD', 'Amerikan Doları'),
        ('EUR', 'Euro'),
        ('GBP', 'İngiliz Sterlini'),
    )

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=50)
    iban = models.CharField(max_length=50, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TRY')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank.name} - {self.account_number} ({self.currency})"

class BankTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Para Yatırma'),
        ('WITHDRAWAL', 'Para Çekme'),
        ('TRANSFER', 'Transfer'),
        ('PAYMENT', 'Ödeme'),
        ('INTEREST', 'Faiz'),
        ('OTHER', 'Diğer'),
    )

    account = models.ForeignKey(IntegratedBankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateTimeField()
    value_date = models.DateField()
    description = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    is_reconciled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account.account_number} - {self.transaction_type} - {self.amount} {self.account.currency}"

class BankTransfer(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Beklemede'),
        ('COMPLETED', 'Tamamlandı'),
        ('FAILED', 'Başarısız'),
        ('CANCELLED', 'İptal Edildi'),
    )

    from_account = models.ForeignKey(IntegratedBankAccount, on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_account = models.ForeignKey(IntegratedBankAccount, on_delete=models.CASCADE, related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=200)
    transfer_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_account.account_number} -> {self.to_account.account_number} - {self.amount} {self.from_account.currency}"

class BankReconciliation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Beklemede'),
        ('COMPLETED', 'Tamamlandı'),
        ('FAILED', 'Başarısız'),
    )

    account = models.ForeignKey(IntegratedBankAccount, on_delete=models.CASCADE, related_name='reconciliations')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_transactions = models.IntegerField(default=0)
    matched_transactions = models.IntegerField(default=0)
    unmatched_transactions = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account.account_number} - {self.start_date} to {self.end_date}"
