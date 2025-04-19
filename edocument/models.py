from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class EDocument(models.Model):
    DOCUMENT_TYPES = (
        ('SATIS', _('Satış Faturası')),
        ('IADE', _('İade Faturası')),
        ('TEVKIFATLI', _('Tevkifatlı Fatura')),
    )
    
    STATUS_CHOICES = (
        ('DRAFT', _('Taslak')),
        ('PENDING', _('Beklemede')),
        ('SENT', _('Gönderildi')),
        ('FAILED', _('Başarısız')),
        ('CANCELLED', _('İptal Edildi')),
    )

    uuid = models.UUIDField(unique=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Fatura bilgileri
    invoice_number = models.CharField(max_length=50)
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    
    # Şirket bilgileri
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_documents'
    )
    receiver_vkn = models.CharField(max_length=11)
    receiver_name = models.CharField(max_length=255)
    
    # XML ve imza bilgileri
    xml_content = models.TextField()
    signed_xml = models.TextField(null=True, blank=True)
    signature_status = models.BooleanField(default=False)
    
    # GİB yanıt bilgileri
    gib_response = models.JSONField(null=True, blank=True)
    gib_error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('E-Belge')
        verbose_name_plural = _('E-Belgeler')
        ordering = ['-created_at']

class EDocumentLog(models.Model):
    document = models.ForeignKey(
        EDocument,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('E-Belge Log')
        verbose_name_plural = _('E-Belge Logları')
        ordering = ['-created_at']

class EDespatchAdvice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', _('Taslak')),
        ('PENDING', _('Beklemede')),
        ('SENT', _('Gönderildi')),
        ('FAILED', _('Başarısız')),
        ('CANCELLED', _('İptal Edildi')),
        ('ACCEPTED', _('Kabul Edildi')),
        ('REJECTED', _('Reddedildi')),
    )

    uuid = models.UUIDField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # İrsaliye bilgileri
    despatch_number = models.CharField(max_length=50)
    despatch_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    
    # Şirket bilgileri
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_despatches'
    )
    receiver_vkn = models.CharField(max_length=11)
    receiver_name = models.CharField(max_length=255)
    
    # Taşıma bilgileri
    transport_type = models.CharField(max_length=50)  # firma aracı, kargo, nakliyeci
    vehicle_plate = models.CharField(max_length=20, null=True, blank=True)
    driver_name = models.CharField(max_length=100, null=True, blank=True)
    
    # XML ve imza bilgileri
    xml_content = models.TextField()
    signed_xml = models.TextField(null=True, blank=True)
    signature_status = models.BooleanField(default=False)
    
    # GİB yanıt bilgileri
    gib_response = models.JSONField(null=True, blank=True)
    gib_error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('E-İrsaliye')
        verbose_name_plural = _('E-İrsaliyeler')
        ordering = ['-created_at']

class EDespatchAdviceLog(models.Model):
    despatch = models.ForeignKey(
        EDespatchAdvice,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('E-İrsaliye Log')
        verbose_name_plural = _('E-İrsaliye Logları')
        ordering = ['-created_at']
