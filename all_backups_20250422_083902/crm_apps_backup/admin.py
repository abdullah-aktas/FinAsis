from django.contrib import admin
from .models import Lead, Customer, CustomerNote, CustomerDocument, Opportunity, Activity

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'company', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'assigned_to', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'company')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Şirket Bilgileri', {
            'fields': ('company', 'position')
        }),
        ('Durum Bilgileri', {
            'fields': ('source', 'status', 'notes', 'assigned_to')
        }),
    )

class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 0

class CustomerDocumentInline(admin.TabularInline):
    model = CustomerDocument
    extra = 0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'company', 'tax_number')
    date_hierarchy = 'created_at'
    inlines = [CustomerNoteInline, CustomerDocumentInline]
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'email', 'phone', 'company', 'is_active')
        }),
        ('Adres Bilgileri', {
            'fields': ('address',)
        }),
        ('Vergi Bilgileri', {
            'fields': ('tax_number', 'tax_office')
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_by',)
        }),
    )

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'value', 'status', 'probability', 'expected_close_date', 'assigned_to')
    list_filter = ('status', 'probability', 'expected_close_date', 'assigned_to')
    search_fields = ('name', 'customer__name', 'notes')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'customer', 'value', 'status')
        }),
        ('Detaylar', {
            'fields': ('probability', 'expected_close_date', 'notes', 'assigned_to', 'created_by')
        }),
    )

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('subject', 'type', 'customer', 'opportunity', 'due_date', 'completed', 'assigned_to')
    list_filter = ('type', 'completed', 'due_date', 'assigned_to')
    search_fields = ('subject', 'description', 'customer__name')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('type', 'subject', 'description')
        }),
        ('İlişkiler', {
            'fields': ('customer', 'opportunity')
        }),
        ('Zamanlama', {
            'fields': ('due_date', 'completed', 'completed_at')
        }),
        ('Atamalar', {
            'fields': ('assigned_to', 'created_by')
        }),
    )
