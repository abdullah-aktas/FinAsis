# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, F
from django.http import HttpResponse
import csv
from accounting.models import Invoice
from stock_management.models import Product
from banking.models import Transaction

@login_required
def kobi_dashboard(request):
    # Günlük satışlar
    today = timezone.now().date()
    daily_sales = Invoice.objects.filter(
        company=request.user.company,
        date=today,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Aylık gelir
    month_start = today.replace(day=1)
    monthly_revenue = Invoice.objects.filter(
        company=request.user.company,
        date__gte=month_start,
        date__lte=today,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Bekleyen faturalar
    pending_invoices = Invoice.objects.filter(
        company=request.user.company,
        status='pending'
    ).count()

    # Stok uyarıları
    stock_alerts = Product.objects.filter(
        company=request.user.company,
        stock_quantity__lte=F('min_stock_level')
    ).count()

    # Son 6 ayın satış verileri
    sales_data = []
    sales_labels = []
    for i in range(6):
        month = today - timedelta(days=30*i)
        month_sales = Invoice.objects.filter(
            company=request.user.company,
            date__year=month.year,
            date__month=month.month,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_data.append(month_sales)
        sales_labels.append(month.strftime('%B %Y'))

    # Ürün kategorileri
    categories = Product.objects.filter(
        company=request.user.company
    ).values('category').annotate(total=Count('id'))
    category_labels = [cat['category'] for cat in categories]
    category_data = [cat['total'] for cat in categories]

    # Önemli hatırlatmalar
    important_reminders = [
        {
            'title': 'Vergi Ödeme Tarihi',
            'description': 'Bu ayın vergi ödemesi yaklaşıyor.',
            'due_date': today + timedelta(days=7)
        },
        {
            'title': 'Stok Kontrolü',
            'description': 'Bazı ürünlerin stok seviyesi düşük.',
            'due_date': today + timedelta(days=3)
        }
    ]

    context = {
        'daily_sales': daily_sales,
        'monthly_revenue': monthly_revenue,
        'pending_invoices': pending_invoices,
        'stock_alerts': stock_alerts,
        'sales_data': sales_data,
        'sales_labels': sales_labels,
        'category_labels': category_labels,
        'category_data': category_data,
        'important_reminders': important_reminders
    }

    return render(request, 'reports/kobi_dashboard.html', context)

@login_required
def export_reports(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="kobi_raporu.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Rapor Türü', 'Değer', 'Tarih'])
    
    # Günlük satışlar
    today = timezone.now().date()
    daily_sales = Invoice.objects.filter(
        company=request.user.company,
        date=today,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    writer.writerow(['Günlük Satış', daily_sales, today])
    
    # Aylık gelir
    month_start = today.replace(day=1)
    monthly_revenue = Invoice.objects.filter(
        company=request.user.company,
        date__gte=month_start,
        date__lte=today,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    writer.writerow(['Aylık Gelir', monthly_revenue, month_start])
    
    # Bekleyen faturalar
    pending_invoices = Invoice.objects.filter(
        company=request.user.company,
        status='pending'
    ).count()
    writer.writerow(['Bekleyen Faturalar', pending_invoices, today])
    
    # Stok uyarıları
    stock_alerts = Product.objects.filter(
        company=request.user.company,
        stock_quantity__lte=F('min_stock_level')
    ).count()
    writer.writerow(['Stok Uyarıları', stock_alerts, today])
    
    return response 