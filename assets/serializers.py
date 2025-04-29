# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import (
    AssetCategory, Asset, Depreciation, 
    Maintenance, AssetTransfer, AssetDisposal,
    AssetRental
)

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'code', 'description', 'depreciation_period']
        read_only_fields = ['id']

class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'code', 'category', 'category_name',
            'purchase_date', 'purchase_cost', 'current_value',
            'salvage_value', 'location', 'status', 'description',
            'serial_number', 'warranty_end_date', 'qr_code',
            'barcode', 'image', 'assigned_to', 'assigned_to_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DepreciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depreciation
        fields = [
            'id', 'asset', 'period_start', 'period_end',
            'depreciation_amount', 'accumulated_depreciation'
        ]
        read_only_fields = ['id']

class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = [
            'id', 'asset', 'maintenance_type', 'status',
            'description', 'cost', 'maintenance_date',
            'next_maintenance_date', 'performed_by', 'notes'
        ]
        read_only_fields = ['id']

class AssetTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTransfer
        fields = [
            'id', 'asset', 'from_location', 'to_location',
            'transfer_date', 'reason', 'approved_by'
        ]
        read_only_fields = ['id']

class AssetDisposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDisposal
        fields = [
            'id', 'asset', 'disposal_type', 'disposal_date',
            'disposal_value', 'reason', 'approved_by'
        ]
        read_only_fields = ['id']

class AssetRentalSerializer(serializers.ModelSerializer):
    renter_name = serializers.CharField(source='renter.get_full_name', read_only=True)
    
    class Meta:
        model = AssetRental
        fields = [
            'id', 'asset', 'renter', 'renter_name',
            'start_date', 'end_date', 'rental_fee',
            'status', 'notes'
        ]
        read_only_fields = ['id'] 