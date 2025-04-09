from django.contrib import admin
from .models import VirtualCompany

@admin.register(VirtualCompany)
class VirtualCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'created_at', 'capital')
    list_filter = ('created_at',)
    search_fields = ('company_name', 'user__username') 