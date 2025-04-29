# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    VirtualCompany, Department, Employee, Project,
    Task, Budget, Report
)

@admin.register(VirtualCompany)
class VirtualCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'founded_date', 'is_active', 'created_by', 'created_at')
    list_filter = ('industry', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'email', 'tax_number')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'manager', 'budget', 'is_active', 'created_at')
    list_filter = ('company', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'manager__username')
    date_hierarchy = 'created_at'
    ordering = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'department', 'role', 'position', 'salary', 'is_active')
    list_filter = ('company', 'department', 'role', 'is_active', 'hire_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position')
    date_hierarchy = 'hire_date'
    ordering = ('user__username',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'department', 'manager', 'status', 'progress', 'is_active')
    list_filter = ('company', 'department', 'status', 'is_active', 'start_date')
    search_fields = ('name', 'description', 'manager__user__username')
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'priority', 'status', 'progress', 'due_date')
    list_filter = ('project', 'priority', 'status', 'start_date', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__user__username')
    date_hierarchy = 'due_date'
    ordering = ('priority', 'due_date')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('company', 'department', 'type', 'amount', 'date', 'created_by')
    list_filter = ('company', 'department', 'type', 'date')
    search_fields = ('description', 'created_by__username')
    date_hierarchy = 'date'
    ordering = ('-date',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'type', 'created_by', 'created_at')
    list_filter = ('company', 'type', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',) 