from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import PurchaseInvoice
from ..forms import PurchaseInvoiceForm


def purchase_invoice_list(request: HttpRequest) -> HttpResponse:
    invoices = PurchaseInvoice.objects.filter(is_active=True)
    return render(
        request, "accounting/purchase_invoice_list.html", {"invoices": invoices}
    )


def purchase_invoice_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:purchase_invoice_list")
    else:
        form = PurchaseInvoiceForm()
    return render(request, "accounting/purchase_invoice_form.html", {"form": form})


def purchase_invoice_detail(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    return render(
        request, "accounting/purchase_invoice_detail.html", {"invoice": invoice}
    )


def purchase_invoice_update(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    if request.method == "POST":
        form = PurchaseInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect("accounting:purchase_invoice_detail", pk=invoice.pk)
    else:
        form = PurchaseInvoiceForm(instance=invoice)
    return render(
        request,
        "accounting/purchase_invoice_form.html",
        {"form": form, "invoice": invoice},
    )


def purchase_invoice_delete(request: HttpRequest, pk: int) -> HttpResponse:
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    if request.method == "POST":
        invoice.delete()
        return redirect("accounting:purchase_invoice_list")
    return render(
        request, "accounting/purchase_invoice_confirm_delete.html", {"invoice": invoice}
    )
