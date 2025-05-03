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


class LoyaltyLevel(models.Model):
    """Sadakat programı seviye modeli"""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='levels')
    level = models.CharField(_('Seviye'), max_length=20, choices=LoyaltyProgram.LEVEL_CHOICES)
    min_points = models.IntegerField(_('Minimum Puan'))
    benefits = models.JSONField(_('Avantajlar'), default=dict)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Sadakat Seviyesi')
        verbose_name_plural = _('Sadakat Seviyeleri')
    
    def __str__(self):
        return f"{self.program.name} - {self.get_level_display()}"

