# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    depreciation_period = models.IntegerField(help_text="Amortisman süresi (ay)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Aktif'),
        ('MAINTENANCE', 'Bakımda'),
        ('RETIRED', 'Emekli'),
        ('SOLD', 'Satıldı'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    description = models.TextField(blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Depreciation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    depreciation_amount = models.DecimalField(max_digits=12, decimal_places=2)
    accumulated_depreciation = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.name} - {self.period_start} to {self.period_end}"

class Maintenance(models.Model):
    MAINTENANCE_TYPES = (
        ('PREVENTIVE', 'Önleyici Bakım'),
        ('CORRECTIVE', 'Düzeltici Bakım'),
        ('INSPECTION', 'Kontrol'),
    )

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    maintenance_date = models.DateField()
    next_maintenance_date = models.DateField(null=True, blank=True)
    performed_by = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_type} ({self.maintenance_date})" 