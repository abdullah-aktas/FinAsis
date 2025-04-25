from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from .models import (
    Customer, Contact, Opportunity, Activity,
    Document, Communication, Note,
    LoyaltyProgram, LoyaltyLevel, CustomerLoyalty,
    SeasonalCampaign, PartnershipProgram, Partner,
    InteractionLog
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 'tax_number', 'email', 'phone',
        'industry', 'risk_level', 'credit_score',
        'annual_revenue', 'employee_count', 'is_active',
        'created_at', 'updated_at'
    )
    list_filter = (
        'industry', 'risk_level', 'is_active',
        'created_at', 'updated_at'
    )
    search_fields = (
        'company_name', 'tax_number', 'email',
        'phone', 'address'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': (
                'company_name', 'tax_number', 'email',
                'phone', 'address'
            )
        }),
        ('İş Bilgileri', {
            'fields': (
                'industry', 'annual_revenue',
                'employee_count'
            )
        }),
        ('Risk ve Kredi', {
            'fields': (
                'risk_level', 'credit_score',
                'credit_limit'
            )
        }),
        ('Durum', {
            'fields': ('is_active',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at')
        })
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
        'title', 'customer_link', 'amount',
        'probability', 'stage', 'expected_close_date',
        'actual_close_date', 'status', 'created_at'
    )
    list_filter = (
        'stage', 'status', 'probability',
        'expected_close_date', 'created_at'
    )
    search_fields = (
        'title', 'description', 'customer__company_name'
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
        'title', 'type', 'file_size',
        'customer_link', 'uploaded_by',
        'created_at'
    )
    list_filter = ('type', 'created_at')
    search_fields = (
        'title', 'description',
        'customer__company_name'
    )
    readonly_fields = (
        'file_size', 'created_at',
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

@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'start_date',
        'end_date', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LoyaltyLevel)
class LoyaltyLevelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'program', 'min_points',
        'max_points', 'benefits', 'created_at'
    )
    list_filter = ('program', 'created_at')
    search_fields = ('name', 'benefits')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CustomerLoyalty)
class CustomerLoyaltyAdmin(admin.ModelAdmin):
    list_display = (
        'customer_link', 'program_link',
        'current_level', 'total_points',
        'created_at'
    )
    list_filter = ('program', 'current_level', 'created_at')
    search_fields = (
        'customer__company_name',
        'program__name'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'

    def program_link(self, obj):
        url = reverse('admin:crm_loyaltyprogram_change', args=[obj.program.id])
        return format_html('<a href="{}">{}</a>', url, obj.program.name)
    program_link.short_description = 'Program'

@admin.register(SeasonalCampaign)
class SeasonalCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'start_date',
        'end_date', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PartnershipProgram)
class PartnershipProgramAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'start_date',
        'end_date', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'program_link', 'contact_person',
        'email', 'phone', 'is_active',
        'created_at'
    )
    list_filter = ('program', 'is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

    def program_link(self, obj):
        url = reverse('admin:crm_partnershipprogram_change', args=[obj.program.id])
        return format_html('<a href="{}">{}</a>', url, obj.program.name)
    program_link.short_description = 'Program'

@admin.register(InteractionLog)
class InteractionLogAdmin(admin.ModelAdmin):
    list_display = (
        'customer_link', 'type', 'description',
        'created_by', 'created_at'
    )
    list_filter = ('type', 'created_at')
    search_fields = (
        'description', 'customer__company_name',
        'created_by__username'
    )
    readonly_fields = ('created_at', 'updated_at')

    def customer_link(self, obj):
        url = reverse('admin:crm_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.company_name)
    customer_link.short_description = 'Müşteri'
