from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    VirtualCompany, Department, Employee, Project,
    Task, Budget, Report
)

class VirtualCompanyForm(forms.ModelForm):
    class Meta:
        model = VirtualCompany
        fields = [
            'name', 'description', 'logo', 'industry',
            'founded_date', 'website', 'email', 'phone',
            'address', 'tax_number', 'tax_office', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'founded_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager', 'budget', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user', 'department', 'role', 'position',
            'salary', 'hire_date', 'is_active'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'department', 'manager',
            'start_date', 'end_date', 'budget', 'status',
            'progress', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
            'progress': forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'priority',
            'status', 'start_date', 'due_date', 'progress'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'type': 'range', 'min': '0', 'max': '100'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['type', 'amount', 'description', 'date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'type', 'content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        } 