# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Customer, Contact, Opportunity, Activity, Document

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_number', 'tax_office', 'phone', 'email']
    search_fields = ['name', 'tax_number', 'tax_office', 'phone', 'email']
    ordering = ['name']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'position', 'phone', 'email']
    list_filter = ['customer']
    search_fields = ['name', 'customer__name', 'position', 'phone', 'email']
    ordering = ['customer', 'name']

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'amount', 'probability', 'status', 'priority', 'expected_close_date']
    list_filter = ['status', 'priority', 'customer']
    search_fields = ['name', 'customer__name']
    ordering = ['-created_at']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['type', 'subject', 'customer', 'due_date', 'status', 'assigned_to']
    list_filter = ['type', 'status', 'customer']
    search_fields = ['subject', 'customer__name']
    ordering = ['-due_date']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'document_type', 'file']
    list_filter = ['document_type', 'customer']
    search_fields = ['title', 'customer__name']
    ordering = ['-created_at']
