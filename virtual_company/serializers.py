from rest_framework import serializers
from .models import VirtualCompany, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class VirtualCompanySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = VirtualCompany
        fields = ['id', 'name', 'description', 'balance', 'created_at', 'updated_at', 'products']
        read_only_fields = ['created_at', 'updated_at', 'balance'] 