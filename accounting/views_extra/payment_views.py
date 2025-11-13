from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Payment, AuditLog
from ..forms import PaymentForm
from django.utils import timezone

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
    # Basit onay akışı
    if request.method == 'POST' and request.POST.get('action') == 'approve' and not payment.approved:
        payment.approved = True
        payment.approved_by = request.user if request.user.is_authenticated else None
        payment.approved_at = timezone.now()
        payment.save()
        # Audit log
        try:
            AuditLog.objects.create(
                company=payment.company,
                actor=request.user if request.user.is_authenticated else None,
                action='PAYMENT_APPROVE',
                entity='Payment',
                entity_id=str(payment.pk),
                metadata={'amount': str(payment.amount), 'method': payment.payment_method}
            )
        except Exception:
            pass
        return redirect('accounting:payment_detail', pk=payment.pk)
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