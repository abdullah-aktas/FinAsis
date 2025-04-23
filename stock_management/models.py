from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(_('Kategori Adı'), max_length=100, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kategori')
        verbose_name_plural = _('Kategoriler')
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(_('Ürün Adı'), max_length=200)
    sku = models.CharField(_('SKU'), max_length=50, unique=True)
    barcode = models.CharField(_('Barkod'), max_length=50, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField(_('Açıklama'), blank=True)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    tax_rate = models.DecimalField(_('Vergi Oranı'), max_digits=5, decimal_places=2, default=18, validators=[MinValueValidator(0), MaxValueValidator(100)])
    min_stock_level = models.PositiveIntegerField(_('Minimum Stok Seviyesi'), default=0)
    max_stock_level = models.PositiveIntegerField(_('Maksimum Stok Seviyesi'), default=1000)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ürün')
        verbose_name_plural = _('Ürünler')
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def current_stock(self):
        return self.stock_movements.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def stock_value(self):
        return self.current_stock * self.unit_price

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', _('Giriş')),
        ('OUT', _('Çıkış')),
        ('ADJ', _('Düzeltme')),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(_('Hareket Tipi'), max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(_('Miktar'))
    reference = models.CharField(_('Referans'), max_length=100, blank=True)
    notes = models.TextField(_('Notlar'), blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='stock_movements')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Stok Hareketi')
        verbose_name_plural = _('Stok Hareketleri')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'movement_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni kayıt
            if self.movement_type == 'OUT' and self.quantity > self.product.current_stock:
                raise ValueError(_('Yetersiz stok miktarı'))
        super().save(*args, **kwargs)

class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    alert_type = models.CharField(_('Uyarı Tipi'), max_length=20, choices=[
        ('LOW', _('Düşük Stok')),
        ('HIGH', _('Yüksek Stok')),
        ('EXPIRING', _('Son Kullanma Tarihi Yaklaşıyor')),
    ])
    message = models.TextField(_('Mesaj'))
    is_read = models.BooleanField(_('Okundu'), default=False)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Stok Uyarısı')
        verbose_name_plural = _('Stok Uyarıları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'alert_type']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"
