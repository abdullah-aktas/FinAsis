import django_tables2 as tables
from .models import Asset, Maintenance, AssetRental

class AssetTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='asset_management/asset_actions.html',
        orderable=False,
        verbose_name='İşlemler'
    )
    
    class Meta:
        model = Asset
        template_name = "django_tables2/bootstrap4.html"
        fields = [
            'name', 'code', 'category', 'status',
            'current_value', 'location', 'assigned_to',
            'purchase_date', 'actions'
        ]
        attrs = {
            'class': 'table table-striped table-bordered',
            'thead': {
                'class': 'thead-dark'
            }
        }

class MaintenanceTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='asset_management/maintenance_actions.html',
        orderable=False,
        verbose_name='İşlemler'
    )
    
    class Meta:
        model = Maintenance
        template_name = "django_tables2/bootstrap4.html"
        fields = [
            'asset', 'maintenance_type', 'status',
            'maintenance_date', 'next_maintenance_date',
            'cost', 'performed_by', 'actions'
        ]
        attrs = {
            'class': 'table table-striped table-bordered',
            'thead': {
                'class': 'thead-dark'
            }
        }

class AssetRentalTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='asset_management/rental_actions.html',
        orderable=False,
        verbose_name='İşlemler'
    )
    
    class Meta:
        model = AssetRental
        template_name = "django_tables2/bootstrap4.html"
        fields = [
            'asset', 'renter', 'start_date', 'end_date',
            'rental_fee', 'status', 'actions'
        ]
        attrs = {
            'class': 'table table-striped table-bordered',
            'thead': {
                'class': 'thead-dark'
            }
        } 