from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
import uuid

class Customer(models.Model):
    """Müşteri modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Müşteri Adı'), max_length=200)
    tax_number = models.CharField(
        _('Vergi/TC No'), 
        max_length=11, 
        unique=True,
        validators=[RegexValidator(regex=r'^\d{10,11}$', message=_('Vergi/TC No 10 veya 11 haneli rakam olmalıdır.'))]
    )
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100)
    address = models.TextField(_('Adres'))
    phone = models.CharField(
        _('Telefon'), 
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message=_('Telefon numarası 10-15 haneli olmalıdır.'))]
    )
    email = models.EmailField(_('E-posta'))
    
    # E-Fatura bilgileri
    is_e_invoice_user = models.BooleanField(_('E-Fatura Mükellefi'), default=False)
    is_e_archive_user = models.BooleanField(_('E-Arşiv Mükellefi'), default=False)
    
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncelleme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Müşteri')
        verbose_name_plural = _('Müşteriler') 
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tax_number})"

# Not: customers uygulamasında testler için 'tests' klasörü oluşturulmalı ve temel model testleri eklenmelidir.
# Örnek: customers/tests/test_models.py
