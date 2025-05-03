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


class Partner(models.Model):
    """İş ortağı modeli"""
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('active', 'Aktif'),
        ('suspended', 'Askıya Alındı'),
        ('terminated', 'Sonlandırıldı'),
    ]
    
    program = models.ForeignKey(PartnershipProgram, on_delete=models.CASCADE, related_name='partners')
    company_name = models.CharField(_('Şirket Adı'), max_length=200)
    contact_person = models.CharField(_('İletişim Kişisi'), max_length=100)
    email = models.EmailField(_('E-posta'))
    phone = models.CharField(_('Telefon'), max_length=20)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    total_sales = models.DecimalField(_('Toplam Satış'), max_digits=10, decimal_places=2, default=0)
    total_commission = models.DecimalField(_('Toplam Komisyon'), max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('İş Ortağı')
        verbose_name_plural = _('İş Ortakları')
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['status']),
            models.Index(fields=['program']),
        ]
    
    def __str__(self):
        return f"{self.company_name} - {self.program.name}"

