from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone
from .models import AssetCategory, Asset, Depreciation, Maintenance, AssetTransfer, AssetDisposal
from .forms import AssetForm, AssetCategoryForm, DepreciationForm, MaintenanceForm, AssetTransferForm, AssetDisposalForm

@login_required
def asset_list(request):
    assets = Asset.objects.all()
    categories = AssetCategory.objects.all()
    context = {
        'assets': assets,
        'categories': categories,
    }
    return render(request, 'asset_management/asset_list.html', context)

@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    depreciations = Depreciation.objects.filter(asset=asset)
    maintenances = Maintenance.objects.filter(asset=asset)
    transfers = AssetTransfer.objects.filter(asset=asset)
    context = {
        'asset': asset,
        'depreciations': depreciations,
        'maintenances': maintenances,
        'transfers': transfers,
    }
    return render(request, 'asset_management/asset_detail.html', context)

@login_required
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            messages.success(request, 'Varlık başarıyla oluşturuldu.')
            return redirect('asset_detail', pk=asset.pk)
    else:
        form = AssetForm()
    return render(request, 'asset_management/asset_form.html', {'form': form})

@login_required
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save()
            messages.success(request, 'Varlık başarıyla güncellendi.')
            return redirect('asset_detail', pk=asset.pk)
    else:
        form = AssetForm(instance=asset)
    return render(request, 'asset_management/asset_form.html', {'form': form})

@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Varlık başarıyla silindi.')
        return redirect('asset_list')
    return render(request, 'asset_management/asset_confirm_delete.html', {'asset': asset})

@login_required
def depreciation_create(request, asset_pk):
    asset = get_object_or_404(Asset, pk=asset_pk)
    if request.method == 'POST':
        form = DepreciationForm(request.POST)
        if form.is_valid():
            depreciation = form.save(commit=False)
            depreciation.asset = asset
            depreciation.save()
            messages.success(request, 'Amortisman kaydı başarıyla oluşturuldu.')
            return redirect('asset_detail', pk=asset_pk)
    else:
        form = DepreciationForm()
    return render(request, 'asset_management/depreciation_form.html', {'form': form, 'asset': asset})

@login_required
def maintenance_create(request, asset_pk):
    asset = get_object_or_404(Asset, pk=asset_pk)
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.asset = asset
            maintenance.save()
            messages.success(request, 'Bakım kaydı başarıyla oluşturuldu.')
            return redirect('asset_detail', pk=asset_pk)
    else:
        form = MaintenanceForm()
    return render(request, 'asset_management/maintenance_form.html', {'form': form, 'asset': asset})

@login_required
def asset_transfer_create(request, asset_pk):
    asset = get_object_or_404(Asset, pk=asset_pk)
    if request.method == 'POST':
        form = AssetTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.asset = asset
            transfer.save()
            messages.success(request, 'Transfer kaydı başarıyla oluşturuldu.')
            return redirect('asset_detail', pk=asset_pk)
    else:
        form = AssetTransferForm()
    return render(request, 'asset_management/transfer_form.html', {'form': form, 'asset': asset})

@login_required
def asset_disposal_create(request, asset_pk):
    asset = get_object_or_404(Asset, pk=asset_pk)
    if request.method == 'POST':
        form = AssetDisposalForm(request.POST)
        if form.is_valid():
            disposal = form.save(commit=False)
            disposal.asset = asset
            disposal.save()
            messages.success(request, 'İmha kaydı başarıyla oluşturuldu.')
            return redirect('asset_detail', pk=asset_pk)
    else:
        form = AssetDisposalForm()
    return render(request, 'asset_management/disposal_form.html', {'form': form, 'asset': asset})

@login_required
def asset_dashboard(request):
    total_assets = Asset.objects.count()
    total_value = Asset.objects.aggregate(total=Sum('current_value'))['total'] or 0
    pending_maintenances = Maintenance.objects.filter(status='PENDING').count()
    recent_transfers = AssetTransfer.objects.order_by('-transfer_date')[:5]
    context = {
        'total_assets': total_assets,
        'total_value': total_value,
        'pending_maintenances': pending_maintenances,
        'recent_transfers': recent_transfers,
    }
    return render(request, 'asset_management/dashboard.html', context)
