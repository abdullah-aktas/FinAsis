from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import VendorPayment
from ..forms import VendorPaymentForm

def vendor_payment_list(request: HttpRequest) -> HttpResponse:
    payments = VendorPayment.objects.filter(is_active=True)
    return render(request, 'accounting/vendor_payment_list.html', {'payments': payments})

def vendor_payment_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = VendorPaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounting:vendor_payment_list')
    else:
        form = VendorPaymentForm()
    return render(request, 'accounting/vendor_payment_form.html', {'form': form})

def vendor_payment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(VendorPayment, pk=pk)
    return render(request, 'accounting/vendor_payment_detail.html', {'payment': payment})

def vendor_payment_update(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(VendorPayment, pk=pk)
    if request.method == 'POST':
        form = VendorPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('accounting:vendor_payment_detail', pk=payment.pk)
    else:
        form = VendorPaymentForm(instance=payment)
    return render(request, 'accounting/vendor_payment_form.html', {'form': form, 'payment': payment})

def vendor_payment_delete(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(VendorPayment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        return redirect('accounting:vendor_payment_list')
    return render(request, 'accounting/vendor_payment_confirm_delete.html', {'payment': payment})


