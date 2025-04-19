# 5. Analytics & Dashboard

## 📌 Amaç
Bu dokümantasyon, FinAsis projesinin analitik ve dashboard özelliklerini, metrik kartları, pivot tablolar ve raporlama sistemlerini detaylandırmaktadır.

## ⚙️ Teknik Yapı

### 1. Metrik Kartları

#### 1.1. Nakit Akışı Metrikleri
```python
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate

def get_cash_flow_metrics(start_date, end_date):
    metrics = {
        'total_cash_in': CashFlow.objects.filter(
            date__range=[start_date, end_date],
            type='IN'
        ).aggregate(total=Sum('amount'))['total'],
        
        'total_cash_out': CashFlow.objects.filter(
            date__range=[start_date, end_date],
            type='OUT'
        ).aggregate(total=Sum('amount'))['total'],
        
        'daily_average': CashFlow.objects.filter(
            date__range=[start_date, end_date]
        ).annotate(
            date=TruncDate('date')
        ).values('date').annotate(
            daily_total=Sum('amount')
        ).aggregate(avg=Avg('daily_total'))['avg']
    }
    return metrics
```

#### 1.2. Vade Takibi
```python
def get_due_date_metrics():
    metrics = {
        'overdue': Invoice.objects.filter(
            due_date__lt=timezone.now(),
            status='UNPAID'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        ),
        
        'upcoming': Invoice.objects.filter(
            due_date__range=[
                timezone.now(),
                timezone.now() + timezone.timedelta(days=30)
            ],
            status='UNPAID'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
    }
    return metrics
```

### 2. Pivot Tablo Sistemi

#### 2.1. Dinamik Pivot Oluşturma
```python
import pandas as pd

def create_pivot_table(data, rows, columns, values):
    df = pd.DataFrame(data)
    pivot = pd.pivot_table(
        df,
        values=values,
        index=rows,
        columns=columns,
        aggfunc='sum'
    )
    return pivot
```

#### 2.2. Excel Export
```python
def export_to_excel(pivot_table, filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    pivot_table.to_excel(writer, sheet_name='Pivot')
    
    workbook = writer.book
    worksheet = writer.sheets['Pivot']
    
    # Format tanımlamaları
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    # Başlıkları formatla
    for col_num, value in enumerate(pivot_table.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    
    writer.save()
```

### 3. Filtrelenebilir Raporlar

#### 3.1. Rapor Oluşturucu
```python
class ReportGenerator:
    def __init__(self, model, filters=None):
        self.model = model
        self.filters = filters or {}
    
    def apply_filters(self, queryset):
        for field, value in self.filters.items():
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset
    
    def generate_report(self, fields):
        queryset = self.model.objects.all()
        queryset = self.apply_filters(queryset)
        return queryset.values(*fields)
```

#### 3.2. PDF Export
```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def export_to_pdf(data, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    # Tablo verilerini hazırla
    table_data = [list(data.columns)]  # Başlıklar
    table_data.extend(data.values.tolist())  # Veriler
    
    # Tablo oluştur
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
```

## 🔧 Kullanım Adımları

### 1. Dashboard Görüntüleme

#### 1.1. Metrik Kartlarını Görüntüleme
```python
# Nakit akışı metriklerini al
cash_metrics = get_cash_flow_metrics(
    start_date=timezone.now() - timezone.timedelta(days=30),
    end_date=timezone.now()
)

# Vade metriklerini al
due_metrics = get_due_date_metrics()

# Template'e gönder
context = {
    'cash_metrics': cash_metrics,
    'due_metrics': due_metrics
}
```

### 2. Pivot Tablo Oluşturma

#### 2.1. Satış Analizi
```python
# Satış verilerini al
sales_data = Sale.objects.values(
    'date',
    'product__category',
    'amount'
)

# Pivot tablo oluştur
pivot = create_pivot_table(
    data=sales_data,
    rows=['date'],
    columns=['product__category'],
    values=['amount']
)

# Excel'e aktar
export_to_excel(pivot, 'sales_analysis.xlsx')
```

### 3. Rapor Oluşturma

#### 3.1. Müşteri Raporu
```python
# Rapor oluşturucu
report = ReportGenerator(
    model=Customer,
    filters={'status': 'ACTIVE'}
)

# Rapor verilerini al
customer_data = report.generate_report([
    'name',
    'total_purchases',
    'last_purchase_date'
])

# PDF'e aktar
export_to_pdf(customer_data, 'customer_report.pdf')
```

## 🧪 Test Örnekleri

### 1. Metrik Hesaplama Testi
```python
def test_cash_flow_metrics():
    # Test verisi oluştur
    CashFlow.objects.create(
        date=timezone.now(),
        amount=1000,
        type='IN'
    )
    
    # Metrikleri hesapla
    metrics = get_cash_flow_metrics(
        start_date=timezone.now() - timezone.timedelta(days=1),
        end_date=timezone.now()
    )
    
    assert metrics['total_cash_in'] == 1000
    assert metrics['total_cash_out'] == 0
```

### 2. Pivot Tablo Testi
```python
def test_pivot_table():
    # Test verisi
    data = [
        {'date': '2023-01-01', 'category': 'A', 'amount': 100},
        {'date': '2023-01-01', 'category': 'B', 'amount': 200},
        {'date': '2023-01-02', 'category': 'A', 'amount': 150}
    ]
    
    # Pivot tablo oluştur
    pivot = create_pivot_table(
        data=data,
        rows=['date'],
        columns=['category'],
        values=['amount']
    )
    
    assert len(pivot.index) == 2
    assert len(pivot.columns) == 2
```

## 📝 Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. Performans Sorunları
**Sorun**: Büyük veri setlerinde yavaş çalışma
**Çözüm**:
- Veritabanı indekslerini optimize edin
- Sorgu önbelleğini kullanın
- Sayfalama uygulayın

### 2. Bellek Kullanımı
**Sorun**: Büyük pivot tablolarda bellek hatası
**Çözüm**:
- Veriyi parçalara bölün
- Stream işleme kullanın
- Bellek limitini ayarlayın

### 3. Export Hataları
**Sorun**: Excel/PDF export sırasında hatalar
**Çözüm**:
- Dosya izinlerini kontrol edin
- Bellek limitini artırın
- Geçici dosyaları temizleyin

## 📂 Dosya Yapısı ve Referanslar

```
finasis/
├── apps/
│   └── analytics/
│       ├── metrics/
│       │   ├── cash_flow.py
│       │   └── due_date.py
│       ├── reports/
│       │   ├── generator.py
│       │   └── exporters.py
│       └── templates/
│           ├── dashboard.html
│           └── reports.html
└── static/
    └── js/
        ├── charts.js
        └── pivot.js
```

## 🔍 Ek Kaynaklar

- [Django Aggregation Dokümantasyonu](https://docs.djangoproject.com/en/stable/topics/db/aggregation/)
- [Pandas Pivot Table Dokümantasyonu](https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html)
- [ReportLab Dokümantasyonu](https://www.reportlab.com/docs/)
- [Chart.js Dokümantasyonu](https://www.chartjs.org/docs/) 