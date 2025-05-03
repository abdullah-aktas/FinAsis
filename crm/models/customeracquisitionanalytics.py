# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounting.models import BaseModel, Account
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomerAcquisitionAnalytics(models.Model):
    """Müşteri edinme analitikleri modeli"""
    
    CHANNEL_CHOICES = [
        ('google_ads', 'Google Ads'),
        ('facebook_ads', 'Facebook Ads'),
        ('referral', 'Referans'),
        ('organic', 'Organik'),
        ('direct', 'Doğrudan'),
        ('email', 'E-posta'),
        ('social', 'Sosyal Medya'),
        ('other', 'Diğer')
    ]
    
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        verbose_name="Edinme Kanalı"
    )
    total_customers = models.IntegerField(
        default=0,
        verbose_name="Toplam Müşteri"
    )
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Dönüşüm Oranı (%)"
    )
    acquisition_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Edinme Maliyeti"
    )
    average_lifetime_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Ortalama Yaşam Boyu Değer"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Son Güncelleme"
    )
    
    class Meta:
        verbose_name = "Müşteri Edinme Analitiği"
        verbose_name_plural = "Müşteri Edinme Analitikleri"
        ordering = ['-total_customers']
    
    def __str__(self):
        return f"{self.get_channel_display()} - {self.total_customers} müşteri"
    
    def update_metrics(self):
        """Metrikleri günceller"""
        # Dönüşüm oranını hesapla
        total_trials = Customer.objects.filter(
            acquisition_channel=self.channel,
            is_trial=True
        ).count()
        
        if total_trials > 0:
            self.conversion_rate = (self.total_customers / total_trials) * 100
        
        # Ortalama yaşam boyu değeri hesapla
        customers = Customer.objects.filter(acquisition_channel=self.channel)
        total_value = sum(customer.total_revenue for customer in customers)
        
        if self.total_customers > 0:
            self.average_lifetime_value = total_value / self.total_customers
        
        self.save()

