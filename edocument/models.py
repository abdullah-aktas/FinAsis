from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid

class EDocumentBase(models.Model):
    """E-dokümanlar için temel model"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_documents'
    )
    receiver_vkn = models.CharField(max_length=11)
    receiver_name = models.CharField(max_length=255)
    xml_content = models.TextField()
    signed_xml = models.TextField(null=True, blank=True)
    signature_status = models.BooleanField(default=False)
    gib_response = models.JSONField(null=True, blank=True)
    gib_error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.sent_at and self.sent_at < self.created_at:
            raise ValidationError(_('Gönderim tarihi oluşturma tarihinden önce olamaz'))

class EDocument(EDocumentBase):
    DOCUMENT_TYPES = (
        ('SATIS', _('Satış Faturası')),
        ('IADE', _('İade Faturası')),
        ('TEVKIFATLI', _('Tevkifatlı Fatura')),
        ('OZELMATRAH', _('Özel Matrah Faturası')),
        ('IHRACAT', _('İhracat Faturası')),
        ('HIZMET', _('Hizmet Faturası')),
    )
    
    STATUS_CHOICES = (
        ('DRAFT', _('Taslak')),
        ('PENDING', _('Beklemede')),
        ('SENT', _('Gönderildi')),
        ('FAILED', _('Başarısız')),
        ('CANCELLED', _('İptal Edildi')),
        ('ARCHIVED', _('Arşivlendi')),
    )

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='TRY')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_tax = models.DecimalField(max_digits=15, decimal_places=2)
    total_discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archive_date = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('E-Belge')
        verbose_name_plural = _('E-Belgeler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['document_type']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        super().clean()
        if self.due_date and self.due_date < self.invoice_date:
            raise ValidationError(_('Vade tarihi fatura tarihinden önce olamaz'))

class EDocumentItem(models.Model):
    document = models.ForeignKey(EDocument, on_delete=models.CASCADE, related_name='items')
    line_number = models.PositiveIntegerField()
    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('E-Belge Kalemi')
        verbose_name_plural = _('E-Belge Kalemleri')
        ordering = ['line_number']
        unique_together = ['document', 'line_number']

class EDocumentLog(models.Model):
    LOG_LEVELS = (
        ('INFO', _('Bilgi')),
        ('WARNING', _('Uyarı')),
        ('ERROR', _('Hata')),
        ('DEBUG', _('Debug')),
    )

    document = models.ForeignKey(EDocument, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO')
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('E-Belge Log')
        verbose_name_plural = _('E-Belge Logları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['status']),
            models.Index(fields=['level']),
            models.Index(fields=['created_at']),
        ]

class EDespatchAdvice(EDocumentBase):
    STATUS_CHOICES = (
        ('DRAFT', _('Taslak')),
        ('PENDING', _('Beklemede')),
        ('SENT', _('Gönderildi')),
        ('FAILED', _('Başarısız')),
        ('CANCELLED', _('İptal Edildi')),
        ('ACCEPTED', _('Kabul Edildi')),
        ('REJECTED', _('Reddedildi')),
        ('PARTIALLY_ACCEPTED', _('Kısmen Kabul Edildi')),
    )

    TRANSPORT_TYPES = (
        ('COMPANY_VEHICLE', _('Firma Aracı')),
        ('COURIER', _('Kargo')),
        ('TRANSPORTER', _('Nakliyeci')),
        ('CUSTOMER', _('Müşteri')),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    despatch_number = models.CharField(max_length=50, unique=True)
    despatch_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPES)
    vehicle_plate = models.CharField(max_length=20, null=True, blank=True)
    driver_name = models.CharField(max_length=100, null=True, blank=True)
    driver_tckn = models.CharField(max_length=11, null=True, blank=True)
    driver_phone = models.CharField(max_length=20, null=True, blank=True)
    transport_company = models.CharField(max_length=255, null=True, blank=True)
    transport_company_vkn = models.CharField(max_length=11, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archive_date = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('E-İrsaliye')
        verbose_name_plural = _('E-İrsaliyeler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['despatch_number']),
            models.Index(fields=['status']),
            models.Index(fields=['transport_type']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        super().clean()
        if self.delivery_date < self.despatch_date:
            raise ValidationError(_('Teslimat tarihi irsaliye tarihinden önce olamaz'))

class EDespatchAdviceItem(models.Model):
    despatch = models.ForeignKey(EDespatchAdvice, on_delete=models.CASCADE, related_name='items')
    line_number = models.PositiveIntegerField()
    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20)
    accepted_quantity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    rejected_quantity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('E-İrsaliye Kalemi')
        verbose_name_plural = _('E-İrsaliye Kalemleri')
        ordering = ['line_number']
        unique_together = ['despatch', 'line_number']

class EDespatchAdviceLog(models.Model):
    LOG_LEVELS = (
        ('INFO', _('Bilgi')),
        ('WARNING', _('Uyarı')),
        ('ERROR', _('Hata')),
        ('DEBUG', _('Debug')),
    )

    despatch = models.ForeignKey(EDespatchAdvice, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO')
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('E-İrsaliye Log')
        verbose_name_plural = _('E-İrsaliye Logları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['status']),
            models.Index(fields=['level']),
            models.Index(fields=['created_at']),
        ]
