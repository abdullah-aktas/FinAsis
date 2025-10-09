from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class AuditLog(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    content_object = GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['content_type','object_id','created_at']),
            models.Index(fields=['action','created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    def __str__(self):
        return f"{self.action} @ {self.created_at}"
    @classmethod
    def log_action(cls, obj, action, user=None, ip=None, payload=None):
        return cls.objects.create(
            content_type=ContentType.objects.get_for_model(obj.__class__),
            object_id=str(getattr(obj, 'pk', getattr(obj, 'id', ''))),
            action=action, user=user, ip_address=ip, payload=payload or {},
        )

class ApprovalRequest(models.Model):
    STATUS = (('PENDING','Beklemede'),('APPROVED','Onaylandı'),('REJECTED','Reddedildi'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='common_approval_requests')
    object_id = models.CharField(max_length=64)
    content_object = GenericForeignKey('content_type', 'object_id')
    status = models.CharField(max_length=16, choices=STATUS, default='PENDING')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='approvals_requested', on_delete=models.CASCADE)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='approvals_decided', on_delete=models.SET_NULL)
    decided_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['content_type','object_id','status']),
            models.Index(fields=['created_at'])
        ]
        ordering = ['-created_at']
    def approve(self, user, comment=''):
        self.status='APPROVED'; self.decided_by=user; self.decided_at=timezone.now(); self.comment = comment or self.comment
        self.save(update_fields=['status','decided_by','decided_at','comment'])
    def reject(self, user, comment=''):
        self.status='REJECTED'; self.decided_by=user; self.decided_at=timezone.now(); self.comment = comment or self.comment
        self.save(update_fields=['status','decided_by','decided_at','comment'])
