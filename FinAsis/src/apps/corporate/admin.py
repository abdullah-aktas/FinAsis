from django.contrib import admin
from .models import PressRelease, InvestorDocument, TeamMember

@admin.register(PressRelease)
class PressReleaseAdmin(admin.ModelAdmin):
    list_display = ("title", "date")
    search_fields = ("title",)
    list_filter = ("date",)

@admin.register(InvestorDocument)
class InvestorDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "published_at")
    list_filter = ("kind",)
    search_fields = ("name",)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "department")
    list_filter = ("department",)
    search_fields = ("name", "role")
