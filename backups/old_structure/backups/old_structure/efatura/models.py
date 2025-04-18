from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Company(models.Model):
    name = models.CharField(max_length=200)
    tax_number = models.CharField(max_length=20, unique=True)
    tax_office = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.tax_number})"

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Taslak'),
        ('SENT', 'Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELLED', 'İptal Edildi'),
    )

    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    sender = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sent_invoices')
    receiver = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_invoices')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fatura #{self.invoice_number} - {self.sender.name} -> {self.receiver.name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

class EInvoice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Taslak'),
        ('SENT', 'Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELLED', 'İptal Edildi'),
    )

    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='e_invoice')
    uuid = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    response_code = models.CharField(max_length=50, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"E-Fatura #{self.invoice.invoice_number} - {self.status}"

class EArchive(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Taslak'),
        ('SENT', 'Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELLED', 'İptal Edildi'),
    )

    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='e_archive')
    uuid = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    response_code = models.CharField(max_length=50, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"E-Arşiv #{self.invoice.invoice_number} - {self.status}"

class EWaybill(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Taslak'),
        ('SENT', 'Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELLED', 'İptal Edildi'),
    )

    waybill_number = models.CharField(max_length=50, unique=True)
    waybill_date = models.DateField()
    sender = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sent_waybills')
    receiver = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_waybills')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    uuid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    response_code = models.CharField(max_length=50, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"E-İrsaliye #{self.waybill_number} - {self.sender.name} -> {self.receiver.name}"
