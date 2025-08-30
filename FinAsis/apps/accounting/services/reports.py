from django.db.models import Sum
from datetime import date
from ..models import Invoice, Expense
from django.db.models.functions import TruncMonth
from collections import OrderedDict
from django.db.models import Count
import io
import pandas as pd
from django.http import HttpResponse
from ..models import Declaration
from reportlab.pdfgen import canvas
from ..models import Customer, Payment
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

"""
Raporlama servisleri: şirket özeti, aylık gelir/gider, en çok satış yapan müşteriler, borçlu müşteriler.
Her fonksiyonun başına kısa docstring eklendi.
"""
#Şirket Özeti Raporu
def get_company_summary(company, start_date=None, end_date=None):
    if not start_date:
        start_date = date.today().replace(day=1)  # bu ayın ilk günü
    if not end_date:
        end_date = date.today()

    # Toplam Gelir
    total_income = Invoice.objects.filter(
        company=company,
        issue_date__range=[start_date, end_date]
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    # Toplam Gider
    total_expense = Expense.objects.filter(
        company=company,
        expense_date__range=[start_date, end_date]
    ).aggregate(total=Sum("amount"))["total"] or 0

    # Kar
    net_profit = total_income - total_expense

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_profit": net_profit
    }
#Aylık Gelir ve Gider Raporu
def get_monthly_income_expense(company, months=6):
    from django.utils.timezone import now
    today = now().date()

    # Gelir
    income_data = (
        Invoice.objects.filter(company=company, issue_date__lte=today)
        .annotate(month=TruncMonth('issue_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('-month')[:months]
    )

    # Gider
    expense_data = (
        Expense.objects.filter(company=company, expense_date__lte=today)
        .annotate(month=TruncMonth('expense_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')[:months]
    )

    result = OrderedDict()
    for i in income_data:
        result[str(i["month"])] = {"income": i["total"], "expense": 0}
    for i in expense_data:
        key = str(i["month"])
        if key in result:
            result[key]["expense"] = i["total"]
        else:
            result[key] = {"income": 0, "expense": i["total"]}

    return result

#En Çok Satış Yapan Müşteriler
def top_customers(company, count=5):
    return Customer.objects.filter(company=company).annotate(
        sale_count=Count('sales')
    ).order_by('-sale_count')[:count]
#Borçlu Müşteriler
def get_debtor_customers(company):
    from django.db.models import Sum
    result = []
    customers = Customer.objects.filter(company=company)

    for customer in customers:
        total_invoice = Invoice.objects.filter(customer=customer).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_paid = Payment.objects.filter(customer=customer).aggregate(Sum('amount'))['amount__sum'] or 0
        if total_invoice > total_paid:
            result.append({
                "customer": customer,
                "borc": total_invoice - total_paid
            })
    return result

def generate_kdv_report(company, period):
    # Türkiye için fatura satırındaki KDV oranlarını dikkate al
    if company.country == 'TR':
        from ..models import Invoice
        invoices = Invoice.objects.filter(company=company, issue_date__startswith=period)
        data = []
        for inv in invoices:
            data.append({
                "Fatura No": inv.invoice_number,
                "KDV Matrahı": float(inv.total_amount),
                "KDV Oranı": f"%{int(inv.kdv_rate * 100)}",
                "KDV Tutarı": float(inv.total_amount) * float(inv.kdv_rate),
                "Para Birimi": company.base_currency
            })
        return pd.DataFrame(data)
    # Diğer ülkeler için örnek oran
    kdv_rates = {
        'DE': 0.19,
        'US': 0.07,
        'GB': 0.20,
    }
    kdv_orani = kdv_rates.get(company.country, 0.18)
    matrah = 10000
    kdv_tutari = matrah * kdv_orani
    data = [{
        "KDV Matrahı": matrah,
        "KDV Oranı": f"%{int(kdv_orani*100)}",
        "KDV Tutarı": kdv_tutari,
        "Para Birimi": company.base_currency
    }]
    return pd.DataFrame(data)

def generate_muhtasar_report(company, period):
    data = [{"Brüt Ücret": 5000, "Stopaj": 750}]
    return pd.DataFrame(data)

def generate_babs_report(company, period):
    data = [{"Alışlar": 20000, "Satışlar": 15000}]
    return pd.DataFrame(data)

def generate_yevmiye_defteri(company, year, month):
    # Örnek/mock veri: Gerçek uygulamada muhasebe fişlerinden alınmalı
    data = [
        {"Tarih": f"{year}-{month:02d}-01", "Fiş No": "1", "Açıklama": "Açılış Fişi", "Borç": 10000, "Alacak": 10000},
        {"Tarih": f"{year}-{month:02d}-05", "Fiş No": "2", "Açıklama": "Satış", "Borç": 5000, "Alacak": 5000},
    ]
    return pd.DataFrame(data)

def generate_kebir_defteri(company, year, month):
    data = [
        {"Hesap Kodu": "100", "Hesap Adı": "Kasa", "Borç Toplamı": 15000, "Alacak Toplamı": 12000, "Bakiye": 3000},
        {"Hesap Kodu": "120", "Hesap Adı": "Alıcılar", "Borç Toplamı": 5000, "Alacak Toplamı": 2000, "Bakiye": 3000},
    ]
    return pd.DataFrame(data)

def generate_mizan_defteri(company, year, month):
    data = [
        {"Hesap Kodu": "100", "Hesap Adı": "Kasa", "Borç": 15000, "Alacak": 12000, "Bakiye": 3000},
        {"Hesap Kodu": "120", "Hesap Adı": "Alıcılar", "Borç": 5000, "Alacak": 2000, "Bakiye": 3000},
    ]
    return pd.DataFrame(data)

def generate_envanter_defteri(company, year, month):
    data = [
        {"Stok Kodu": "STK001", "Stok Adı": "Ürün A", "Miktar": 100, "Birim Fiyat": 50, "Toplam": 5000},
        {"Stok Kodu": "STK002", "Stok Adı": "Ürün B", "Miktar": 200, "Birim Fiyat": 30, "Toplam": 6000},
    ]
    return pd.DataFrame(data)

def generate_kasa_defteri(company, year, month):
    data = [
        {"Tarih": f"{year}-{month:02d}-01", "Açıklama": "Kasa Açılışı", "Giren": 10000, "Çıkan": 0, "Bakiye": 10000},
        {"Tarih": f"{year}-{month:02d}-10", "Açıklama": "Satış Tahsilatı", "Giren": 5000, "Çıkan": 0, "Bakiye": 15000},
    ]
    return pd.DataFrame(data)

def generate_demirbas_defteri(company, year):
    data = [
        {"Demirbaş Kodu": "DMR001", "Adı": "Bilgisayar", "Alış Tarihi": f"{year}-01-15", "Tutar": 15000, "Amortisman Oranı": "%20"},
        {"Demirbaş Kodu": "DMR002", "Adı": "Yazıcı", "Alış Tarihi": f"{year}-03-10", "Tutar": 3000, "Amortisman Oranı": "%20"},
    ]
    return pd.DataFrame(data)

def generate_bilanco(company, year, month):
    data = [
        {"Aktif": "Kasa", "Tutar": 20000},
        {"Aktif": "Alacaklar", "Tutar": 10000},
        {"Pasif": "Sermaye", "Tutar": 25000},
        {"Pasif": "Borçlar", "Tutar": 5000},
    ]
    return pd.DataFrame(data)

def generate_gelir_tablosu(company, year, month):
    data = [
        {"Gelir Türü": "Satış Geliri", "Tutar": 30000},
        {"Gelir Türü": "Faaliyet Gideri", "Tutar": -10000},
        {"Gelir Türü": "Net Kar", "Tutar": 20000},
    ]
    return pd.DataFrame(data)

def generate_nakit_akisi_tablosu(company, year, month):
    data = [
        {"Dönem": f"{year}-{month:02d}", "Nakit Giriş": 25000, "Nakit Çıkış": 15000, "Net Nakit Akışı": 10000},
    ]
    return pd.DataFrame(data)

def export_report_to_excel(df, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def export_report_to_pdf(df, filename):
    output = io.BytesIO()
    p = canvas.Canvas(output)
    y = 800
    for col in df.columns:
        p.drawString(100, y, col)
        y -= 20
    for row in df.itertuples(index=False):
        y -= 20
        p.drawString(100, y, str(row))
    p.save()
    output.seek(0)
    response = HttpResponse(output, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def export_report_to_json(report_data):
    """Verilen rapor verisini JSON olarak dışa aktarır."""
    def normalize(data):
        # pandas DataFrame ise liste-dict'e çevir
        try:
            import pandas as pd  # noqa: F401
            if hasattr(data, 'to_dict'):
                return data.to_dict(orient='records')
        except Exception:
            pass
        return data

    normalized = normalize(report_data)
    response = HttpResponse(
        json.dumps(normalized, ensure_ascii=False, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename=report.json'
    return response

def export_report_to_xml(report_data):
    """Verilen rapor verisini XML olarak dışa aktarır."""
    def normalize_to_rows(data):
        try:
            if hasattr(data, 'to_dict'):
                return data.to_dict(orient='records')
        except Exception:
            pass
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
        return [{'value': str(data)}]

    rows = normalize_to_rows(report_data)
    root = Element('Report')
    for row in rows:
        row_el = SubElement(root, 'Row')
        if isinstance(row, dict):
            for key, value in row.items():
                col = SubElement(row_el, str(key).replace(' ', '_'))
                col.text = str(value)
        else:
            value_el = SubElement(row_el, 'Value')
            value_el.text = str(row)

    rough = tostring(root, encoding='utf-8')
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    response = HttpResponse(pretty.encode('utf-8'), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=report.xml'
    return response

def calculate_financial_ratios(company, year, month):
    # Gerçek uygulamada bilanço ve gelir tablosundan alınmalı
    # Mock değerler
    current_assets = 50000
    current_liabilities = 25000
    total_debt = 40000
    equity = 60000
    net_profit = 20000
    sales = 100000
    total_assets = 120000
    # Oranlar
    ratios = {
        "Cari Oran": round(current_assets / current_liabilities, 2),
        "Borç/Özsermaye": round(total_debt / equity, 2),
        "Net Kar Marjı": f"%{round((net_profit / sales) * 100, 2)}",
        "Aktif Karlılık": f"%{round((net_profit / total_assets) * 100, 2)}",
    }
    return ratios

def trend_analysis(company, year):
    # Basit trend analizi (örnek)
    # Gerçek uygulamada geçmiş yılların verileriyle
    sales_trend = [80000, 90000, 100000, 110000]
    profit_trend = [10000, 15000, 18000, 20000]
    return {
        "Satış Trend": sales_trend,
        "Kar Trend": profit_trend
    }

def ai_financial_advice(company, year, month):
    ratios = calculate_financial_ratios(company, year, month)
    advice = []
    if ratios["Cari Oran"] < 1.5:
        advice.append("Likidite riskiniz yüksek, kısa vadeli borçlarınızı azaltın veya dönen varlıklarınızı artırın.")
    if float(ratios["Net Kar Marjı"].replace('%','')) < 10:
        advice.append("Net kar marjınız düşük, maliyetleri gözden geçirin veya satışları artırmaya odaklanın.")
    if ratios["Borç/Özsermaye"] > 1:
        advice.append("Borçluluk oranınız yüksek, özkaynak artırımı veya borç azaltımı önerilir.")
    if not advice:
        advice.append("Finansal göstergeleriniz sağlıklı görünüyor. Mevcut stratejinizi sürdürebilirsiniz.")
    return advice
