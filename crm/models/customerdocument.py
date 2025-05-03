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


class CustomerDocument(models.Model):
    """Müşteri belgesi modeli"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_documents', verbose_name='Müşteri')
    title = models.CharField(max_length=200, verbose_name='Başlık')
    file = models.FileField(upload_to='customer_documents/', verbose_name='Dosya')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Müşteri Belgesi'
        verbose_name_plural = 'Müşteri Belgeleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.company_name} - {self.title}"

