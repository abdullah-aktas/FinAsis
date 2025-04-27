from django.contrib import admin
from .models import VirtualCompany, Product

@admin.register(VirtualCompany)
class VirtualCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'price', 'stock', 'created_at', 'updated_at')
    list_filter = ('company', 'created_at')
    search_fields = ('name', 'description')
