# -*- coding: utf-8 -*-
from django import forms
from .models import AssetCategory, Asset, Depreciation, Maintenance, AssetTransfer, AssetDisposal, AssetRental

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'code', 'category', 'serial_number', 'purchase_date',
            'purchase_cost', 'current_value', 'location', 'status', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DepreciationForm(forms.ModelForm):
    class Meta:
        model = Depreciation
        fields = ['period_start', 'period_end', 'depreciation_amount', 'accumulated_depreciation']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'maintenance_date', 'maintenance_type', 'description',
            'cost', 'performed_by', 'status', 'notes'
        ]
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class AssetTransferForm(forms.ModelForm):
    class Meta:
        model = AssetTransfer
        fields = [
            'from_location', 'to_location', 'transfer_date',
            'reason'
        ]
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class AssetDisposalForm(forms.ModelForm):
    class Meta:
        model = AssetDisposal
        fields = [
            'disposal_date', 'disposal_type', 'disposal_value',
            'reason'
        ]
        widgets = {
            'disposal_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class AssetRentalForm(forms.ModelForm):
    class Meta:
        model = AssetRental
        fields = [
            'renter', 'start_date', 'end_date', 'rental_fee',
            'status', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 