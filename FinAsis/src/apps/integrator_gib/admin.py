from django.contrib import admin
from .models import IntegratorConfig, AccessToken


@admin.register(IntegratorConfig)
class IntegratorConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "base_url")


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ("integrator", "expires_at", "created_at")
    autocomplete_fields = ("integrator",)
