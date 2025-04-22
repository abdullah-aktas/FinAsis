from django.contrib import admin
from .models import AssetCategory, Asset, Depreciation, Maintenance, AssetTransfer, AssetDisposal

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('created_at',)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'purchase_date', 'purchase_cost', 'current_value', 'status')
    search_fields = ('name', 'code', 'serial_number')
    list_filter = ('category', 'status', 'purchase_date')
    date_hierarchy = 'purchase_date'

@admin.register(Depreciation)
class DepreciationAdmin(admin.ModelAdmin):
    list_display = ('asset', 'depreciation_date', 'amount', 'remaining_value')
    search_fields = ('asset__name', 'asset__code')
    list_filter = ('depreciation_date',)
    date_hierarchy = 'depreciation_date'

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('asset', 'maintenance_date', 'maintenance_type', 'cost', 'status')
    search_fields = ('asset__name', 'asset__code', 'description')
    list_filter = ('maintenance_type', 'status', 'maintenance_date')
    date_hierarchy = 'maintenance_date'

@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ('asset', 'from_location', 'to_location', 'transfer_date', 'status')
    search_fields = ('asset__name', 'asset__code', 'from_location', 'to_location')
    list_filter = ('status', 'transfer_date')
    date_hierarchy = 'transfer_date'

@admin.register(AssetDisposal)
class AssetDisposalAdmin(admin.ModelAdmin):
    list_display = ('asset', 'disposal_date', 'disposal_type', 'disposal_value', 'status')
    search_fields = ('asset__name', 'asset__code', 'reason')
    list_filter = ('disposal_type', 'status', 'disposal_date')
    date_hierarchy = 'disposal_date'
