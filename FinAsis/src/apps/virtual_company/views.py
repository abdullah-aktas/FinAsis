# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VirtualCompany, Product
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django import forms
from .serializers import VirtualCompanySerializer, ProductSerializer, ARAccountingEntrySerializer, ARCompanySerializer, ARProductSerializer
from django.db.models import Sum
from rest_framework.permissions import BasePermission
from typing import Any
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView

class IsOwnerOrAdmin(BasePermission):
    """
    Sadece şirket sahibi veya admin erişebilir.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.owner == request.user

class VirtualCompanyViewSet(viewsets.ModelViewSet):
    """
    Sanal şirket view seti. Sadece sahibi kendi şirketlerini görebilir.
    Filtering, ordering ve search desteği vardır.
    """
    queryset = VirtualCompany.objects.all()
    serializer_class = VirtualCompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'balance']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return VirtualCompany.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer: VirtualCompanySerializer) -> None:
        instance = serializer.save(owner=self.request.user)
        print(f"AUDIT: {self.request.user} yeni bir şirket oluşturdu: {instance.name}")

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        company = self.get_object()
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(company=company)
            print(f"AUDIT: {request.user} {company} şirketine ürün ekledi: {product.name}")
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        company = self.get_object()
        products = company.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def total_inventory_value(self, request, pk=None):
        company = self.get_object()
        total_value = sum([p.price * p.stock for p in company.products.all()])
        return Response({'total_inventory_value': total_value})

    @action(detail=True, methods=['get'])
    def financial_report(self, request, pk=None):
        """
        Şirketin toplam stok değeri, toplam gelir, toplam gider ve kârlılık oranı raporu.
        """
        company = self.get_object()
        # Toplam stok değeri
        total_stock_value = sum([p.price * p.stock for p in company.products.all()])
        # Toplam gelir ve gider
        transactions = getattr(company, 'transactions', None)
        total_income = 0
        total_expense = 0
        if transactions:
            total_income = sum([t.amount for t in transactions.filter(transaction_type='INCOME')])
            total_expense = sum([t.amount for t in transactions.filter(transaction_type='EXPENSE')])
        # Kârlılık oranı
        profit = total_income - total_expense
        profit_rate = (profit / total_income * 100) if total_income > 0 else 0
        return Response({
            'total_stock_value': total_stock_value,
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': profit,
            'profit_rate': profit_rate
        })

class ProductViewSet(viewsets.ModelViewSet):
    """
    Ürün view seti. Sadece kullanıcının sahip olduğu şirketlerin ürünlerini görebilir.
    Filtering, ordering ve search desteği vardır.
    Ürün eklerken stok veya fiyat negatifse, kullanıcı dostu hata mesajı döner.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'price', 'stock']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)
    
    def perform_create(self, serializer: ProductSerializer) -> None:
        data = serializer.validated_data
        if data['price'] < 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'price': [_('Fiyat negatif olamaz.')]} )
        if data['stock'] < 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'stock': [_('Stok negatif olamaz.')]} )
        company = VirtualCompany.objects.get(owner=self.request.user)
        product = serializer.save(company=company)
        print(f"AUDIT: {self.request.user} yeni ürün ekledi: {product.name}")

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Birden fazla ürünü tek seferde ekler.
        """
        items = request.data.get('items', [])
        errors = []
        created = []
        company = VirtualCompany.objects.get(owner=request.user)
        for item in items:
            serializer = ProductSerializer(data=item)
            if serializer.is_valid():
                data = serializer.validated_data
                if data['price'] < 0 or data['stock'] < 0:
                    errors.append({'item': item, 'error': _('Fiyat veya stok negatif olamaz.')})
                    continue
                product = serializer.save(company=company)
                created.append(ProductSerializer(product).data)
            else:
                errors.append({'item': item, 'error': serializer.errors})
        if errors:
            return Response({'created': created, 'errors': errors}, status=400)
        return Response({'created': created}, status=201)

class ARAccountingEntryCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ARAccountingEntrySerializer(data=request.data)
        if serializer.is_valid():
            entry = serializer.save(student=request.user)
            entry.apply_effect()  # Bakiyeye etkiyi uygula
            return Response({'success': True, 'entry_id': entry.id})
        return Response(serializer.errors, status=400)

class ARCompanyListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        companies = VirtualCompany.objects.filter(owner=request.user)
        serializer = ARCompanySerializer(companies, many=True)
        return Response(serializer.data)

class ARProductByMarkerAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, marker_id):
        try:
            product = Product.objects.get(marker_id=marker_id)
            serializer = ARProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Ürün bulunamadı'}, status=404)

# -------------------- Web (HTML) Views --------------------

class VirtualCompanyForm(forms.ModelForm):
    class Meta:
        model = VirtualCompany
        fields = ['name', 'description', 'balance']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['company', 'name', 'description', 'price', 'stock', 'marker_id']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            field = self.fields.get('company')
            if field:  # type: ignore
                # type: ignore below: django dynamic attribute
                field.queryset = VirtualCompany.objects.filter(owner=user)  # type: ignore[attr-defined]

class OwnerQuerysetMixin:
    """Mixin: yalnızca giriş yapan kullanıcının sahip olduğu VirtualCompany kayıtlarını döndür."""
    def get_queryset(self):  # type: ignore
        try:
            qs = super().get_queryset()  # type: ignore
        except AttributeError:
            qs = VirtualCompany.objects.all()
        user = getattr(self.request, 'user', None)  # type: ignore
        if user and user.is_authenticated:
            return qs.filter(owner=user)
        return qs.none()

class VirtualCompanyListView(OwnerQuerysetMixin, ListView):
    model = VirtualCompany
    template_name = 'virtual_company/virtual_company_list.html'
    context_object_name = 'object_list'
    def get_queryset(self):  # type: ignore
        base_qs = super().get_queryset()
        value_expr = ExpressionWrapper(
            F('products__price') * F('products__stock'),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        )
        return base_qs.prefetch_related('products').annotate(
            total_inventory_annotated=Sum(value_expr)
        )
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        companies = ctx.get('object_list', [])
        total_balance = sum((c.balance for c in companies), start=0)
        # Annotated alan varsa onu kullan, yoksa fallback hesapla
        if companies and hasattr(companies[0], 'total_inventory_annotated'):
            total_inventory = sum((c.total_inventory_annotated or 0 for c in companies), start=0)
        else:
            total_inventory = sum(
                (sum(p.price * p.stock for p in c.products.all()) for c in companies),
                start=0
            )
        ctx.update({
            'title': 'Sanal Şirketler',
            'company_count': len(companies),
            'total_balance': total_balance,
            'total_inventory_value': total_inventory,
        })
        return ctx

class VirtualCompanyDetailView(OwnerQuerysetMixin, DetailView):
    model = VirtualCompany
    template_name = 'virtual_company/virtual_company_detail.html'

class VirtualCompanyCreateView(CreateView):
    model = VirtualCompany
    form_class = VirtualCompanyForm
    template_name = 'virtual_company/virtual_company_form.html'
    success_url = reverse_lazy('virtual_company:virtual_company_list')
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class VirtualCompanyUpdateView(OwnerQuerysetMixin, UpdateView):
    model = VirtualCompany
    form_class = VirtualCompanyForm
    template_name = 'virtual_company/virtual_company_form.html'
    success_url = reverse_lazy('virtual_company:virtual_company_list')

class VirtualCompanyDeleteView(OwnerQuerysetMixin, DeleteView):
    model = VirtualCompany
    template_name = 'virtual_company/virtual_company_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:virtual_company_list')

class ProductListView(ListView):
    model = Product
    template_name = 'virtual_company/product_list.html'
    context_object_name = 'object_list'
    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'virtual_company/product_form.html'
    success_url = reverse_lazy('virtual_company:product_list')
    def form_valid(self, form):
        if not form.cleaned_data.get('company'):
            form.add_error('company', 'Bir şirket seçmelisiniz.')
            return self.form_invalid(form)
        return super().form_valid(form)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'virtual_company/product_form.html'
    success_url = reverse_lazy('virtual_company:product_list')
    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'virtual_company/product_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:product_list')
    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)
