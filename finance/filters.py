# -*- coding: utf-8 -*-
import django_filters
from django.utils.translation import gettext_lazy as _
from .models import Account, Transaction, Budget, FinancialReport, Tax

class AccountFilter(django_filters.FilterSet):
    """Hesap filtreleri"""
    search = django_filters.CharFilter(method='search_filter', label=_('Arama'))
    type = django_filters.ChoiceFilter(choices=Account.TYPE_CHOICES, label=_('Hesap Tipi'))
    currency = django_filters.CharFilter(label=_('Para Birimi'))
    min_balance = django_filters.NumberFilter(field_name='balance', lookup_expr='gte', label=_('Min. Bakiye'))
    max_balance = django_filters.NumberFilter(field_name='balance', lookup_expr='lte', label=_('Max. Bakiye'))
    
    class Meta:
        model = Account
        fields = ['type', 'currency', 'is_active']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )

class TransactionFilter(django_filters.FilterSet):
    """İşlem filtreleri"""
    search = django_filters.CharFilter(method='search_filter', label=_('Arama'))
    account = django_filters.ModelChoiceFilter(queryset=Account.objects.all(), label=_('Hesap'))
    type = django_filters.ChoiceFilter(choices=Transaction.TYPE_CHOICES, label=_('İşlem Tipi'))
    status = django_filters.ChoiceFilter(choices=Transaction.STATUS_CHOICES, label=_('Durum'))
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label=_('Min. Tutar'))
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label=_('Max. Tutar'))
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte', label=_('Başlangıç Tarihi'))
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte', label=_('Bitiş Tarihi'))
    
    class Meta:
        model = Transaction
        fields = ['account', 'type', 'status', 'date']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(description__icontains=value) |
            Q(reference__icontains=value)
        )

class BudgetFilter(django_filters.FilterSet):
    """Bütçe filtreleri"""
    search = django_filters.CharFilter(method='search_filter', label=_('Arama'))
    category = django_filters.CharFilter(label=_('Kategori'))
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte', label=_('Min. Tutar'))
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte', label=_('Max. Tutar'))
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', label=_('Başlangıç Tarihi'))
    end_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', label=_('Bitiş Tarihi'))
    
    class Meta:
        model = Budget
        fields = ['category', 'is_active']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

class FinancialReportFilter(django_filters.FilterSet):
    """Finansal rapor filtreleri"""
    search = django_filters.CharFilter(method='search_filter', label=_('Arama'))
    type = django_filters.ChoiceFilter(choices=FinancialReport.TYPE_CHOICES, label=_('Rapor Tipi'))
    status = django_filters.ChoiceFilter(choices=FinancialReport.STATUS_CHOICES, label=_('Durum'))
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', label=_('Başlangıç Tarihi'))
    end_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', label=_('Bitiş Tarihi'))
    
    class Meta:
        model = FinancialReport
        fields = ['type', 'status']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )

class TaxFilter(django_filters.FilterSet):
    """Vergi filtreleri"""
    search = django_filters.CharFilter(method='search_filter', label=_('Arama'))
    type = django_filters.ChoiceFilter(choices=Tax.TYPE_CHOICES, label=_('Vergi Tipi'))
    min_rate = django_filters.NumberFilter(field_name='rate', lookup_expr='gte', label=_('Min. Oran'))
    max_rate = django_filters.NumberFilter(field_name='rate', lookup_expr='lte', label=_('Max. Oran'))
    
    class Meta:
        model = Tax
        fields = ['type', 'is_active']
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        ) 