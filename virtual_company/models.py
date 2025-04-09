from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class VirtualCompany(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    capital = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = 'Sanal Şirket'
        verbose_name_plural = 'Sanal Şirketler'

# Stok Yönetimi Modelleri
class Product(models.Model):
    name = models.CharField(_('Ürün Adı'), max_length=200)
    code = models.CharField(_('Ürün Kodu'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(_('Stok Miktarı'), default=0)
    min_stock_level = models.IntegerField(_('Minimum Stok Seviyesi'), default=10)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ürün')
        verbose_name_plural = _('Ürünler')

    def __str__(self):
        return f"{self.name} ({self.code})"

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', _('Giriş')),
        ('out', _('Çıkış')),
        ('transfer', _('Transfer')),
        ('adjustment', _('Düzeltme')),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(_('Hareket Tipi'), max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(_('Miktar'))
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    reference = models.CharField(_('Referans'), max_length=100)
    notes = models.TextField(_('Notlar'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Stok Hareketi')
        verbose_name_plural = _('Stok Hareketleri')

# Üretim Yönetimi Modelleri
class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('planned', _('Planlandı')),
        ('in_progress', _('Üretimde')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    )

    order_number = models.CharField(_('Üretim Emri No'), max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_orders')
    quantity = models.IntegerField(_('Üretim Miktarı'))
    planned_start_date = models.DateField(_('Planlanan Başlangıç'))
    planned_end_date = models.DateField(_('Planlanan Bitiş'))
    actual_start_date = models.DateField(_('Gerçek Başlangıç'), null=True, blank=True)
    actual_end_date = models.DateField(_('Gerçek Bitiş'), null=True, blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(_('Notlar'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Üretim Emri')
        verbose_name_plural = _('Üretim Emirleri')

class BillOfMaterials(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_masters')
    component = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_components')
    quantity = models.DecimalField(_('Miktar'), max_digits=10, decimal_places=3)
    unit = models.CharField(_('Birim'), max_length=20)
    notes = models.TextField(_('Notlar'), blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ürün Ağacı')
        verbose_name_plural = _('Ürün Ağaçları')
        unique_together = ('product', 'component')

class QualityControl(models.Model):
    RESULT_CHOICES = (
        ('passed', _('Geçti')),
        ('failed', _('Başarısız')),
        ('conditional', _('Şartlı Kabul')),
    )

    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='quality_controls')
    inspection_date = models.DateTimeField(_('Kontrol Tarihi'))
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    result = models.CharField(_('Sonuç'), max_length=20, choices=RESULT_CHOICES)
    notes = models.TextField(_('Notlar'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kalite Kontrol')
        verbose_name_plural = _('Kalite Kontroller') 