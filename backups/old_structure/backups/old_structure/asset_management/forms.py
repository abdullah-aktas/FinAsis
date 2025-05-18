# -*- coding: utf-8 -*-
from django import forms
from .models import AssetCategory, Asset, Depreciation, Maintenance, AssetTransfer, AssetDisposal

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
        fields = ['depreciation_date', 'amount', 'remaining_value', 'notes']
        widgets = {
            'depreciation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
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
            'reason', 'status', 'notes'
        ]
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class AssetDisposalForm(forms.ModelForm):
    class Meta:
        model = AssetDisposal
        fields = [
            'disposal_date', 'disposal_type', 'disposal_value',
            'reason', 'status', 'notes'
        ]
        widgets = {
            'disposal_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 