from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class AuditEvent(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    tenant = models.ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    data = models.JSONField(default=dict, blank=True)
    diff = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action}:{self.content_type_id}:{self.object_id}"
