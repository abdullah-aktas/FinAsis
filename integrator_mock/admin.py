from django.contrib import admin
from .models import MockIntegration, MockRequest, MockScenario


@admin.register(MockIntegration)
class MockIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "integration_type",
        "success_rate",
        "response_delay_ms",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "mock_endpoint")
    list_filter = ("integration_type", "is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(MockRequest)
class MockRequestAdmin(admin.ModelAdmin):
    list_display = (
        "integration",
        "request_method",
        "request_path",
        "response_status",
        "response_time_ms",
        "user",
        "created_at",
    )
    search_fields = ("request_path", "ip_address")
    list_filter = ("integration", "request_method", "response_status", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(MockScenario)
class MockScenarioAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "integration",
        "response_code",
        "priority",
        "is_active",
        "usage_count",
    )
    search_fields = ("name", "description")
    list_filter = ("integration", "is_active", "created_at")
    readonly_fields = ("usage_count", "created_at")
