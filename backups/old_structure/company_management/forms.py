# -*- coding: utf-8 -*-
from django import forms
from .models import Company, Department, Employee

class CompanyForm(forms.ModelForm):
    """Şirket formu"""
    class Meta:
        model = Company
        fields = [
            'name', 'tax_number', 'tax_office', 'address', 'phone',
            'email', 'website', 'logo', 'description', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DepartmentForm(forms.ModelForm):
    """Departman formu"""
    class Meta:
        model = Department
        fields = ['company', 'name', 'manager', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployeeForm(forms.ModelForm):
    """Çalışan formu"""
    class Meta:
        model = Employee
        fields = [
            'user', 'company', 'department', 'position',
            'hire_date', 'salary', 'notes', 'is_active'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        } 