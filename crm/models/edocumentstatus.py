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


class EDocumentStatus(models.Model):
    """E-belge durum takibi"""
    DOCUMENT_TYPES = (
        ('einvoice', _('E-Fatura')),
        ('earchive', _('E-Arşiv')),
        ('edespatch', _('E-İrsaliye')),
        ('ereceipt', _('E-Serbest Meslek Makbuzu')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Beklemede')),
        ('processing', _('İşleniyor')),
        ('sent', _('Gönderildi')),
        ('delivered', _('Teslim Edildi')),
        ('accepted', _('Kabul Edildi')),
        ('rejected', _('Reddedildi')),
        ('error', _('Hata')),
    )
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='e_documents', verbose_name=_('Satış'))
    document_type = models.CharField(_('Belge Tipi'), max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(_('Belge Numarası'), max_length=50, blank=True)
    external_id = models.CharField(_('Harici ID'), max_length=100, blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    status_message = models.TextField(_('Durum Mesajı'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('E-Belge Durumu')
        verbose_name_plural = _('E-Belge Durumları')
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_number}"

