import django_filters
from .models import Asset, Maintenance, AssetRental

class AssetFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    serial_number = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=lambda: AssetCategory.objects.all())
    status = django_filters.ChoiceFilter(choices=Asset.STATUS_CHOICES)
    min_value = django_filters.NumberFilter(field_name='current_value', lookup_expr='gte')
    max_value = django_filters.NumberFilter(field_name='current_value', lookup_expr='lte')
    purchase_date_after = django_filters.DateFilter(field_name='purchase_date', lookup_expr='gte')
    purchase_date_before = django_filters.DateFilter(field_name='purchase_date', lookup_expr='lte')
    assigned_to = django_filters.ModelChoiceFilter(queryset=lambda: settings.AUTH_USER_MODEL.objects.all())

    class Meta:
        model = Asset
        fields = [
            'name', 'code', 'serial_number', 'category',
            'status', 'min_value', 'max_value',
            'purchase_date_after', 'purchase_date_before',
            'assigned_to'
        ]

class MaintenanceFilter(django_filters.FilterSet):
    asset = django_filters.ModelChoiceFilter(queryset=lambda: Asset.objects.all())
    maintenance_type = django_filters.ChoiceFilter(choices=Maintenance.MAINTENANCE_TYPES)
    status = django_filters.ChoiceFilter(choices=Maintenance.STATUS_CHOICES)
    min_cost = django_filters.NumberFilter(field_name='cost', lookup_expr='gte')
    max_cost = django_filters.NumberFilter(field_name='cost', lookup_expr='lte')
    maintenance_date_after = django_filters.DateFilter(field_name='maintenance_date', lookup_expr='gte')
    maintenance_date_before = django_filters.DateFilter(field_name='maintenance_date', lookup_expr='lte')

    class Meta:
        model = Maintenance
        fields = [
            'asset', 'maintenance_type', 'status',
            'min_cost', 'max_cost', 'maintenance_date_after',
            'maintenance_date_before'
        ]

class AssetRentalFilter(django_filters.FilterSet):
    asset = django_filters.ModelChoiceFilter(queryset=lambda: Asset.objects.all())
    renter = django_filters.ModelChoiceFilter(queryset=lambda: settings.AUTH_USER_MODEL.objects.all())
    status = django_filters.ChoiceFilter(choices=AssetRental.STATUS_CHOICES)
    min_fee = django_filters.NumberFilter(field_name='rental_fee', lookup_expr='gte')
    max_fee = django_filters.NumberFilter(field_name='rental_fee', lookup_expr='lte')
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = AssetRental
        fields = [
            'asset', 'renter', 'status', 'min_fee',
            'max_fee', 'start_date_after', 'start_date_before',
            'end_date_after', 'end_date_before'
        ] 