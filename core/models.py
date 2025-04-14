from django.db import models
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    """
    Tüm modeller için temel zaman damgası alanları
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """
    Yumuşak silme özelliği olan modeller için temel sınıf
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_deleted')

    class Meta:
        abstract = True

class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Tüm modeller için temel sınıf
    """
    class Meta:
        abstract = True

class AuditLog(models.Model):
    """
    Sistem genelinde yapılan değişikliklerin kaydı
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField()
    ip_address = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model}" 