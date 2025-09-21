from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Vendor
from ..forms import VendorForm

def vendor_list(request: HttpRequest) -> HttpResponse:
    vendors = Vendor.objects.filter(is_active=True)
    return render(request, 'accounting/vendor_list.html', {'vendors': vendors})

def vendor_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounting:vendor_list')
    else:
        form = VendorForm()
    return render(request, 'accounting/vendor_form.html', {'form': form})

def vendor_detail(request: HttpRequest, pk: int) -> HttpResponse:
    vendor = get_object_or_404(Vendor, pk=pk)
    return render(request, 'accounting/vendor_detail.html', {'vendor': vendor})

def vendor_update(request: HttpRequest, pk: int) -> HttpResponse:
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('accounting:vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'accounting/vendor_form.html', {'form': form, 'vendor': vendor})

def vendor_delete(request: HttpRequest, pk: int) -> HttpResponse:
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        return redirect('accounting:vendor_list')
    return render(request, 'accounting/vendor_confirm_delete.html', {'vendor': vendor})


