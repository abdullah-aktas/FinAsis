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


class ReferralProgram(models.Model):
    referrer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='referrals_given')
    referred = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='referrals_received')
    bonus_amount = models.DecimalField(_('Bonus Miktarı'), max_digits=10, decimal_places=2)
    status = models.CharField(_('Durum'), max_length=20, choices=[
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('paid', 'Ödendi'),
    ], default='pending')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    paid_at = models.DateTimeField(_('Ödeme Tarihi'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Referans Programı')
        verbose_name_plural = _('Referans Programları')
    
    def __str__(self):
        return f"{self.referrer.company_name} -> {self.referred.company_name}"

