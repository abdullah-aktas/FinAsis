from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from ..models import Declaration, Company
from ..services.reports import (
    generate_kdv_report, generate_muhtasar_report, generate_babs_report,
    export_report_to_excel, export_report_to_pdf,
    generate_yevmiye_defteri, generate_kebir_defteri, generate_mizan_defteri,
    generate_envanter_defteri, generate_kasa_defteri, generate_demirbas_defteri,
    generate_bilanco, generate_gelir_tablosu, generate_nakit_akisi_tablosu,
    generate_ar_aging, generate_ap_aging,
    calculate_financial_ratios, trend_analysis, ai_financial_advice
)
from django.contrib.auth.decorators import login_required
from ..services.beyanname_service import (
    generate_kdv_xml, generate_muhtasar_xml, generate_babs_xml
)

def report_redirect(request: HttpRequest) -> HttpResponse:
    return redirect('accounting:summary_report')

def summary_report(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting/summary_report.html')

def income_expense_chart_data(request: HttpRequest) -> HttpResponse:
    # Örnek veri, gerçek veri ile değiştirilmeli
    data = {
        'income': [1000, 2000, 1500],
        'expense': [800, 1200, 900],
    }
    return HttpResponse(data)

def chart_dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounting/chart_dashboard.html')

def summary_report_pdf(request: HttpRequest) -> HttpResponse:
    # PDF rapor üretimi burada yapılacak
    return HttpResponse('PDF raporu')

def declaration_report_list(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    return render(request, 'accounting/declaration_report_list.html', {'companies': companies})

def kdv_report_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    period = request.GET.get('period', '2024-06')
    df = generate_kdv_report(company, period)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'kdv_{period}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'kdv_{period}.pdf')
    return render(request, 'accounting/kdv_report.html', {'df': df, 'period': period, 'company': company, 'companies': companies})

def muhtasar_report_view(request: HttpRequest) -> HttpResponse:
    company = request.user.company
    period = request.GET.get('period', '2024-06')
    df = generate_muhtasar_report(company, period)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'muhtasar_{period}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'muhtasar_{period}.pdf')
    return render(request, 'accounting/muhtasar_report.html', {'df': df, 'period': period})

def babs_report_view(request: HttpRequest) -> HttpResponse:
    company = request.user.company
    period = request.GET.get('period', '2024-06')
    df = generate_babs_report(company, period)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'babs_{period}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'babs_{period}.pdf')
    return render(request, 'accounting/babs_report.html', {'df': df, 'period': period})

def ar_aging_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    company = Company.objects.get(pk=company_id) if company_id else companies.first()
    df = generate_ar_aging(company)
    if 'excel' in request.GET:
        return export_report_to_excel(df, 'aging.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, 'aging.pdf')
    return render(request, 'accounting/ar_aging.html', {'df': df, 'company': company, 'companies': companies})

def ap_aging_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    company = Company.objects.get(pk=company_id) if company_id else companies.first()
    df = generate_ap_aging(company)
    if 'excel' in request.GET:
        return export_report_to_excel(df, 'ap_aging.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, 'ap_aging.pdf')
    return render(request, 'accounting/ap_aging.html', {'df': df, 'company': company, 'companies': companies})

def kdv_xml_download(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    period = request.GET.get('period', '2024-06')
    company = Company.objects.get(pk=company_id) if company_id else companies.first()
    xml_bytes = generate_kdv_xml(company, period)
    response = HttpResponse(xml_bytes, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename=kdv_{period}.xml'
    return response

def muhtasar_xml_download(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    period = request.GET.get('period', '2024-06')
    company = Company.objects.get(pk=company_id) if company_id else companies.first()
    xml_bytes = generate_muhtasar_xml(company, period)
    response = HttpResponse(xml_bytes, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename=muhtasar_{period}.xml'
    return response

def babs_xml_download(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    period = request.GET.get('period', '2024-06')
    company = Company.objects.get(pk=company_id) if company_id else companies.first()
    xml_bytes = generate_babs_xml(company, period)
    response = HttpResponse(xml_bytes, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename=babs_{period}.xml'
    return response

def yevmiye_defteri_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_yevmiye_defteri(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'yevmiye_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'yevmiye_{year}_{month}.pdf')
    return render(request, 'accounting/yevmiye_defteri.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def kebir_defteri_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_kebir_defteri(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'kebir_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'kebir_{year}_{month}.pdf')
    return render(request, 'accounting/kebir_defteri.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def mizan_defteri_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_mizan_defteri(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'mizan_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'mizan_{year}_{month}.pdf')
    return render(request, 'accounting/mizan_defteri.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def envanter_defteri_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_envanter_defteri(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'envanter_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'envanter_{year}_{month}.pdf')
    return render(request, 'accounting/envanter_defteri.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def kasa_defteri_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_kasa_defteri(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'kasa_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'kasa_{year}_{month}.pdf')
    return render(request, 'accounting/kasa_defteri.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def demirbas_defteri_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_demirbas_defteri(company, year)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'demirbas_{year}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'demirbas_{year}.pdf')
    return render(request, 'accounting/demirbas_defteri.html', {'df': df, 'year': year, 'company': company, 'companies': companies})

def bilanco_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_bilanco(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'bilanco_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'bilanco_{year}_{month}.pdf')
    return render(request, 'accounting/bilanco.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def gelir_tablosu_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_gelir_tablosu(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'gelir_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'gelir_{year}_{month}.pdf')
    return render(request, 'accounting/gelir_tablosu.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def nakit_akisi_tablosu_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    df = generate_nakit_akisi_tablosu(company, year, month)
    if 'excel' in request.GET:
        return export_report_to_excel(df, f'nakit_akisi_{year}_{month}.xlsx')
    if 'pdf' in request.GET:
        return export_report_to_pdf(df, f'nakit_akisi_{year}_{month}.pdf')
    return render(request, 'accounting/nakit_akisi_tablosu.html', {'df': df, 'year': year, 'month': month, 'company': company, 'companies': companies})

def financial_analysis_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    year = int(request.GET.get('year', '2024'))
    month = int(request.GET.get('month', '6'))
    if company_id:
        company = Company.objects.get(pk=company_id)
    else:
        company = companies.first()
    ratios = calculate_financial_ratios(company, year, month)
    trends = trend_analysis(company, year)
    advice = ai_financial_advice(company, year, month)
    return render(request, 'accounting/financial_analysis.html', {
        'ratios': ratios,
        'trends': trends,
        'advice': advice,
        'company': company,
        'companies': companies,
        'year': year,
        'month': month
    }) 

def variance_analysis_view(request: HttpRequest) -> HttpResponse:
    companies = Company.objects.filter(created_by=request.user)
    company_id = request.GET.get('company')
    company = Company.objects.get(pk=company_id) if company_id else companies.first()
    period = request.GET.get('period', '2024-06')
    # Basit sapma: gerçekleşen (Invoice+Expense) vs senaryo çarpanları
    from ..models import PlanningScenario, Invoice, Expense
    scenario_id = request.GET.get('scenario')
    scenario = PlanningScenario.objects.filter(company=company, id=scenario_id).first() if scenario_id else PlanningScenario.objects.filter(company=company).first()
    year, month = period.split('-')
    inv_total = Invoice.objects.filter(company=company, issue_date__year=int(year), issue_date__month=int(month)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    exp_total = Expense.objects.filter(company=company, expense_date__year=int(year), expense_date__month=int(month)).aggregate(Sum('amount'))['amount__sum'] or 0
    actual_profit = float(inv_total) - float(exp_total)
    if scenario:
        plan_revenue = float(inv_total) * float(scenario.revenue_multiplier)
        plan_expense = float(exp_total) * float(scenario.expense_multiplier)
        plan_profit = plan_revenue - plan_expense
    else:
        plan_revenue = float(inv_total)
        plan_expense = float(exp_total)
        plan_profit = plan_revenue - plan_expense
    df = pd.DataFrame([
        {"Kalem": "Gelir", "Gerçek": float(inv_total), "Plan": plan_revenue, "Sapma": float(inv_total) - plan_revenue},
        {"Kalem": "Gider", "Gerçek": float(exp_total), "Plan": plan_expense, "Sapma": float(exp_total) - plan_expense},
        {"Kalem": "Kar", "Gerçek": actual_profit, "Plan": plan_profit, "Sapma": actual_profit - plan_profit},
    ])
    return render(request, 'accounting/variance_analysis.html', {'df': df, 'company': company, 'companies': companies, 'scenario': scenario, 'period': period})

@login_required
def auto_book_view(request: HttpRequest) -> HttpResponse:
    """Belge/metin yükleyip fiş önizleme arayüzü."""
    companies = Company.objects.filter(created_by=request.user)
    return render(request, 'accounting/auto_book.html', {'companies': companies})

@login_required
def rule_manager_view(request: HttpRequest) -> HttpResponse:
    """Kural listesi ve hızlı test arayüzü."""
    companies = Company.objects.filter(created_by=request.user)
    return render(request, 'accounting/rule_manager.html', {'companies': companies})