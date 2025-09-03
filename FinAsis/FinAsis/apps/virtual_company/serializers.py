# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import VirtualCompany, Product, AccountingEntry

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

class ARAccountingEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingEntry
        fields = ['id', 'company', 'student', 'date', 'description', 'debit_account', 'credit_account', 'amount', 'effect_on_balance']
        read_only_fields = ['id', 'date', 'student']

class ARCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualCompany
        fields = ['id', 'name']

class ARProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'marker_id'] 