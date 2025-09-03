from django.db import models
from django.utils import timezone

class ChainRecord(models.Model):
    reference = models.CharField(max_length=255)
    hash_hex = models.CharField(max_length=64, db_index=True)
    payload_preview = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.hash_hex[:8]}"
