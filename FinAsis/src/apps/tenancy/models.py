from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tenant(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class Company(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.tenant.code})"

class UserTenantRole(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('viewer', 'Viewer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_roles')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_roles')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tenant', 'role')

    def __str__(self):
        return f"{self.user_id}:{self.tenant_id}:{self.role}"
