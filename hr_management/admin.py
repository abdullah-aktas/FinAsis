from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Employee, Department, Salary, Payroll, Leave

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'identity_number', 'email', 'department', 'position', 'is_active')
    list_filter = ('department', 'gender', 'marital_status', 'employment_status', 'is_active')
    search_fields = ('first_name', 'last_name', 'identity_number', 'email')
    fieldsets = (
        (_('Kişisel Bilgiler'), {
            'fields': ('first_name', 'last_name', 'identity_number', 'birth_date', 'gender', 'marital_status')
        }),
        (_('İletişim Bilgileri'), {
            'fields': ('address', 'phone', 'email', 'emergency_contact', 'emergency_phone')
        }),
        (_('İş Bilgileri'), {
            'fields': ('hire_date', 'department', 'position', 'employment_status')
        }),
        (_('Banka Bilgileri'), {
            'fields': ('bank_account', 'iban')
        }),
        (_('Durum'), {
            'fields': ('is_active',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'manager', 'budget')
    list_filter = ('parent',)
    search_fields = ('name', 'code')
    fieldsets = (
        (_('Temel Bilgiler'), {
            'fields': ('name', 'code', 'parent', 'manager')
        }),
        (_('Ek Bilgiler'), {
            'fields': ('budget', 'description')
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'base_salary', 'currency', 'effective_date', 'payment_frequency')
    list_filter = ('currency', 'payment_frequency')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'effective_date'
    fieldsets = (
        (_('Temel Bilgiler'), {
            'fields': ('employee', 'base_salary', 'currency', 'effective_date', 'payment_frequency')
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period_start', 'period_end', 'net_salary', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'period_start'
    fieldsets = (
        (_('Dönem Bilgileri'), {
            'fields': ('employee', 'period_start', 'period_end')
        }),
        (_('Maaş Bilgileri'), {
            'fields': ('base_salary', 'overtime_hours', 'overtime_pay', 'bonus', 'deductions')
        }),
        (_('Ödeme Bilgileri'), {
            'fields': ('net_salary', 'gross_salary', 'payment_date', 'payment_status', 'payment_reference')
        }),
        (_('Notlar'), {
            'fields': ('notes',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status')
    list_filter = ('leave_type', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'start_date'
    fieldsets = (
        (_('Temel Bilgiler'), {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'total_days')
        }),
        (_('Onay Bilgileri'), {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        (_('Diğer Bilgiler'), {
            'fields': ('reason',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'approved_by', 'approved_at')
