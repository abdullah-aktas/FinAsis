from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Customer
from ..forms import CustomerForm

def customer_list(request: HttpRequest) -> HttpResponse:
    customers = Customer.objects.filter(is_active=True)
    return render(request, 'accounting/customer_list.html', {'customers': customers})

def customer_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounting:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'accounting/customer_form.html', {'form': form})

def customer_detail(request: HttpRequest, pk: int) -> HttpResponse:
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'accounting/customer_detail.html', {'customer': customer})

def customer_update(request: HttpRequest, pk: int) -> HttpResponse:
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('accounting:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'accounting/customer_form.html', {'form': form, 'customer': customer})

def customer_delete(request: HttpRequest, pk: int) -> HttpResponse:
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('accounting:customer_list')
    return render(request, 'accounting/customer_confirm_delete.html', {'customer': customer}) 