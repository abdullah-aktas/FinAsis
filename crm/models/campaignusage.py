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


class CampaignUsage(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='usages')
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='campaign_usages')
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE, related_name='campaign_usages')
    discount_amount = models.DecimalField(_('İndirim Miktarı'), max_digits=10, decimal_places=2)
    bonus_amount = models.DecimalField(_('Bonus Miktarı'), max_digits=10, decimal_places=2, null=True, blank=True)
    used_at = models.DateTimeField(_('Kullanım Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kampanya Kullanımı')
        verbose_name_plural = _('Kampanya Kullanımları')
    
    def __str__(self):
        return f"{self.campaign.name} - {self.customer.company_name}"

