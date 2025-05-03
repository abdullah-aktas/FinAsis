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


class InteractionLog(models.Model):
    """Müşteri etkileşim kaydı modeli"""
    INTERACTION_TYPES = [
        ('call', 'Telefon'),
        ('email', 'E-posta'),
        ('meeting', 'Toplantı'),
        ('note', 'Not'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions', verbose_name='Müşteri')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, verbose_name='Etkileşim Tipi')
    subject = models.CharField(max_length=200, verbose_name='Konu')
    notes = models.TextField(verbose_name='Notlar')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Tarih')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    
    class Meta:
        verbose_name = 'Etkileşim Kaydı'
        verbose_name_plural = 'Etkileşim Kayıtları'
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_interaction_type_display()} - {self.subject}"
