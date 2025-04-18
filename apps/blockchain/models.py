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

class BlockchainTransaction(BaseModel):
    """
    Blockchain İşlemi
    """
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    ]
    
    TRANSACTION_TYPES = [
        ('invoice', 'Fatura'),
        ('payment', 'Ödeme'),
        ('account', 'Cari Hesap'),
        ('other', 'Diğer'),
    ]
    
    title = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    reference_model = models.CharField(max_length=100, blank=True, null=True)
    data_hash = models.CharField(max_length=64, blank=True, null=True)
    blockchain_hash = models.CharField(max_length=66, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_transaction_type_display()}"
    
    class Meta:
        verbose_name = 'Blockchain İşlemi'
        verbose_name_plural = 'Blockchain İşlemleri'
        ordering = ['-created_at']

class BlockchainLog(BaseModel):
    """
    Blockchain Log
    """
    transaction = models.ForeignKey(BlockchainTransaction, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    message = models.TextField()
    error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction.title} - {self.status} - {self.created_at}"
    
    class Meta:
        verbose_name = 'Blockchain Log'
        verbose_name_plural = 'Blockchain Logları'
        ordering = ['-created_at']
