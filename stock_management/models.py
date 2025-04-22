from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_count_date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity}"

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('IN', 'Giriş'),
        ('OUT', 'Çıkış'),
        ('TRANSFER', 'Transfer'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='from_movements')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='to_movements', null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name}: {self.quantity}"

class StockCount(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Taslak'),
        ('IN_PROGRESS', 'Devam Ediyor'),
        ('COMPLETED', 'Tamamlandı'),
        ('CANCELLED', 'İptal Edildi'),
    )

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    count_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stok Sayımı - {self.warehouse.name} - {self.count_date}"

class StockCountItem(models.Model):
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    expected_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    counted_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    difference = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock_count} - {self.product.name}"
