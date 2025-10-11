from django.contrib import admin
from .models import AdvisorProfile, AdvisorRegistrySource, TaxpayerProfile, Engagement


@admin.register(AdvisorProfile)
class AdvisorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "verified_at")
    list_filter = ("type", "verified_at")
    search_fields = ("user__username", "chamber_no", "mersis_no")


@admin.register(AdvisorRegistrySource)
class AdvisorRegistrySourceAdmin(admin.ModelAdmin):
    list_display = ("source", "external_id", "fetched_at")
    search_fields = ("source", "external_id")


@admin.register(TaxpayerProfile)
class TaxpayerProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "vkn_tckn", "mersis_no")
    search_fields = ("name", "vkn_tckn")


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ("advisor", "taxpayer", "scope", "status", "created_at")
    list_filter = ("scope", "status")
    autocomplete_fields = ("advisor", "taxpayer")
