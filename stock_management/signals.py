from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StockMovement, Product, StockAlert

@receiver(post_save, sender=StockMovement)
def update_stock_alerts(sender, instance, created, **kwargs):
    """
    Stok hareketi kaydedildiğinde stok uyarılarını günceller.
    """
    product = instance.product
    current_stock = product.current_stock

    # Düşük stok kontrolü
    if current_stock <= product.min_stock_level:
        StockAlert.objects.get_or_create(
            product=product,
            alert_type='LOW',
            defaults={
                'message': f'Ürün stok seviyesi minimum seviyenin altına düştü. Mevcut stok: {current_stock}'
            }
        )
    else:
        StockAlert.objects.filter(product=product, alert_type='LOW').delete()

    # Yüksek stok kontrolü
    if current_stock >= product.max_stock_level:
        StockAlert.objects.get_or_create(
            product=product,
            alert_type='HIGH',
            defaults={
                'message': f'Ürün stok seviyesi maksimum seviyenin üzerine çıktı. Mevcut stok: {current_stock}'
            }
        )
    else:
        StockAlert.objects.filter(product=product, alert_type='HIGH').delete() 