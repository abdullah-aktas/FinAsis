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


class ServiceSubscription(models.Model):
    """Hizmet aboneliği modeli"""
    SUBSCRIPTION_TYPES = [
        ('package', 'Premium Paket'),
        ('consulting', 'Danışmanlık'),
        ('training', 'Eğitim'),
        ('api', 'API'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('cancelled', 'İptal Edildi'),
        ('expired', 'Süresi Doldu'),
    ]
    
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='subscriptions')
    subscription_type = models.CharField(_('Abonelik Tipi'), max_length=20, choices=SUBSCRIPTION_TYPES)
    package = models.ForeignKey(PremiumPackage, on_delete=models.SET_NULL, null=True, blank=True)
    consulting_service = models.ForeignKey(ConsultingService, on_delete=models.SET_NULL, null=True, blank=True)
    training_program = models.ForeignKey(TrainingProgram, on_delete=models.SET_NULL, null=True, blank=True)
    api_pricing = models.ForeignKey(APIPricing, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='active')
    monthly_fee = models.DecimalField(_('Aylık Ücret'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Hizmet Aboneliği')
        verbose_name_plural = _('Hizmet Abonelikleri')
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_subscription_type_display()}"
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    def calculate_monthly_revenue(self):
        """Aylık gelir hesaplama"""
        if self.subscription_type == 'package':
            return self.monthly_fee
        elif self.subscription_type == 'consulting':
            return self.consulting_service.hourly_rate * self.consulting_service.min_hours
        elif self.subscription_type == 'training':
            return self.training_program.price_per_person * self.training_program.min_participants
        elif self.subscription_type == 'api':
            return self.api_pricing.base_price + (self.api_pricing.price_per_request * self.api_pricing.requests_per_month)
        return Decimal('0')

