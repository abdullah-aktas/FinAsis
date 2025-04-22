from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Warehouse, Product, Stock, StockMovement, StockCount, StockCountItem
from .forms import WarehouseForm, ProductForm, StockForm, StockMovementForm, StockCountForm, StockCountItemForm

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
