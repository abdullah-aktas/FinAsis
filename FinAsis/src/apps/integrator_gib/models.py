from django.db import models


class IntegratorConfig(models.Model):
    name = models.CharField(max_length=100, default='Default Integrator')
    base_url = models.URLField()
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)
    certificate_alias = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)


class AccessToken(models.Model):
    integrator = models.ForeignKey(IntegratorConfig, on_delete=models.CASCADE, related_name='tokens')
    token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
