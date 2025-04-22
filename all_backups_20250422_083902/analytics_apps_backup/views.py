from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json

# Create your views here.

@login_required
def dashboard(request):
    """
    Analytics dashboard view
    """
    context = {
        'page_title': 'Analitik Paneli',
        'total_profit': 12500,
        'total_revenue': 25000,
        'total_expenses': 12500,
        'profit_margin': 50,
        'monthly_data': [
            {'month': 'Ocak', 'profit': 1200, 'revenue': 2400},
            {'month': 'Şubat', 'profit': 1500, 'revenue': 3000},
            {'month': 'Mart', 'profit': 1800, 'revenue': 3600},
            {'month': 'Nisan', 'profit': 2100, 'revenue': 4200},
            {'month': 'Mayıs', 'profit': 2400, 'revenue': 4800},
            {'month': 'Haziran', 'profit': 2700, 'revenue': 5400},
        ],
        'top_products': [
            {'name': 'Ürün A', 'sales': 120, 'revenue': 2400},
            {'name': 'Ürün B', 'sales': 100, 'revenue': 2000},
            {'name': 'Ürün C', 'sales': 80, 'revenue': 1600},
            {'name': 'Ürün D', 'sales': 60, 'revenue': 1200},
            {'name': 'Ürün E', 'sales': 40, 'revenue': 800},
        ],
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
def reports(request):
    """
    Reports list view
    """
    context = {
        'page_title': 'Raporlar',
        'reports': [
            {'id': 1, 'title': 'Aylık Satış Raporu', 'date': '2025-04-01', 'type': 'Satış'},
            {'id': 2, 'title': 'Ürün Performans Raporu', 'date': '2025-04-05', 'type': 'Ürün'},
            {'id': 3, 'title': 'Müşteri Analiz Raporu', 'date': '2025-04-10', 'type': 'Müşteri'},
            {'id': 4, 'title': 'Finansal Özet Raporu', 'date': '2025-04-15', 'type': 'Finans'},
        ],
    }
    return render(request, 'analytics/reports.html', context)

@login_required
def report_detail(request, report_id):
    """
    Report detail view
    """
    # Burada gerçek bir veritabanından rapor verisi çekilebilir
    reports = {
        1: {'id': 1, 'title': 'Aylık Satış Raporu', 'date': '2025-04-01', 'type': 'Satış', 'content': 'Aylık satış raporu içeriği...'},
        2: {'id': 2, 'title': 'Ürün Performans Raporu', 'date': '2025-04-05', 'type': 'Ürün', 'content': 'Ürün performans raporu içeriği...'},
        3: {'id': 3, 'title': 'Müşteri Analiz Raporu', 'date': '2025-04-10', 'type': 'Müşteri', 'content': 'Müşteri analiz raporu içeriği...'},
        4: {'id': 4, 'title': 'Finansal Özet Raporu', 'date': '2025-04-15', 'type': 'Finans', 'content': 'Finansal özet raporu içeriği...'},
    }
    
    report = reports.get(report_id, {'id': 0, 'title': 'Rapor Bulunamadı', 'date': '', 'type': '', 'content': ''})
    
    context = {
        'page_title': report['title'],
        'report': report,
    }
    return render(request, 'analytics/report_detail.html', context)

@login_required
def charts(request):
    """
    Charts view
    """
    context = {
        'page_title': 'Grafikler',
        'chart_data': json.dumps({
            'labels': ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
            'datasets': [
                {
                    'label': 'Satışlar',
                    'data': [1200, 1500, 1800, 2100, 2400, 2700],
                    'backgroundColor': 'rgba(33, 147, 176, 0.2)',
                    'borderColor': 'rgba(33, 147, 176, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Giderler',
                    'data': [600, 750, 900, 1050, 1200, 1350],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        }),
    }
    return render(request, 'analytics/charts.html', context)

@login_required
def export_data(request):
    """
    Export data view
    """
    # Burada gerçek veri dışa aktarma işlemi yapılabilir
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics_data.csv"'
    
    # Örnek CSV verisi
    response.write('Tarih,Satış,Gelir,Gider,Kar\n')
    response.write('2025-01-01,1200,2400,1200,1200\n')
    response.write('2025-02-01,1500,3000,1500,1500\n')
    response.write('2025-03-01,1800,3600,1800,1800\n')
    response.write('2025-04-01,2100,4200,2100,2100\n')
    response.write('2025-05-01,2400,4800,2400,2400\n')
    response.write('2025-06-01,2700,5400,2700,2700\n')
    
    return response
