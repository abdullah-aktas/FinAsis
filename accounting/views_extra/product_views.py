from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Product
from ..forms import ProductForm


def product_list(request: HttpRequest) -> HttpResponse:
    products = Product.objects.filter(is_active=True)
    return render(request, "accounting/product_list.html", {"products": products})


def product_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:product_list")
    else:
        form = ProductForm()
    return render(request, "accounting/product_form.html", {"form": form})


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    return render(request, "accounting/product_detail.html", {"product": product})


def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("accounting:product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(
        request, "accounting/product_form.html", {"form": form, "product": product}
    )


def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("accounting:product_list")
    return render(
        request, "accounting/product_confirm_delete.html", {"product": product}
    )
