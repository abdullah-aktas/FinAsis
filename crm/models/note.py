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


class Note(models.Model):
    """Not modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(_('Başlık'), max_length=255)
    content = models.TextField(_('İçerik'))
    is_private = models.BooleanField(_('Özel'), default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notes')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Not')
        verbose_name_plural = _('Notlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_private']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.company_name}"

