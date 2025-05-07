# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import (
    Customer, Contact, Opportunity, Activity,
    Document, Communication, Note
)
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_number', 'credit_score', 'phone', 'email', 'is_active')
    search_fields = ('name', 'tax_number', 'email')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'tax_number', 'tax_office')
        }),
        ('İletişim Bilgileri', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Finansal Bilgiler', {
            'fields': ('credit_score',)
        }),
        ('Durum', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone',
        'position', 'department', 'is_primary',
        'customer_link', 'created_at'
    )
    list_filter = (
        'position', 'department', 'is_primary',
        'created_at'
    )
    search_fields = (
        'first_name', 'last_name', 'email',
        'phone', 'customer__company_name'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'customer_link', 'value',
        'probability', 'status', 'expected_close_date',
        'created_at'
    )
    list_filter = (
        'status', 'probability',
        'expected_close_date', 'created_at'
    )
    search_fields = (
        'name', 'notes', 'customer__company_name'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'type', 'due_date',
        'completed', 'customer_link',
        'opportunity_link', 'created_at'
    )
    list_filter = (
        'type', 'completed', 'due_date',
        'created_at'
    )
    search_fields = (
        'subject', 'description',
        'customer__company_name',
        'opportunity__title'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        if obj.customer:
            url = reverse('admin:crm_customer_change', args=[obj.customer.id])
            return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
        return '-'
    customer_link.short_description = 'Müşteri'

    def opportunity_link(self, obj):
        if obj.opportunity:
            url = reverse('admin:crm_opportunity_change', args=[obj.opportunity.id])
            return format_html('<a href="{}">{}</a>', url, obj.opportunity.title)
        return '-'
    opportunity_link.short_description = 'Fırsat'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type',
        'customer_link', 'uploaded_by',
        'created_at'
    )
    list_filter = ('type', 'created_at')
    search_fields = (
        'title', 'description',
        'customer__company_name'
    )
    readonly_fields = (
        'created_at',
        'updated_at'
    )

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'

@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'type', 'direction',
        'status', 'customer_link',
        'contact_link', 'created_at'
    )
    list_filter = (
        'type', 'direction', 'status',
        'created_at'
    )
    search_fields = (
        'subject', 'content',
        'customer__company_name',
        'contact__first_name',
        'contact__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'

    def contact_link(self, obj):
        if obj.contact:
            url = reverse('admin:crm_contact_change', args=[obj.contact.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                f'{obj.contact.first_name} {obj.contact.last_name}'
            )
        return '-'
    contact_link.short_description = 'İletişim Kişisi'

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'customer_link',
        'created_by', 'created_at'
    )
    list_filter = ('created_at',)
    search_fields = (
        'title', 'content',
        'customer__company_name'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'
