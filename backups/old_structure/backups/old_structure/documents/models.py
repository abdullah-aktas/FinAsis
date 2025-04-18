from django.db import models
from django.conf import settings
from apps.virtual_company.models import VirtualCompany

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    virtual_company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class Document(BaseModel):
    """
    Belge
    """
    DOCUMENT_TYPES = [
        ('invoice', 'Fatura'),
        ('receipt', 'Fiş'),
        ('contract', 'Sözleşme'),
        ('report', 'Rapor'),
        ('other', 'Diğer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    ]
    
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extracted_data = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_document_type_display()}"
    
    class Meta:
        verbose_name = 'Belge'
        verbose_name_plural = 'Belgeler'
        ordering = ['-created_at']

class DocumentProcessingLog(BaseModel):
    """
    Belge İşleme Logu
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    message = models.TextField()
    error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.document.title} - {self.status} - {self.created_at}"
    
    class Meta:
        verbose_name = 'Belge İşleme Logu'
        verbose_name_plural = 'Belge İşleme Logları'
        ordering = ['-created_at']
