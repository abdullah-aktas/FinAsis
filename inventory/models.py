from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel

class Product(BaseModel):
    """Ürün modeli"""
    name = models.CharField(max_length=200, verbose_name=_('Ürün Adı'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Ürün Kodu'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _('Ürün')
        verbose_name_plural = _('Ürünler')
        ordering = ['name']
