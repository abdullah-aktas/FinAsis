# -*- coding: utf-8 -*-
from django.utils import timezone
from django.db.models import Sum, F
from .models import Product, StockAlert

def check_stock_alerts(product):
    """
    Ürün stok seviyesini kontrol eder ve gerekli uyarıları oluşturur.
    """
    current_stock = product.stock_movements.aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Düşük stok kontrolü
    if current_stock <= product.min_stock_level:
        StockAlert.objects.create(
            product=product,
            alert_type='LOW',
            message=f'{product.name} ürününün stok seviyesi minimum seviyenin altına düştü. '
                   f'Mevcut stok: {current_stock}, Minimum stok: {product.min_stock_level}'
        )
    
    # Yüksek stok kontrolü
    if current_stock >= product.max_stock_level:
        StockAlert.objects.create(
            product=product,
            alert_type='HIGH',
            message=f'{product.name} ürününün stok seviyesi maksimum seviyeyi aştı. '
                   f'Mevcut stok: {current_stock}, Maksimum stok: {product.max_stock_level}'
        )

def get_stock_value(products):
    """
    Verilen ürünlerin toplam stok değerini hesaplar.
    """
    return sum(product.stock_value for product in products)

def get_stock_movements_summary(product, start_date=None, end_date=None):
    """
    Belirli bir tarih aralığında ürünün stok hareketlerinin özetini döndürür.
    """
    movements = product.stock_movements.all()
    
    if start_date:
        movements = movements.filter(created_at__gte=start_date)
    if end_date:
        movements = movements.filter(created_at__lte=end_date)
    
    return movements.aggregate(
        total_in=Sum('quantity', filter=F('movement_type') == 'IN'),
        total_out=Sum('quantity', filter=F('movement_type') == 'OUT'),
        total_adjustment=Sum('quantity', filter=F('movement_type') == 'ADJ')
    )

def get_low_stock_products(threshold=None):
    """
    Stok seviyesi düşük olan ürünleri döndürür.
    """
    products = Product.objects.annotate(
        current_stock=Sum('stock_movements__quantity')
    ).filter(current_stock__isnull=False)
    
    if threshold is not None:
        return products.filter(current_stock__lte=threshold)
    
    return products.filter(current_stock__lte=F('min_stock_level'))

def get_high_stock_products(threshold=None):
    """
    Stok seviyesi yüksek olan ürünleri döndürür.
    """
    products = Product.objects.annotate(
        current_stock=Sum('stock_movements__quantity')
    ).filter(current_stock__isnull=False)
    
    if threshold is not None:
        return products.filter(current_stock__gte=threshold)
    
    return products.filter(current_stock__gte=F('max_stock_level'))

def get_stock_trend(product, days=30):
    """
    Son 30 günlük stok trendini döndürür.
    """
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=days)
    
    movements = product.stock_movements.filter(
        created_at__range=(start_date, end_date)
    ).values('created_at__date').annotate(
        total=Sum('quantity')
    ).order_by('created_at__date')
    
    return list(movements)

def calculate_stock_turnover(product, start_date=None, end_date=None):
    """
    Stok devir hızını hesaplar.
    """
    if not start_date:
        start_date = timezone.now() - timezone.timedelta(days=365)
    if not end_date:
        end_date = timezone.now()
    
    # Ortalama stok
    movements = product.stock_movements.filter(
        created_at__range=(start_date, end_date)
    )
    avg_stock = movements.aggregate(
        avg=Sum('quantity') / movements.count()
    )['avg'] or 0
    
    # Satış miktarı
    sales = movements.filter(movement_type='OUT').aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Stok devir hızı
    if avg_stock > 0:
        turnover = sales / avg_stock
    else:
        turnover = 0
    
    return {
        'average_stock': avg_stock,
        'sales_quantity': sales,
        'turnover_rate': turnover
    } 