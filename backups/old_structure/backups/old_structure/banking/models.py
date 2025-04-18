from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Check(models.Model):
    STATUS_CHOICES = (
        ('RECEIVED', 'Alındı'),
        ('ISSUED', 'Verildi'),
        ('CASHED', 'Tahsil Edildi'),
        ('BOUNCED', 'Karşılıksız'),
        ('CANCELLED', 'İptal Edildi'),
    )

    check_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    drawer_name = models.CharField(max_length=200)
    drawer_tax_number = models.CharField(max_length=20, blank=True, null=True)
    payee_name = models.CharField(max_length=200)
    payee_tax_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Çek #{self.check_number} - {self.amount} TL"

class PromissoryNote(models.Model):
    STATUS_CHOICES = (
        ('RECEIVED', 'Alındı'),
        ('ISSUED', 'Verildi'),
        ('PAID', 'Ödendi'),
        ('PROTESTED', 'Protestolu'),
        ('CANCELLED', 'İptal Edildi'),
    )

    note_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    drawer_name = models.CharField(max_length=200)
    drawer_tax_number = models.CharField(max_length=20, blank=True, null=True)
    payee_name = models.CharField(max_length=200)
    payee_tax_number = models.CharField(max_length=20, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Senet #{self.note_number} - {self.amount} TL"

class CheckMovement(models.Model):
    MOVEMENT_TYPES = (
        ('RECEIVE', 'Alındı'),
        ('ISSUE', 'Verildi'),
        ('CASH', 'Tahsil Edildi'),
        ('BOUNCE', 'Karşılıksız'),
        ('CANCEL', 'İptal Edildi'),
    )

    check = models.ForeignKey(Check, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    movement_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.check.check_number} - {self.movement_type} ({self.movement_date})"

class PromissoryNoteMovement(models.Model):
    MOVEMENT_TYPES = (
        ('RECEIVE', 'Alındı'),
        ('ISSUE', 'Verildi'),
        ('PAY', 'Ödendi'),
        ('PROTEST', 'Protesto'),
        ('CANCEL', 'İptal Edildi'),
    )

    promissory_note = models.ForeignKey(PromissoryNote, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    movement_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.promissory_note.note_number} - {self.movement_type} ({self.movement_date})" 