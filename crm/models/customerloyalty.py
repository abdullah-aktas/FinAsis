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


class CustomerLoyalty(models.Model):
    """Müşteri sadakat bilgileri modeli"""
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='loyalty_info')
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    current_level = models.ForeignKey(LoyaltyLevel, on_delete=models.SET_NULL, null=True)
    total_points = models.IntegerField(_('Toplam Puan'), default=0)
    points_expiry_date = models.DateField(_('Puan Son Kullanma Tarihi'), null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Müşteri Sadakat Bilgisi')
        verbose_name_plural = _('Müşteri Sadakat Bilgileri')
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['total_points']),
            models.Index(fields=['points_expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.program.name}"

