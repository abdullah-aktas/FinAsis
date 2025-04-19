from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg
from apps.invoice.models import Invoice, InvoiceItem
from apps.customer.models import Customer
from apps.product.models import Product

@login_required
def pivot_table_view(request):
    """Pivot tablo ana görünümü"""
    context = {
        'modules': [
            {'id': 'invoice', 'name': 'Faturalar'},
            {'id': 'customer', 'name': 'Müşteriler'},
            {'id': 'product', 'name': 'Ürünler'},
            {'id': 'stock', 'name': 'Stok'},
            {'id': 'cash', 'name': 'Kasa'},
            {'id': 'bank', 'name': 'Banka'}
        ]
    }
    return render(request, 'analytics/pivot_table.html', context)

@login_required
def get_pivot_data(request):
    """Pivot tablo verilerini hazırlayan API endpoint"""
    module = request.GET.get('module')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if module == 'invoice':
        data = prepare_invoice_pivot(start_date, end_date)
    elif module == 'customer':
        data = prepare_customer_pivot(start_date, end_date)
    elif module == 'product':
        data = prepare_product_pivot(start_date, end_date)
    else:
        data = []
    
    return JsonResponse({'data': data})

def prepare_invoice_pivot(start_date, end_date):
    """Fatura verilerini pivot formatına dönüştür"""
    invoices = Invoice.objects.filter(
        date__range=[start_date, end_date]
    ).values('date', 'customer__name', 'type').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    df = pd.DataFrame(invoices)
    pivot = pd.pivot_table(
        df,
        values=['total', 'count'],
        index=['date', 'customer__name'],
        columns=['type'],
        aggfunc={'total': 'sum', 'count': 'sum'}
    ).reset_index()
    
    return pivot.to_dict('records')

def prepare_customer_pivot(start_date, end_date):
    """Müşteri verilerini pivot formatına dönüştür"""
    customers = Customer.objects.all()
    data = []
    
    for customer in customers:
        invoices = Invoice.objects.filter(
            customer=customer,
            date__range=[start_date, end_date]
        )
        
        data.append({
            'customer': customer.name,
            'total_invoices': invoices.count(),
            'total_amount': invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'avg_invoice_amount': invoices.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        })
    
    return data

def prepare_product_pivot(start_date, end_date):
    """Ürün verilerini pivot formatına dönüştür"""
    products = Product.objects.all()
    data = []
    
    for product in products:
        invoice_items = InvoiceItem.objects.filter(
            product=product,
            invoice__date__range=[start_date, end_date]
        )
        
        data.append({
            'product': product.name,
            'total_quantity': invoice_items.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'total_amount': invoice_items.aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'avg_price': invoice_items.aggregate(Avg('unit_price'))['unit_price__avg'] or 0
        })
    
    return data 