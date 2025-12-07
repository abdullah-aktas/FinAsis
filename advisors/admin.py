from django.contrib import admin
from .models import (
    AdvisorProfile,
    AdvisorRegistrySource,
    TaxpayerProfile,
    Engagement,
    AdvisorService,
    ConsultationSession,
    AdvisorReport,
    ClientContract,
    AdvisorTimeTracking,
    ClientDocument,
    AdvisorTask,
)


@admin.register(AdvisorProfile)
class AdvisorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "chamber_no", "verified_at")
    list_filter = ("type", "verified_at")
    search_fields = ("user__username", "chamber_no", "mersis_no")
    readonly_fields = ("verified_at",)


@admin.register(AdvisorRegistrySource)
class AdvisorRegistrySourceAdmin(admin.ModelAdmin):
    list_display = ("source", "external_id", "fetched_at")
    search_fields = ("source", "external_id")
    readonly_fields = ("fetched_at",)


@admin.register(TaxpayerProfile)
class TaxpayerProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "vkn_tckn", "mersis_no", "company")
    search_fields = ("name", "vkn_tckn", "mersis_no")
    list_filter = ("company",)


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ("advisor", "taxpayer", "scope", "status", "created_at")
    list_filter = ("scope", "status")
    search_fields = ("advisor__user__username", "taxpayer__name")


@admin.register(AdvisorService)
class AdvisorServiceAdmin(admin.ModelAdmin):
    list_display = (
        "service_name",
        "advisor",
        "service_type",
        "pricing_model",
        "price",
        "is_active",
    )
    list_filter = ("service_type", "pricing_model", "is_active")
    search_fields = ("service_name", "advisor__user__username")


@admin.register(ConsultationSession)
class ConsultationSessionAdmin(admin.ModelAdmin):
    list_display = (
        "taxpayer",
        "advisor",
        "session_type",
        "scheduled_date",
        "status",
        "billable",
    )
    list_filter = ("status", "session_type", "billable")
    search_fields = ("taxpayer__name", "advisor__user__username")
    date_hierarchy = "scheduled_date"


@admin.register(AdvisorReport)
class AdvisorReportAdmin(admin.ModelAdmin):
    list_display = ("title", "taxpayer", "report_type", "is_approved", "delivered_at")
    list_filter = ("report_type", "is_approved")
    search_fields = ("title", "taxpayer__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ClientContract)
class ClientContractAdmin(admin.ModelAdmin):
    list_display = (
        "contract_number",
        "taxpayer",
        "advisor",
        "contract_type",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("contract_type", "status", "auto_renew")
    search_fields = ("contract_number", "taxpayer__name", "title")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AdvisorTimeTracking)
class AdvisorTimeTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "advisor",
        "taxpayer",
        "date",
        "duration_minutes",
        "total_amount",
        "billable",
        "invoiced",
    )
    list_filter = ("billable", "invoiced", "date")
    search_fields = ("advisor__user__username", "taxpayer__name", "task_description")
    date_hierarchy = "date"


@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "taxpayer",
        "document_type",
        "uploaded_by",
        "is_confidential",
        "uploaded_at",
    )
    list_filter = ("document_type", "is_confidential")
    search_fields = ("title", "taxpayer__name")
    readonly_fields = ("uploaded_at", "file_size")


@admin.register(AdvisorTask)
class AdvisorTaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "advisor",
        "taxpayer",
        "task_type",
        "priority",
        "due_date",
        "is_completed",
    )
    list_filter = ("task_type", "priority", "is_completed")
    search_fields = ("title", "advisor__user__username", "taxpayer__name")
    date_hierarchy = "due_date"
