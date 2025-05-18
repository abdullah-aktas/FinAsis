# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Bank(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    branch_code = models.CharField(max_length=20, blank=True, null=True)
    branch_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Check(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Beklemede'),
        ('DEPOSITED', 'Tahsil Edildi'),
        ('BOUNCED', 'Karşılıksız'),
        ('CANCELLED', 'İptal Edildi'),
    )

    TYPE_CHOICES = (
        ('RECEIVABLE', 'Alacak'),
        ('PAYABLE', 'Borç'),
    )

    check_number = models.CharField(max_length=50)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    check_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    drawer_name = models.CharField(max_length=200)
    drawer_tax_number = models.CharField(max_length=20, blank=True, null=True)
    payee_name = models.CharField(max_length=200)
    payee_tax_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.check_number} - {self.amount} TL"

class PromissoryNote(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Beklemede'),
        ('PAID', 'Ödendi'),
        ('PROTESTED', 'Protestolu'),
        ('CANCELLED', 'İptal Edildi'),
    )

    TYPE_CHOICES = (
        ('RECEIVABLE', 'Alacak'),
        ('PAYABLE', 'Borç'),
    )

    note_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    note_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    drawer_name = models.CharField(max_length=200)
    drawer_tax_number = models.CharField(max_length=20, blank=True, null=True)
    payee_name = models.CharField(max_length=200)
    payee_tax_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.note_number} - {self.amount} TL"

class CheckTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Tahsilat'),
        ('PAYMENT', 'Ödeme'),
        ('BOUNCE', 'Karşılıksız'),
        ('CANCEL', 'İptal'),
    )

    check = models.ForeignKey(Check, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.check.check_number} - {self.transaction_type}"

class PromissoryNoteTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('PAYMENT', 'Ödeme'),
        ('PROTEST', 'Protesto'),
        ('CANCEL', 'İptal'),
    )

    promissory_note = models.ForeignKey(PromissoryNote, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.promissory_note.note_number} - {self.transaction_type}"
