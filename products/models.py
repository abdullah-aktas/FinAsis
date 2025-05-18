from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Product(models.Model):
    """Ürün modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(_('Ürün Kodu'), max_length=50, unique=True)
    name = models.CharField(_('Ürün Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    unit = models.CharField(_('Birim'), max_length=10, default='ADET')
    
    # Fiyat bilgileri
    purchase_price = models.DecimalField(
        _('Alış Fiyatı'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    sale_price = models.DecimalField(
        _('Satış Fiyatı'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_rate = models.DecimalField(
        _('KDV Oranı (%)'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('18.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Stok bilgileri
    stock_quantity = models.DecimalField(
        _('Stok Miktarı'),
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000')
    )
    min_stock_level = models.DecimalField(
        _('Minimum Stok Seviyesi'),
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000')
    )
    
    # Takip bilgileri
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncelleme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ürün')
        verbose_name_plural = _('Ürünler')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"
