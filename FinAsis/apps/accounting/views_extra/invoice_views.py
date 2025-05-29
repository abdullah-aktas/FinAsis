from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Invoice
from ..forms import InvoiceForm
from ..services.efatura_service import send_invoice_to_gib, check_invoice_status, cancel_invoice_on_gib
from django.contrib import messages

def invoice_list(request: HttpRequest) -> HttpResponse:
    invoices = Invoice.objects.filter(is_active=True)
    return render(request, 'accounting/invoice_list.html', {'invoices': invoices})

def invoice_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounting:invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'accounting/invoice_form.html', {'form': form})

def invoice_detail(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'accounting/invoice_detail.html', {'invoice': invoice})

def invoice_update(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('accounting:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'accounting/invoice_form.html', {'form': form, 'invoice': invoice})

def invoice_delete(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('accounting:invoice_list')
    return render(request, 'accounting/invoice_confirm_delete.html', {'invoice': invoice})

def invoice_send_gib(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice, pk=pk)
    try:
        response = send_invoice_to_gib(invoice)
        if response.status_code == 200:
            messages.success(request, "Fatura GİB'e başarıyla gönderildi.")
        else:
            messages.error(request, f"GİB gönderim hatası: {response.text}")
    except Exception as e:
        messages.error(request, f"GİB gönderim istisnası: {str(e)}")
    return redirect('accounting:invoice_detail', pk=pk)

def invoice_check_gib_status(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice, pk=pk)
    try:
        response = check_invoice_status(invoice)
        messages.info(request, f"GİB Durumu: {invoice.gib_status} | Yanıt: {invoice.gib_response}")
    except Exception as e:
        messages.error(request, f"GİB durum sorgu istisnası: {str(e)}")
    return redirect('accounting:invoice_detail', pk=pk)

def invoice_cancel_gib(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(Invoice, pk=pk)
    try:
        response = cancel_invoice_on_gib(invoice)
        if response.status_code == 200:
            messages.success(request, "Fatura GİB'de iptal edildi.")
        else:
            messages.error(request, f"GİB iptal hatası: {response.text}")
    except Exception as e:
        messages.error(request, f"GİB iptal istisnası: {str(e)}")
    return redirect('accounting:invoice_detail', pk=pk) 