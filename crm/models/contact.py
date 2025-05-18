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


class Contact(models.Model):
    """İletişim kişisi modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(_('Ad'), max_length=100)
    last_name = models.CharField(_('Soyad'), max_length=100)
    position = models.CharField(_('Pozisyon'), max_length=100)
    department = models.CharField(_('Departman'), max_length=100)
    phone = models.CharField(_('Telefon'), max_length=20)
    mobile = models.CharField(_('Cep Telefonu'), max_length=20)
    email = models.EmailField(_('E-posta'))
    is_primary = models.BooleanField(_('Birincil İletişim'), default=False)
    notes = models.TextField(_('Notlar'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('İletişim Kişisi')
        verbose_name_plural = _('İletişim Kişileri')
        ordering = ['-is_primary', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['email']),
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

