# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, StockMovement, ProductionOrder

@receiver(post_save, sender=StockMovement)
def update_product_stock(sender, instance, created, **kwargs):
    if created:
        cache.delete(f'product_stock_{instance.product.id}')

@receiver([post_save, post_delete], sender=ProductionOrder)
def clear_production_cache(sender, instance, **kwargs):
    cache.delete(f'production_orders_{instance.product.id}')
    cache.delete('active_production_orders') 