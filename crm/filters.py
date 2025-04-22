import django_filters
from django.db.models import Q
from django.utils import timezone
from .models import (
    Customer, Contact, Opportunity, Activity,
    Document, Communication, Note
)

class CustomerFilter(django_filters.FilterSet):
    """Müşteri filtreleri"""
    search = django_filters.CharFilter(method='search_filter')
    risk_level = django_filters.MultipleChoiceFilter(choices=Customer.RISK_LEVEL_CHOICES)
    industry = django_filters.MultipleChoiceFilter(choices=Customer.INDUSTRY_CHOICES)
    credit_score_min = django_filters.NumberFilter(field_name='credit_score', lookup_expr='gte')
    credit_score_max = django_filters.NumberFilter(field_name='credit_score', lookup_expr='lte')
    annual_revenue_min = django_filters.NumberFilter(field_name='annual_revenue', lookup_expr='gte')
    annual_revenue_max = django_filters.NumberFilter(field_name='annual_revenue', lookup_expr='lte')
    employee_count_min = django_filters.NumberFilter(field_name='employee_count', lookup_expr='gte')
    employee_count_max = django_filters.NumberFilter(field_name='employee_count', lookup_expr='lte')
    has_opportunities = django_filters.BooleanFilter(method='filter_has_opportunities')
    has_overdue_activities = django_filters.BooleanFilter(method='filter_has_overdue_activities')
    last_activity_days = django_filters.NumberFilter(method='filter_last_activity_days')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Customer
        fields = {
            'company_name': ['exact', 'icontains'],
            'tax_number': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(company_name__icontains=value) |
            Q(tax_number__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value)
        )

    def filter_has_opportunities(self, queryset, name, value):
        if value:
            return queryset.filter(opportunities__isnull=False).distinct()
        return queryset.filter(opportunities__isnull=True).distinct()

    def filter_has_overdue_activities(self, queryset, name, value):
        if value:
            return queryset.filter(
                opportunities__activities__completed=False,
                opportunities__activities__due_date__lt=timezone.now()
            ).distinct()
        return queryset.exclude(
            opportunities__activities__completed=False,
            opportunities__activities__due_date__lt=timezone.now()
        ).distinct()

    def filter_last_activity_days(self, queryset, name, value):
        date = timezone.now() - timezone.timedelta(days=value)
        return queryset.filter(
            opportunities__activities__created_at__gte=date
        ).distinct()

class ContactFilter(django_filters.FilterSet):
    """İletişim kişisi filtreleri"""
    search = django_filters.CharFilter(method='search_filter')
    position = django_filters.MultipleChoiceFilter(choices=Contact.POSITION_CHOICES)
    department = django_filters.MultipleChoiceFilter(choices=Contact.DEPARTMENT_CHOICES)
    is_primary = django_filters.BooleanFilter()
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())

    class Meta:
        model = Contact
        fields = {
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'mobile': ['exact', 'icontains'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value) |
            Q(mobile__icontains=value)
        )

class OpportunityFilter(django_filters.FilterSet):
    """Fırsat filtreleri"""
    search = django_filters.CharFilter(method='search_filter')
    stage = django_filters.MultipleChoiceFilter(choices=Opportunity.STAGE_CHOICES)
    probability_min = django_filters.NumberFilter(field_name='probability', lookup_expr='gte')
    probability_max = django_filters.NumberFilter(field_name='probability', lookup_expr='lte')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    expected_close_date_min = django_filters.DateFilter(field_name='expected_close_date', lookup_expr='gte')
    expected_close_date_max = django_filters.DateFilter(field_name='expected_close_date', lookup_expr='lte')
    actual_close_date_min = django_filters.DateFilter(field_name='actual_close_date', lookup_expr='gte')
    actual_close_date_max = django_filters.DateFilter(field_name='actual_close_date', lookup_expr='lte')
    has_overdue_activities = django_filters.BooleanFilter(method='filter_has_overdue_activities')
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    owner = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())

    class Meta:
        model = Opportunity
        fields = {
            'title': ['exact', 'icontains'],
            'description': ['icontains'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(customer__company_name__icontains=value)
        )

    def filter_has_overdue_activities(self, queryset, name, value):
        if value:
            return queryset.filter(
                activities__completed=False,
                activities__due_date__lt=timezone.now()
            ).distinct()
        return queryset.exclude(
            activities__completed=False,
            activities__due_date__lt=timezone.now()
        ).distinct()

class ActivityFilter(django_filters.FilterSet):
    """Aktivite filtreleri"""
    search = django_filters.CharFilter(method='search_filter')
    type = django_filters.MultipleChoiceFilter(choices=Activity.TYPE_CHOICES)
    completed = django_filters.BooleanFilter()
    overdue = django_filters.BooleanFilter(method='filter_overdue')
    due_date_min = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='gte')
    due_date_max = django_filters.DateTimeFilter(field_name='due_date', lookup_expr='lte')
    completed_at_min = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_at_max = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    opportunity = django_filters.ModelChoiceFilter(queryset=Opportunity.objects.all())
    assigned_to = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())

    class Meta:
        model = Activity
        fields = {
            'subject': ['exact', 'icontains'],
            'description': ['icontains'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(subject__icontains=value) |
            Q(description__icontains=value) |
            Q(opportunity__title__icontains=value) |
            Q(opportunity__customer__company_name__icontains=value)
        )

    def filter_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(
                completed=False,
                due_date__lt=timezone.now()
            )
        return queryset.exclude(
            completed=False,
            due_date__lt=timezone.now()
        )

class DocumentFilter(django_filters.FilterSet):
    """Doküman filtreleri"""
    search = django_filters.CharFilter(method='search_filter')
    type = django_filters.MultipleChoiceFilter(choices=Document.TYPE_CHOICES)
    file_size_min = django_filters.NumberFilter(method='filter_file_size_min')
    file_size_max = django_filters.NumberFilter(method='filter_file_size_max')
    file_extension = django_filters.CharFilter(method='filter_file_extension')
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    uploaded_by = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())

    class Meta:
        model = Document
        fields = {
            'title': ['exact', 'icontains'],
            'description': ['icontains'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(customer__company_name__icontains=value)
        )

    def filter_file_size_min(self, queryset, name, value):
        return queryset.filter(file__size__gte=value)

    def filter_file_size_max(self, queryset, name, value):
        return queryset.filter(file__size__lte=value)

    def filter_file_extension(self, queryset, name, value):
        return queryset.filter(file__iendswith=f'.{value.lower()}')

class CommunicationFilter(django_filters.FilterSet):
    """İletişim kaydı filtreleri"""
    search = django_filters.CharFilter(method='search_filter')
    type = django_filters.MultipleChoiceFilter(choices=Communication.TYPE_CHOICES)
    direction = django_filters.MultipleChoiceFilter(choices=Communication.DIRECTION_CHOICES)
    status = django_filters.MultipleChoiceFilter(choices=Communication.STATUS_CHOICES)
    duration_min = django_filters.DurationFilter(field_name='duration', lookup_expr='gte')
    duration_max = django_filters.DurationFilter(field_name='duration', lookup_expr='lte')
    customer = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())
    contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all())
    created_by = django_filters.ModelChoiceFilter(queryset=Customer.objects.all())

    class Meta:
        model = Communication
        fields = {
            'subject': ['exact', 'icontains'],
            'content': ['icontains'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(subject__icontains=value) |
            Q(content__icontains=value) |
            Q(customer__company_name__icontains=value) |
            Q(contact__first_name__icontains=value) |
            Q(contact__last_name__icontains=value)
        ) 