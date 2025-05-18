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


class TrainingProgram(models.Model):
    """Kurumsal eğitim programı modeli"""
    PROGRAM_TYPES = [
        ('workshop', 'Workshop'),
        ('certification', 'Sertifikasyon'),
        ('custom', 'Özel Program'),
    ]
    
    name = models.CharField(_('Program Adı'), max_length=100)
    program_type = models.CharField(_('Program Tipi'), max_length=20, choices=PROGRAM_TYPES)
    description = models.TextField(_('Açıklama'))
    duration = models.IntegerField(_('Süre (Saat)'))
    price_per_person = models.DecimalField(_('Kişi Başı Fiyat'), max_digits=10, decimal_places=2)
    min_participants = models.IntegerField(_('Minimum Katılımcı'), default=5)
    max_participants = models.IntegerField(_('Maksimum Katılımcı'), default=20)
    materials_included = models.BooleanField(_('Materyal Dahil'), default=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Eğitim Programı')
        verbose_name_plural = _('Eğitim Programları')
    
    def __str__(self):
        return f"{self.name} - {self.get_program_type_display()}"

