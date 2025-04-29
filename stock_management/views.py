# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Warehouse, Product, Stock, StockMovement, StockCount, StockCountItem
from .forms import WarehouseForm, ProductForm, StockForm, StockMovementForm, StockCountForm, StockCountItemForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Category, StockAlert
from .forms import CategoryForm
from .utils import check_stock_alerts
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

# Create your views here.

# Warehouse Views
@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'stock_management/warehouse_list.html', {
        'warehouses': warehouses,
        'page_title': 'Depolar'
    })

@login_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'stock_management/warehouse_detail.html', {
        'warehouse': warehouse,
        'page_title': f'Depo: {warehouse.name}'
    })

@login_required
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, 'Depo başarıyla oluşturuldu.')
            return redirect('stock_management:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm()
    
    return render(request, 'stock_management/warehouse_form.html', {
        'form': form,
        'page_title': 'Yeni Depo Ekle'
    })

@login_required
def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Depo bilgileri güncellendi.')
            return redirect('stock_management:warehouse_detail', pk=warehouse.pk)
    else:
        form = WarehouseForm(instance=warehouse)
    
    return render(request, 'stock_management/warehouse_form.html', {
        'form': form,
        'warehouse': warehouse,
        'page_title': f'Depo Düzenle: {warehouse.name}'
    })

@login_required
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, 'Depo silindi.')
        return redirect('stock_management:warehouse_list')
    
    return render(request, 'stock_management/warehouse_confirm_delete.html', {
        'warehouse': warehouse,
        'page_title': f'Depo Sil: {warehouse.name}'
    })

# Diğer model view tanımları buraya eklenecek...

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'stock_management/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all()
        
        # Arama filtresi
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(barcode__icontains=search_query)
            )
        
        # Kategori filtresi
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Stok durumu filtresi
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'low':
            queryset = queryset.annotate(
                current_stock=Sum('stock_movements__quantity')
            ).filter(current_stock__lte=F('min_stock_level'))
        elif stock_status == 'high':
            queryset = queryset.annotate(
                current_stock=Sum('stock_movements__quantity')
            ).filter(current_stock__gte=F('max_stock_level'))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['stock_alerts'] = StockAlert.objects.filter(is_read=False)[:5]
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'stock_management/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Son stok hareketleri
        context['recent_movements'] = product.stock_movements.select_related(
            'created_by'
        ).order_by('-created_at')[:10]
        
        # Stok grafiği verileri
        context['stock_history'] = product.stock_movements.values(
            'created_at__date'
        ).annotate(
            total=Sum('quantity')
        ).order_by('created_at__date')
        
        return context

class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock_management/product_form.html'
    permission_required = 'stock_management.add_product'
    success_url = reverse_lazy('stock_management:product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ürün başarıyla oluşturuldu.')
        return response

class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock_management/product_form.html'
    permission_required = 'stock_management.change_product'
    success_url = reverse_lazy('stock_management:product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ürün başarıyla güncellendi.')
        return response

class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'stock_management/product_confirm_delete.html'
    permission_required = 'stock_management.delete_product'
    success_url = reverse_lazy('stock_management:product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ürün başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

class StockMovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'stock_management/stock_movement_form.html'

    def get_initial(self):
        initial = super().get_initial()
        product_id = self.request.GET.get('product')
        if product_id:
            initial['product'] = get_object_or_404(Product, id=product_id)
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Stok uyarılarını kontrol et
        check_stock_alerts(form.instance.product)
        
        messages.success(self.request, 'Stok hareketi başarıyla kaydedildi.')
        return response

    def get_success_url(self):
        return reverse_lazy('stock_management:product_detail', kwargs={'pk': self.object.product.id})

def stock_alert_list(request):
    if not request.user.has_perm('stock_management.view_stockalert'):
        raise PermissionDenied
    
    alerts = StockAlert.objects.select_related('product').order_by('-created_at')
    return render(request, 'stock_management/stock_alert_list.html', {'alerts': alerts})

def mark_alert_read(request, alert_id):
    if not request.user.has_perm('stock_management.change_stockalert'):
        raise PermissionDenied
    
    alert = get_object_or_404(StockAlert, id=alert_id)
    alert.is_read = True
    alert.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('stock_management:stock_alert_list')

def stock_report(request):
    if not request.user.has_perm('stock_management.view_stockreport'):
        raise PermissionDenied
    
    # Stok raporu verileri
    products = Product.objects.annotate(
        current_stock=Sum('stock_movements__quantity')
    ).filter(current_stock__isnull=False)
    
    # Düşük stoklu ürünler
    low_stock = products.filter(current_stock__lte=F('min_stock_level'))
    
    # Yüksek stoklu ürünler
    high_stock = products.filter(current_stock__gte=F('max_stock_level'))
    
    # Stok değeri
    total_value = sum(product.stock_value for product in products)
    
    context = {
        'products': products,
        'low_stock': low_stock,
        'high_stock': high_stock,
        'total_value': total_value,
    }
    
    return render(request, 'stock_management/stock_report.html', context)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'stock_management/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        queryset = Category.objects.all()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'stock_management/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        return context

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'stock_management/category_form.html'
    permission_required = 'stock_management.add_category'
    success_url = reverse_lazy('stock_management:category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Kategori başarıyla oluşturuldu.')
        return response

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'stock_management/category_form.html'
    permission_required = 'stock_management.change_category'
    success_url = reverse_lazy('stock_management:category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Kategori başarıyla güncellendi.')
        return response

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'stock_management/category_confirm_delete.html'
    permission_required = 'stock_management.delete_category'
    success_url = reverse_lazy('stock_management:category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Kategori başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'stock_management/stock_movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20

    def get_queryset(self):
        queryset = StockMovement.objects.select_related('product', 'created_by').all()
        
        # Ürün filtresi
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Hareket tipi filtresi
        movement_type = self.request.GET.get('type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        # Tarih aralığı filtresi
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        
        return queryset.order_by('-created_at')

class StockMovementDetailView(LoginRequiredMixin, DetailView):
    model = StockMovement
    template_name = 'stock_management/stock_movement_detail.html'
    context_object_name = 'movement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movement = self.get_object()
        context['product'] = movement.product
        context['created_by'] = movement.created_by
        return context

class ProductAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search)
            )
        return queryset

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class StockMovementAPIView(generics.ListCreateAPIView):
    queryset = StockMovement.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product', '')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class StockAlertAPIView(generics.ListAPIView):
    queryset = StockAlert.objects.filter(is_read=False)
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_stock_ajax(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 0)
    
    try:
        product = Product.objects.get(id=product_id)
        current_stock = product.current_stock
        is_available = current_stock >= quantity
        
        return JsonResponse({
            'success': True,
            'current_stock': current_stock,
            'is_available': is_available
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ürün bulunamadı'
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_autocomplete(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(sku__icontains=query) |
        Q(barcode__icontains=query)
    )[:10]
    
    results = [{
        'id': product.id,
        'text': f"{product.name} ({product.sku})",
        'stock': product.current_stock
    } for product in products]
    
    return JsonResponse({'results': results})

def movement_report(request):
    if not request.user.has_perm('stock_management.view_stockmovement'):
        raise PermissionDenied
    
    movements = StockMovement.objects.select_related('product', 'created_by')
    
    # Filtreler
    product_id = request.GET.get('product')
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        movements = movements.filter(created_at__range=[start_date, end_date])
    
    context = {
        'movements': movements,
        'products': Product.objects.all(),
        'movement_types': StockMovement.MOVEMENT_TYPES,
    }
    
    return render(request, 'stock_management/movement_report.html', context)
