from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django_tables2 import SingleTableView
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    AssetCategory, Asset, Depreciation, Maintenance, 
    AssetTransfer, AssetDisposal, AssetRental
)
from .forms import (
    AssetForm, AssetCategoryForm, DepreciationForm, 
    MaintenanceForm, AssetTransferForm, AssetDisposalForm,
    AssetRentalForm
)
from .tables import AssetTable
from .filters import AssetFilter
from .serializers import (
    AssetSerializer, AssetCategorySerializer, 
    MaintenanceSerializer, AssetRentalSerializer
)

class AssetListView(LoginRequiredMixin, FilterView, SingleTableView):
    model = Asset
    table_class = AssetTable
    filterset_class = AssetFilter
    template_name = 'asset_management/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('category', 'assigned_to')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = AssetCategory.objects.all()
        return context

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'asset_management/asset_detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.get_object()
        context['depreciations'] = Depreciation.objects.filter(asset=asset)
        context['maintenances'] = Maintenance.objects.filter(asset=asset)
        context['transfers'] = AssetTransfer.objects.filter(asset=asset)
        context['rentals'] = AssetRental.objects.filter(asset=asset)
        return context

class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'asset_management/asset_form.html'
    success_url = reverse_lazy('asset_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Varlık başarıyla oluşturuldu.')
        return response

class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'asset_management/asset_form.html'
    success_url = reverse_lazy('asset_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Varlık başarıyla güncellendi.')
        return response

class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model = Asset
    template_name = 'asset_management/asset_confirm_delete.html'
    success_url = reverse_lazy('asset_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Varlık başarıyla silindi.')
        return response

class AssetDashboardView(LoginRequiredMixin, ListView):
    template_name = 'asset_management/dashboard.html'
    context_object_name = 'assets'

    def get_queryset(self):
        return Asset.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_assets'] = Asset.objects.count()
        context['total_value'] = Asset.objects.aggregate(
            total=Sum('current_value')
        )['total'] or 0
        context['pending_maintenances'] = Maintenance.objects.filter(
            status='PENDING'
        ).count()
        context['active_rentals'] = AssetRental.objects.filter(
            status='ACTIVE'
        ).count()
        context['recent_transfers'] = AssetTransfer.objects.order_by(
            '-transfer_date'
        )[:5]
        return context

# API Views
class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'serial_number']
    ordering_fields = ['name', 'purchase_date', 'current_value']

    @action(detail=True, methods=['post'])
    def create_maintenance(self, request, pk=None):
        asset = self.get_object()
        serializer = MaintenanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(asset=asset)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def create_rental(self, request, pk=None):
        asset = self.get_object()
        serializer = AssetRentalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(asset=asset)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'performed_by']
    ordering_fields = ['maintenance_date', 'cost']

class AssetRentalViewSet(viewsets.ModelViewSet):
    queryset = AssetRental.objects.all()
    serializer_class = AssetRentalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['notes']
    ordering_fields = ['start_date', 'end_date', 'rental_fee']
