from django.db import models
from django.conf import settings

class EInvoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('PENDING', 'Beklemede'),
        ('SENT', 'Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sent_invoices')
    receiver_vkn = models.CharField(max_length=11)
    receiver_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    pdf_file = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)
    xml_file = models.FileField(upload_to='invoices/xml/', null=True, blank=True)

    class Meta:
        verbose_name = 'E-Fatura'
        verbose_name_plural = 'E-Faturalar'

class EArchive(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('ARCHIVED', 'Arşivlendi'),
        ('ERROR', 'Hata'),
    ]

    archive_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    document_type = models.CharField(max_length=50)
    document_date = models.DateField()
    document_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    file = models.FileField(upload_to='archive/')
    ocr_content = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'E-Arşiv'
        verbose_name_plural = 'E-Arşiv'

class BankIntegration(models.Model):
    BANK_CHOICES = [
        ('GARANTI', 'Garanti BBVA'),
        ('ISBANK', 'İş Bankası'),
        ('AKBANK', 'Akbank'),
        ('YAPIKREDI', 'Yapı Kredi'),
        ('ZIRAAT', 'Ziraat Bankası'),
    ]

    bank = models.CharField(max_length=20, choices=BANK_CHOICES)
    account_holder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=50)
    iban = models.CharField(max_length=50)
    api_key = models.CharField(max_length=200)
    api_secret = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Banka Entegrasyonu'
        verbose_name_plural = 'Banka Entegrasyonları'
        unique_together = ['bank', 'account_number'] 