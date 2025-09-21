from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Group

class Plan(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    PERIOD_CHOICES = [
        ('month', 'Aylık'),
        ('year', 'Yıllık'),
    ]
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='prices')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='month')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('plan', 'period', 'currency')

    def __str__(self):
        return f"{self.plan.name} {self.period} {self.amount} {self.currency}"

class Module(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PlanModule(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_modules')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plan', 'module')

class PlanGroup(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_groups')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plan', 'group')

class SubscriptionStatus(models.TextChoices):
    TRIAL = 'trial', 'Trial'
    ACTIVE = 'active', 'Active'
    PAST_DUE = 'past_due', 'Past Due'
    CANCELED = 'canceled', 'Canceled'

class SubscriptionProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_profile')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.TRIAL)
    current_period_end = models.DateTimeField(null=True, blank=True)
    provider = models.CharField(max_length=20, default='paytr')
    external_customer_id = models.CharField(max_length=100, blank=True, default='')
    external_subscription_id = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    METHOD_CHOICES = [
        ('paytr', 'PayTR'),
        ('bank', 'Banka Havale/EFT'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_transactions')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, default='initiated')
    external_id = models.CharField(max_length=200, blank=True, default='')
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BankTransfer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    reference_code = models.CharField(max_length=20, unique=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def confirm(self):
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=['is_confirmed','confirmed_at'])
