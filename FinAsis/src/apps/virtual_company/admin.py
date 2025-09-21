# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import VirtualCompany, Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'stock', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(VirtualCompany)
class VirtualCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'balance', 'created_at', 'updated_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    inlines = [ProductInline]
    readonly_fields = ('created_at', 'updated_at', 'balance')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'price', 'stock', 'created_at', 'updated_at')
    list_filter = ('company', 'created_at')
    search_fields = ('name', 'description', 'company__name')
    readonly_fields = ('created_at', 'updated_at')
