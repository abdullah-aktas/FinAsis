from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Sale
from ..forms import SaleForm


def sale_list(request: HttpRequest) -> HttpResponse:
    sales = Sale.objects.filter(is_active=True)
    return render(request, "accounting/sale_list.html", {"sales": sales})


def sale_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:sale_list")
    else:
        form = SaleForm()
    return render(request, "accounting/sale_form.html", {"form": form})


def sale_detail(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, "accounting/sale_detail.html", {"sale": sale})


def sale_update(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect("accounting:sale_detail", pk=sale.pk)
    else:
        form = SaleForm(instance=sale)
    return render(request, "accounting/sale_form.html", {"form": form, "sale": sale})


def sale_delete(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        sale.delete()
        return redirect("accounting:sale_list")
    return render(request, "accounting/sale_confirm_delete.html", {"sale": sale})
