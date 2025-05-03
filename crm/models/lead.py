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


class Lead(models.Model):
    """Potansiyel müşteri/aday modeli"""
    LEAD_STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('contacted', 'İletişime Geçildi'),
        ('qualified', 'Kalifiye'),
        ('proposal', 'Teklif Verildi'),
        ('negotiation', 'Pazarlık Aşamasında'),
        ('won', 'Kazanıldı'),
        ('lost', 'Kaybedildi'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name='Ad')
    last_name = models.CharField(max_length=100, verbose_name='Soyad')
    email = models.EmailField(verbose_name='E-posta')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    company = models.CharField(max_length=200, blank=True, verbose_name='Şirket')
    position = models.CharField(max_length=100, blank=True, verbose_name='Pozisyon')
    source = models.CharField(max_length=100, blank=True, verbose_name='Kaynak')
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new', verbose_name='Durum')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads', verbose_name='Atanan Kişi')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Aday'
        verbose_name_plural = 'Adaylar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

