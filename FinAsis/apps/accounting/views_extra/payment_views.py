from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Payment
from ..forms import PaymentForm

def payment_list(request: HttpRequest) -> HttpResponse:
    payments = Payment.objects.filter(is_active=True)
    return render(request, 'accounting/payment_list.html', {'payments': payments})

def payment_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounting:payment_list')
    else:
        form = PaymentForm()
    return render(request, 'accounting/payment_form.html', {'form': form})

def payment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'accounting/payment_detail.html', {'payment': payment})

def payment_update(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('accounting:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'accounting/payment_form.html', {'form': form, 'payment': payment})

def payment_delete(request: HttpRequest, pk: int) -> HttpResponse:
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        return redirect('accounting:payment_list')
    return render(request, 'accounting/payment_confirm_delete.html', {'payment': payment}) 