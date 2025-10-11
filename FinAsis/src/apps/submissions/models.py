from django.db import models
from django.conf import settings


class Declaration(models.Model):
    code = models.CharField(max_length=50)  # e.g., KDV1, BA-BS, Muhtasar
    period = models.CharField(max_length=20)  # e.g., 2025-01
    taxpayer_vkn_tckn = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)  # normalized data to render XML/JSON for GIB
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['code', 'period', 'taxpayer_vkn_tckn'])
        ]


class Submission(models.Model):
    TARGETS = (
        ('gib', 'GIB'),
    )
    declaration = models.ForeignKey(Declaration, on_delete=models.CASCADE, related_name='submissions')
    target = models.CharField(max_length=10, choices=TARGETS, default='gib')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    advisor_required = models.BooleanField(default=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='draft')  # draft|queued|sent|accepted|rejected
    external_id = models.CharField(max_length=100, blank=True)  # integrator tracking id


class SubmissionLog(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, default='info')
    message = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
