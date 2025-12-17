# -*- coding: utf-8 -*-
"""
TFRS/VUK Uyumlu Raporlama View'ları
Yazdırma, dijital gönderim, yetki kontrolü ve KVKK uyumluluğu ile
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from datetime import date, datetime
import json
import io

from ..models import Company
from ..services.report_generator import (
    TFRSReportGenerator,
    ReportPermissionChecker,
    ReportExportService,
    KVKKDataProtection,
)


@login_required
@require_http_methods(["GET", "POST"])
def tfrs_balance_sheet_view(request: HttpRequest) -> HttpResponse:
    """TFRS uyumlu Bilanço raporu"""
    company_id = request.GET.get("company") or request.POST.get("company")
    as_of_date_str = request.GET.get("date") or request.POST.get("date")
    action = request.GET.get("action") or request.POST.get("action")
    
    # Şirket seçimi
    companies = Company.objects.filter(created_by=request.user)
    if not company_id and companies.exists():
        company = companies.first()
    elif company_id:
        company = get_object_or_404(Company, pk=company_id, created_by=request.user)
    else:
        messages.error(request, _("Lütfen bir şirket seçin."))
        return redirect("accounting:company_list")
    
    # Yetki kontrolü
    if not ReportPermissionChecker.can_access_report(request.user, company, 'bilanco'):
        messages.error(request, _("Bu rapora erişim yetkiniz bulunmamaktadır."))
        return redirect("accounting:home")
    
    # Tarih kontrolü
    if as_of_date_str:
        try:
            as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
        except ValueError:
            as_of_date = date.today()
    else:
        as_of_date = date.today()
    
    # Rapor oluştur
    generator = TFRSReportGenerator(company, request.user)
    report_data = generator.generate_balance_sheet(as_of_date)
    
    # KVKK: Veri erişim logu
    KVKKDataProtection.create_data_access_log(
        request.user,
        company,
        'bilanco',
        ['balance_sheet_data', 'company_financials']
    )
    
    # Anonimleştirme kontrolü
    if KVKKDataProtection.should_anonymize_report(request.user, company, 'bilanco'):
        report_data = KVKKDataProtection.anonymize_personal_data(report_data)
    
    # İşlemler: PDF, Excel, E-posta
    if action == "pdf":
        if not ReportPermissionChecker.can_export_report(request.user, company, 'bilanco'):
            messages.error(request, _("Bu raporu dışa aktarma yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        return ReportExportService.export_to_pdf(report_data, 'bilanco', 'accounting/reports/balance_sheet_pdf.html')
    
    elif action == "excel":
        if not ReportPermissionChecker.can_export_report(request.user, company, 'bilanco'):
            messages.error(request, _("Bu raporu dışa aktarma yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        return ReportExportService.export_to_excel(report_data, 'bilanco')
    
    elif action == "print":
        # Yazdırma için özel template
        return render(request, "accounting/reports/balance_sheet_print.html", {
            "report_data": report_data,
            "company": company,
            "as_of_date": as_of_date,
        })
    
    elif action == "send_email":
        if not ReportPermissionChecker.can_send_report(request.user, company, 'bilanco'):
            messages.error(request, _("Bu raporu gönderme yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        
        recipients = request.POST.getlist("recipients")
        if not recipients:
            messages.error(request, _("Lütfen en az bir alıcı e-posta adresi girin."))
            return redirect(request.path)
        
        # PDF oluştur ve gönder
        pdf_buffer = io.BytesIO()
        pdf_response = ReportExportService.export_to_pdf(report_data, 'bilanco', 'accounting/reports/balance_sheet_pdf.html')
        pdf_buffer.write(pdf_response.content)
        pdf_buffer.seek(0)
        
        success = ReportExportService.send_report_email(
            request.user,
            company,
            report_data,
            'bilanco',
            recipients,
            pdf_buffer
        )
        
        if success:
            messages.success(request, _("Rapor başarıyla gönderildi."))
        else:
            messages.error(request, _("Rapor gönderilirken bir hata oluştu."))
        
        return redirect(request.path)
    
    # Normal görüntüleme
    context = {
        "report_data": report_data,
        "company": company,
        "companies": companies,
        "as_of_date": as_of_date,
        "can_export": ReportPermissionChecker.can_export_report(request.user, company, 'bilanco'),
        "can_send": ReportPermissionChecker.can_send_report(request.user, company, 'bilanco'),
    }
    return render(request, "accounting/reports/balance_sheet.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def tfrs_income_statement_view(request: HttpRequest) -> HttpResponse:
    """TFRS uyumlu Gelir Tablosu raporu"""
    company_id = request.GET.get("company") or request.POST.get("company")
    start_date_str = request.GET.get("start_date") or request.POST.get("start_date")
    end_date_str = request.GET.get("end_date") or request.POST.get("end_date")
    action = request.GET.get("action") or request.POST.get("action")
    
    companies = Company.objects.filter(created_by=request.user)
    if not company_id and companies.exists():
        company = companies.first()
    elif company_id:
        company = get_object_or_404(Company, pk=company_id, created_by=request.user)
    else:
        messages.error(request, _("Lütfen bir şirket seçin."))
        return redirect("accounting:company_list")
    
    if not ReportPermissionChecker.can_access_report(request.user, company, 'gelir_tablosu'):
        messages.error(request, _("Bu rapora erişim yetkiniz bulunmamaktadır."))
        return redirect("accounting:home")
    
    # Tarih kontrolü
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            start_date = date.today().replace(day=1)
    else:
        start_date = date.today().replace(day=1)
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            end_date = date.today()
    else:
        end_date = date.today()
    
    generator = TFRSReportGenerator(company, request.user)
    report_data = generator.generate_income_statement(start_date, end_date)
    
    KVKKDataProtection.create_data_access_log(
        request.user,
        company,
        'gelir_tablosu',
        ['income_statement_data', 'revenue_expense_data']
    )
    
    if KVKKDataProtection.should_anonymize_report(request.user, company, 'gelir_tablosu'):
        report_data = KVKKDataProtection.anonymize_personal_data(report_data)
    
    if action == "pdf":
        if not ReportPermissionChecker.can_export_report(request.user, company, 'gelir_tablosu'):
            messages.error(request, _("Bu raporu dışa aktarma yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        return ReportExportService.export_to_pdf(report_data, 'gelir_tablosu', 'accounting/reports/income_statement_pdf.html')
    
    elif action == "excel":
        if not ReportPermissionChecker.can_export_report(request.user, company, 'gelir_tablosu'):
            messages.error(request, _("Bu raporu dışa aktarma yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        return ReportExportService.export_to_excel(report_data, 'gelir_tablosu')
    
    elif action == "print":
        return render(request, "accounting/reports/income_statement_print.html", {
            "report_data": report_data,
            "company": company,
            "start_date": start_date,
            "end_date": end_date,
        })
    
    elif action == "send_email":
        if not ReportPermissionChecker.can_send_report(request.user, company, 'gelir_tablosu'):
            messages.error(request, _("Bu raporu gönderme yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        
        recipients = request.POST.getlist("recipients")
        if not recipients:
            messages.error(request, _("Lütfen en az bir alıcı e-posta adresi girin."))
            return redirect(request.path)
        
        pdf_buffer = io.BytesIO()
        pdf_response = ReportExportService.export_to_pdf(report_data, 'gelir_tablosu', 'accounting/reports/income_statement_pdf.html')
        pdf_buffer.write(pdf_response.content)
        pdf_buffer.seek(0)
        
        success = ReportExportService.send_report_email(
            request.user,
            company,
            report_data,
            'gelir_tablosu',
            recipients,
            pdf_buffer
        )
        
        if success:
            messages.success(request, _("Rapor başarıyla gönderildi."))
        else:
            messages.error(request, _("Rapor gönderilirken bir hata oluştu."))
        
        return redirect(request.path)
    
    context = {
        "report_data": report_data,
        "company": company,
        "companies": companies,
        "start_date": start_date,
        "end_date": end_date,
        "can_export": ReportPermissionChecker.can_export_report(request.user, company, 'gelir_tablosu'),
        "can_send": ReportPermissionChecker.can_send_report(request.user, company, 'gelir_tablosu'),
    }
    return render(request, "accounting/reports/income_statement.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def tfrs_trial_balance_view(request: HttpRequest) -> HttpResponse:
    """TFRS uyumlu Genel Mizan raporu"""
    company_id = request.GET.get("company") or request.POST.get("company")
    as_of_date_str = request.GET.get("date") or request.POST.get("date")
    action = request.GET.get("action") or request.POST.get("action")
    
    companies = Company.objects.filter(created_by=request.user)
    if not company_id and companies.exists():
        company = companies.first()
    elif company_id:
        company = get_object_or_404(Company, pk=company_id, created_by=request.user)
    else:
        messages.error(request, _("Lütfen bir şirket seçin."))
        return redirect("accounting:company_list")
    
    if not ReportPermissionChecker.can_access_report(request.user, company, 'mizan'):
        messages.error(request, _("Bu rapora erişim yetkiniz bulunmamaktadır."))
        return redirect("accounting:home")
    
    if as_of_date_str:
        try:
            as_of_date = datetime.strptime(as_of_date_str, "%Y-%m-%d").date()
        except ValueError:
            as_of_date = date.today()
    else:
        as_of_date = date.today()
    
    generator = TFRSReportGenerator(company, request.user)
    report_data = generator.generate_trial_balance(as_of_date)
    
    KVKKDataProtection.create_data_access_log(
        request.user,
        company,
        'mizan',
        ['trial_balance_data', 'account_balances']
    )
    
    if action == "pdf":
        if not ReportPermissionChecker.can_export_report(request.user, company, 'mizan'):
            messages.error(request, _("Bu raporu dışa aktarma yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        return ReportExportService.export_to_pdf(report_data, 'mizan', 'accounting/reports/trial_balance_pdf.html')
    
    elif action == "excel":
        if not ReportPermissionChecker.can_export_report(request.user, company, 'mizan'):
            messages.error(request, _("Bu raporu dışa aktarma yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        return ReportExportService.export_to_excel(report_data, 'mizan')
    
    elif action == "print":
        return render(request, "accounting/reports/trial_balance_print.html", {
            "report_data": report_data,
            "company": company,
            "as_of_date": as_of_date,
        })
    
    elif action == "send_email":
        if not ReportPermissionChecker.can_send_report(request.user, company, 'mizan'):
            messages.error(request, _("Bu raporu gönderme yetkiniz bulunmamaktadır."))
            return redirect(request.path)
        
        recipients = request.POST.getlist("recipients")
        if not recipients:
            messages.error(request, _("Lütfen en az bir alıcı e-posta adresi girin."))
            return redirect(request.path)
        
        pdf_buffer = io.BytesIO()
        pdf_response = ReportExportService.export_to_pdf(report_data, 'mizan', 'accounting/reports/trial_balance_pdf.html')
        pdf_buffer.write(pdf_response.content)
        pdf_buffer.seek(0)
        
        success = ReportExportService.send_report_email(
            request.user,
            company,
            report_data,
            'mizan',
            recipients,
            pdf_buffer
        )
        
        if success:
            messages.success(request, _("Rapor başarıyla gönderildi."))
        else:
            messages.error(request, _("Rapor gönderilirken bir hata oluştu."))
        
        return redirect(request.path)
    
    context = {
        "report_data": report_data,
        "company": company,
        "companies": companies,
        "as_of_date": as_of_date,
        "can_export": ReportPermissionChecker.can_export_report(request.user, company, 'mizan'),
        "can_send": ReportPermissionChecker.can_send_report(request.user, company, 'mizan'),
    }
    return render(request, "accounting/reports/trial_balance.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def tfrs_report_list_view(request: HttpRequest) -> HttpResponse:
    """TFRS raporları listesi ve seçim sayfası"""
    companies = Company.objects.filter(created_by=request.user)
    
    reports = [
        {
            "code": "bilanco",
            "name": _("Bilanço"),
            "description": _("TFRS uyumlu bilanço raporu"),
            "url": "accounting:tfrs_balance_sheet",
            "icon": "bi-file-earmark-spreadsheet",
        },
        {
            "code": "gelir_tablosu",
            "name": _("Gelir Tablosu"),
            "description": _("TFRS uyumlu gelir tablosu"),
            "url": "accounting:tfrs_income_statement",
            "icon": "bi-graph-up",
        },
        {
            "code": "nakit_akisi",
            "name": _("Nakit Akış Tablosu"),
            "description": _("TFRS uyumlu nakit akış tablosu"),
            "url": "accounting:tfrs_cash_flow",
            "icon": "bi-cash-stack",
        },
        {
            "code": "mizan",
            "name": _("Genel Mizan"),
            "description": _("VUK uyumlu genel mizan"),
            "url": "accounting:tfrs_trial_balance",
            "icon": "bi-table",
        },
        {
            "code": "yevmiye",
            "name": _("Yevmiye Defteri"),
            "description": _("VUK uyumlu yevmiye defteri"),
            "url": "accounting:tfrs_journal_ledger",
            "icon": "bi-journal-text",
        },
        {
            "code": "kebir",
            "name": _("Büyük Defter"),
            "description": _("VUK uyumlu büyük defter"),
            "url": "accounting:tfrs_general_ledger",
            "icon": "bi-book",
        },
    ]
    
    context = {
        "companies": companies,
        "reports": reports,
    }
    return render(request, "accounting/reports/tfrs_report_list.html", context)

