from rest_framework import serializers
from .models import Product, StockMovement, ProductionOrder, BillOfMaterials, QualityControl

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('stock_quantity', 'created_at', 'updated_at')

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')

class BillOfMaterialsSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source='component.name', read_only=True)
    
    class Meta:
        model = BillOfMaterials
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ProductionOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProductionOrder
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

class QualityControlSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)
    production_order_number = serializers.CharField(source='production_order.order_number', read_only=True)
    
    class Meta:
        model = QualityControl
        fields = '__all__'
        read_only_fields = ('created_at', 'inspector') 