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


class Activity(models.Model):
    """Aktivite modeli"""
    TYPE_CHOICES = [
        ('call', _('Telefon')),
        ('meeting', _('Toplantı')),
        ('email', _('E-posta')),
        ('task', _('Görev'))
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(_('Konu'), max_length=255)
    description = models.TextField(_('Açıklama'))
    due_date = models.DateTimeField(_('Bitiş Tarihi'))
    completed = models.BooleanField(_('Tamamlandı'), default=False)
    completed_at = models.DateTimeField(_('Tamamlanma Tarihi'), null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Aktivite')
        verbose_name_plural = _('Aktiviteler')
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['due_date']),
        ]
    def __str__(self):
        return f"{self.type} - {self.subject}"
