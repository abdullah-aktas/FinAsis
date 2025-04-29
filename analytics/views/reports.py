# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from apps.invoice.models import Invoice, InvoiceItem
from apps.customer.models import Customer
from apps.product.models import Product
from datetime import datetime, timedelta

@login_required
def transaction_grid(request):
    """İşlem grid'i ana görünümü"""
    context = {
        'customers': Customer.objects.all(),
        'products': Product.objects.all(),
        'transaction_types': [
            {'id': 'income', 'name': 'Gelir'},
            {'id': 'expense', 'name': 'Gider'},
            {'id': 'collection', 'name': 'Tahsilat'},
            {'id': 'payment', 'name': 'Ödeme'}
        ]
    }
    return render(request, 'analytics/transaction_grid.html', context)

@login_required
def get_transactions(request):
    """HTMX ile işlem verilerini getiren endpoint"""
    # Filtreleme parametreleri
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    customer_id = request.GET.get('customer')
    product_id = request.GET.get('product')
    transaction_type = request.GET.get('type')
    search_query = request.GET.get('search')
    
    # Temel sorgu
    transactions = Invoice.objects.all()
    
    # Filtreleri uygula
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    
    if customer_id:
        transactions = transactions.filter(customer_id=customer_id)
    
    if product_id:
        transactions = transactions.filter(items__product_id=product_id)
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    
    if search_query:
        transactions = transactions.filter(
            Q(invoice_number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Sayfalama
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 25)
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'total_count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page
    }
    
    return render(request, 'analytics/partials/transaction_list.html', context)

@login_required
def export_transactions(request):
    """İşlem verilerini Excel/PDF olarak dışa aktar"""
    import pandas as pd
    from django.http import HttpResponse
    from datetime import datetime
    
    # Filtreleme parametrelerini al
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    export_format = request.GET.get('format', 'excel')
    
    # Verileri al
    transactions = Invoice.objects.all()
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    
    # DataFrame oluştur
    data = []
    for t in transactions:
        data.append({
            'Tarih': t.date,
            'Fatura No': t.invoice_number,
            'Müşteri': t.customer.name,
            'Tür': t.get_type_display(),
            'Tutar': t.total_amount,
            'Açıklama': t.description
        })
    
    df = pd.DataFrame(data)
    
    # Dosya adı
    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'excel':
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        df.to_excel(response, index=False)
    else:  # PDF
        from weasyprint import HTML
        from django.template.loader import render_to_string
        
        html_string = render_to_string('analytics/export/transactions_pdf.html', {
            'transactions': data
        })
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        HTML(string=html_string).write_pdf(response)
    
    return response 