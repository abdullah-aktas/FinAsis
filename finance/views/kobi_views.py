# -*- coding: utf-8 from kobi_analysis.models import *
from accounting.models import Company
"""
KOBİ Finance Views
Django views for SME financial management dashboard and analysis
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from datetime import datetime, timedelta
import json

from kobi_analysis.models import KOBIFinancialAnalysis, BudgetPlan  # wildcard kaldırıldı
from accounting.models import Company
from finance.enhanced_accounting_models import JournalEntry  # ledger entries

# BudgetItem modeli henüz tanımlı değilse bütçe detay karşılaştırmasını atlaya biliriz
try:  # noqa: SIM105
    from kobi_analysis.models import BudgetItem  # type: ignore
except Exception:  # pragma: no cover
    BudgetItem = None  # type: ignore


@login_required
def kobi_dashboard(request):
    """
    Ana KOBİ finansal yönetim paneli
    """
    # Şirket bilgisi
    company = request.user.company if hasattr(request.user, 'company') else None
    if not company:
        messages.error(request, _('Lütfen önce şirket bilgilerinizi tamamlayın.'))
        return redirect('company_setup')
    
    # Tarih aralıkları
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Temel finansal metrikler
    context = {
        'company': company,
        'today': today,
    }
    
    try:
        # KOBİ Finansal Analizi varsa getir
        financial_analysis = KOBIFinancialAnalysis.objects.filter(
            company=company
        ).order_by('-analysis_date').first()
        
        if financial_analysis:
            score_val = financial_analysis.financial_health_score or 0
            context.update({
                'financial_health': {
                    'score': score_val,
                    'status_text': _('İyi') if score_val > 70 else _('Orta') if score_val > 50 else _('Zayıf'),
                    'last_updated': getattr(financial_analysis, 'analysis_period_end', timezone.now().date()),
                    'risk_level': 'low' if score_val > 70 else 'medium' if score_val > 50 else 'high',
                    'risk_level_text': _('Düşük Risk') if score_val > 70 else _('Orta Risk') if score_val > 50 else _('Yüksek Risk'),
                }
            })
        
        # Aylık gelir hesaplama
        monthly_revenue = JournalEntry.objects.filter(
            voucher__company=company,
            voucher__date__gte=this_month_start,
            voucher__date__lte=today,
            account__account_type='INCOME'
        ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')
        
        # Net kar hesaplama (gelir - gider)
        monthly_expenses = JournalEntry.objects.filter(
            voucher__company=company,
            voucher__date__gte=this_month_start,
            voucher__date__lte=today,
            account__account_type='EXPENSE'
        ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')
        
        net_profit = monthly_revenue - monthly_expenses
        
        # Nakit bakiye (kasa + banka hesapları)
        cash_balance = JournalEntry.objects.filter(
            voucher__company=company,
            account__code__startswith__in=['100', '102']  # Kasa ve Banka hesapları
        ).aggregate(
            debit_total=Sum('debit_amount'),
            credit_total=Sum('credit_amount')
        )
        
        cash_debit = cash_balance['debit_total'] or Decimal('0')
        cash_credit = cash_balance['credit_total'] or Decimal('0')
        total_cash_balance = cash_debit - cash_credit
        
        # Kar marjı hesaplama
        profit_margin = (net_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
        
        context.update({
            'monthly_revenue': monthly_revenue,
            'net_profit': net_profit,
            'cash_balance': total_cash_balance,
            'profit_margin': profit_margin,
        })
        
        # Finansal oranlar
        if financial_analysis:
            context['financial_ratios'] = {
                'current_ratio': {
                    'value': financial_analysis.current_ratio,
                    'status': 'good' if (financial_analysis.current_ratio or 0) >= 1.2 else 'average' if (financial_analysis.current_ratio or 0) >= 1.0 else 'poor'
                },
                'quick_ratio': {
                    'value': financial_analysis.quick_ratio,
                    'status': 'good' if (financial_analysis.quick_ratio or 0) >= 1.0 else 'average' if (financial_analysis.quick_ratio or 0) >= 0.8 else 'poor'
                },
                'debt_to_equity': {
                    'value': financial_analysis.debt_to_equity_ratio,
                    'status': 'good' if (financial_analysis.debt_to_equity_ratio or 99) <= 0.5 else 'average' if (financial_analysis.debt_to_equity_ratio or 99) <= 1.0 else 'poor'
                },
                'roa': {
                    'value': financial_analysis.roa,
                    'status': 'good' if (financial_analysis.roa or 0) >= 10 else 'average' if (financial_analysis.roa or 0) >= 5 else 'poor'
                },
                'roe': {
                    'value': financial_analysis.roe,
                    'status': 'good' if (financial_analysis.roe or 0) >= 15 else 'average' if (financial_analysis.roe or 0) >= 8 else 'poor'
                },
            }
        
        # Uyarılar ve öneriler
        alerts = []
        
        if total_cash_balance < 0:
            alerts.append({
                'type': 'critical',
                'title': _('Nakit Sıkıntısı'),
                'description': _('Nakit bakiyeniz negatif. Acil nakit akışı planlaması yapın.'),
                'priority': 'high',
                'priority_text': _('Yüksek'),
                'action': _('Nakit akış tahmini oluşturun ve vadeli ödemeleri gözden geçirin.')
            })
        
        if profit_margin < 5:
            alerts.append({
                'type': 'warning',
                'title': _('Düşük Kar Marjı'),
                'description': _('Kar marjınız %5\'in altında. Maliyet analizi yapmanız öneriyoruz.'),
                'priority': 'medium',
                'priority_text': _('Orta'),
                'action': _('Gider kalemlerini detaylı analiz edin ve fiyatlandırma stratejinizi gözden geçirin.')
            })
        if financial_analysis and (financial_analysis.current_ratio or 0) < 1.0:
            alerts.append({
                'type': 'warning',
                'title': _('Likidite Sorunu'),
                'description': _('Cari oranınız 1.0\'ın altında. Kısa vadeli borç ödeme gücünüz sınırlı.'),
                'priority': 'high',
                'priority_text': _('Yüksek'),
                'action': _('Alacak tahsilat süresini kısaltın veya kısa vadeli finansman alternatifleri değerlendirin.')
            })
        
        context['alerts'] = alerts
        
        # Son işlemler
        recent_transactions = JournalEntry.objects.filter(
            voucher__company=company
        ).select_related('voucher', 'account').order_by('-voucher__date', '-id')[:10]
        
        formatted_transactions = []
        for entry in recent_transactions:
            amount = entry.debit_amount if entry.debit_amount > 0 else entry.credit_amount
            formatted_transactions.append({
                'date': entry.voucher.date,
                # get_voucher_type_display olabilir; yoksa voucher_type alanını kullan
                'type_text': getattr(entry.voucher, 'get_voucher_type_display', lambda: getattr(entry.voucher, 'voucher_type', ''))(),
                'description': entry.description or entry.voucher.description,
                'amount': amount,
                'amount_color': 'success' if entry.debit_amount > 0 else 'danger',
                'status_text': _('Onaylandı'),
                'status_color': 'success',
                'icon': 'arrow-up' if entry.debit_amount > 0 else 'arrow-down',
                'color': 'success' if entry.debit_amount > 0 else 'danger'
            })
        
        context['recent_transactions'] = formatted_transactions
        
        # Yaklaşan vadeler (örnek)
        context['upcoming_due_dates'] = []
        
        # Chart.js için veri hazırlama
        last_6_months = []
        cash_inflow_data = []
        cash_outflow_data = []
        
        for i in range(6):
            month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            
            inflow = JournalEntry.objects.filter(
                voucher__company=company,
                voucher__date__gte=month_start,
                voucher__date__lte=month_end,
                credit_amount__gt=0
            ).aggregate(total=Sum('credit_amount'))['total'] or 0
            
            outflow = JournalEntry.objects.filter(
                voucher__company=company,
                voucher__date__gte=month_start,
                voucher__date__lte=month_end,
                debit_amount__gt=0
            ).aggregate(total=Sum('debit_amount'))['total'] or 0
            
            last_6_months.insert(0, month_start.strftime('%b %Y'))
            cash_inflow_data.insert(0, float(inflow))
            cash_outflow_data.insert(0, float(outflow))
        
        context.update({
            'cash_flow_labels': json.dumps(last_6_months),
            'cash_inflow_data': json.dumps(cash_inflow_data),
            'cash_outflow_data': json.dumps(cash_outflow_data),
            'income_expense_data': json.dumps([float(monthly_revenue), float(monthly_expenses)]),
        })
        
        # Bütçe karşılaştırması
        current_budget = None
        if 'BudgetPlan' in globals():  # güvenli kontrol
            current_budget = BudgetPlan.objects.filter(
                company=company,
                period_start__lte=today,
                period_end__gte=today
            ).first()

        context['budget_comparison'] = current_budget
        if current_budget and BudgetItem:
            try:
                budget_items = BudgetItem.objects.filter(budget_plan=current_budget)
                budget_labels, budget_planned, budget_actual = [], [], []
                for item in budget_items:
                    acc_name = getattr(item.account, 'name', getattr(item.account, 'code', ''))
                    budget_labels.append(acc_name[:20])
                    budget_planned.append(float(getattr(item, 'planned_amount', 0)))
                    actual_amount = JournalEntry.objects.filter(
                        voucher__company=company,
                        voucher__date__gte=this_month_start,
                        voucher__date__lte=today,
                        account=item.account
                    ).aggregate(
                        total=Sum('debit_amount') - Sum('credit_amount')
                    )['total'] or 0
                    budget_actual.append(float(actual_amount))
                context.update({
                    'budget_labels': json.dumps(budget_labels),
                    'budget_planned': json.dumps(budget_planned),
                    'budget_actual': json.dumps(budget_actual),
                    'budget_data': True,
                })
            except Exception:  # pragma: no cover
                pass
        
    except Exception as e:
        messages.error(request, f'Dashboard verileri yüklenirken hata oluştu: {str(e)}')
        context.update({
            'monthly_revenue': 0,
            'net_profit': 0,
            'cash_balance': 0,
            'profit_margin': 0,
            'alerts': [],
            'recent_transactions': [],
        })
    
    return render(request, 'finance/kobi_dashboard.html', context)


@login_required
def financial_analysis_report(request):
    """
    Detaylı finansal analiz raporu
    """
    company = request.user.company if hasattr(request.user, 'company') else None
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('finance:kobi_dashboard')
    
    # En son analizi getir veya yenisini oluştur
    analysis = KOBIFinancialAnalysis.objects.filter(
        company=company
    ).order_by('-analysis_period_end').first()
    
    if not analysis:
        # Otomatik analiz oluştur
        analysis = create_kobi_analysis(company)
        if analysis:
            messages.success(request, _('Finansal analiz raporu oluşturuldu.'))
        else:
            messages.error(request, _('Analiz oluşturulamadı. Yeterli veri bulunmuyor.'))
            return redirect('finance:kobi_dashboard')
    
    context = {
        'company': company,
        'analysis': analysis,
    'analysis_period': f"{analysis.analysis_period_start.strftime('%d.%m.%Y')} - {analysis.analysis_period_end.strftime('%d.%m.%Y')}",
        'report_date': timezone.now(),
        'next_analysis_date': timezone.now() + timedelta(days=30),
    }
    
    # Finansal sağlık skoru
    context['financial_health_score'] = {
        'score': analysis.financial_health_score,
    'gauge_offset': 283 - ((analysis.financial_health_score or 0) / 100 * 283),
        'status_text': get_health_status_text(analysis.financial_health_score),
        'description': get_health_description(analysis.financial_health_score),
        'liquidity_score': calculate_liquidity_score(analysis),
        'profitability_score': calculate_profitability_score(analysis),
        'debt_score': calculate_debt_score(analysis),
    }
    
    # Risk seviyesi
    context['overall_risk_level'] = get_risk_level(analysis.financial_health_score)
    
    # Finansal oranlar
    context['ratios'] = {
        'current_ratio': {
            'value': analysis.current_ratio,
            'status': get_ratio_status(analysis.current_ratio, 'current'),
            'status_text': get_ratio_status_text(analysis.current_ratio, 'current'),
            'industry_avg': 1.2,
            'trend': 'up',  # Bu gerçek verilerle hesaplanmalı
            'trend_icon': 'up',
            'trend_text': _('Yükseliş eğiliminde')
        },
        'quick_ratio': {
            'value': analysis.quick_ratio,
            'status': get_ratio_status(analysis.quick_ratio, 'quick'),
            'status_text': get_ratio_status_text(analysis.quick_ratio, 'quick'),
            'trend': 'stable',
            'trend_icon': 'right',
            'trend_text': _('Stabil')
        },
        'profit_margin': {
            'value': analysis.profit_margin,
            'status': get_ratio_status(analysis.profit_margin, 'profit_margin'),
            'status_text': get_ratio_status_text(analysis.profit_margin, 'profit_margin')
        },
        'roa': {
            'value': analysis.roa,
            'status': get_ratio_status(analysis.roa, 'roa'),
            'status_text': get_ratio_status_text(analysis.roa, 'roa')
        },
        'debt_to_equity': {
            'value': analysis.debt_to_equity_ratio,
            'status': get_ratio_status(analysis.debt_to_equity_ratio, 'debt_to_equity'),
            'status_text': get_ratio_status_text(analysis.debt_to_equity_ratio, 'debt_to_equity')
        },
        'debt_ratio': {
            # debt_ratio alanı yok; debt_to_equity_ratio kullan veya None
            'value': analysis.debt_to_equity_ratio,
            'status': get_ratio_status(analysis.debt_to_equity_ratio, 'debt_to_equity'),
            'status_text': get_ratio_status_text(analysis.debt_to_equity_ratio, 'debt_to_equity')
        }
    }
    
    # Öneriler
    context['recommendations'] = generate_recommendations(analysis)
    
    # Risk faktörleri
    context['risk_factors'] = analyze_risk_factors(analysis)
    
    # Grafik verileri (örnek)
    context.update({
        'profit_trend_labels': json.dumps(['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz']),
        'revenue_data': json.dumps([100000, 120000, 110000, 130000, 125000, 140000]),
        'profit_data': json.dumps([10000, 15000, 12000, 18000, 16000, 20000]),
        'cashflow_labels': json.dumps(['Oca', 'Şub', 'Mar']),
        'cash_inflow': json.dumps([50000, 60000, 55000]),
        'cash_outflow': json.dumps([45000, 50000, 48000]),
        'company_ratios': json.dumps([80, 75, 85, 70, 60]),  # Normalize edilmiş oranlar
        'sector_ratios': json.dumps([75, 70, 80, 65, 70]),
        'asset_labels': json.dumps(['Dönen Varlıklar', 'Sabit Varlıklar', 'Maddi Olmayan']),
        'asset_values': json.dumps([60, 35, 5]),
    })
    
    # Export işlemi
    export_format = request.GET.get('export')
    if export_format == 'pdf':
        return generate_pdf_report(request, context)
    elif export_format == 'excel':
        return generate_excel_report(request, context)
    
    return render(request, 'finance/financial_analysis_report.html', context)


def create_kobi_analysis(company):
    """
    Otomatik KOBİ finansal analizi oluştur
    """
    try:
        # Analiz dönemi (son 12 ay)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        # Temel finansal veriler
        revenue = calculate_total_revenue(company, start_date, end_date)
        expenses = calculate_total_expenses(company, start_date, end_date)
        current_assets = calculate_current_assets(company, end_date)
        current_liabilities = calculate_current_liabilities(company, end_date)
        total_assets = calculate_total_assets(company, end_date)
        total_equity = calculate_total_equity(company, end_date)
        
        # Yeterli veri kontrolü
        if not all([revenue > 0, total_assets > 0]):
            return None
        
        # Analiz oluştur
        analysis = KOBIFinancialAnalysis.objects.create(
            company=company,
            analysis_date=timezone.now().date(),
            start_date=start_date,
            end_date=end_date,
            total_revenue=revenue,
            total_expenses=expenses,
            net_profit=revenue - expenses,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            total_assets=total_assets,
            total_equity=total_equity,
            current_ratio=current_assets / current_liabilities if current_liabilities > 0 else 0,
            quick_ratio=(current_assets * Decimal('0.8')) / current_liabilities if current_liabilities > 0 else 0,
            debt_to_equity_ratio=(total_assets - total_equity) / total_equity if total_equity > 0 else 0,
            debt_ratio=((total_assets - total_equity) / total_assets * 100) if total_assets > 0 else 0,
            profit_margin=((revenue - expenses) / revenue * 100) if revenue > 0 else 0,
            return_on_assets=((revenue - expenses) / total_assets * 100) if total_assets > 0 else 0,
            return_on_equity=((revenue - expenses) / total_equity * 100) if total_equity > 0 else 0,
        )
        
        # Finansal sağlık skoru hesaplama: modelde farklı implementasyonlar olabilir
        calc_health = getattr(analysis, 'calculate_health_score', None)
        if callable(calc_health):  # ilk model varyantı
            try:
                calc_health()
            except Exception:
                pass
        calc_all = getattr(analysis, 'calculate_all_ratios', None)
        if callable(calc_all):  # alternatif model varyantı
            try:
                calc_all()
            except Exception:
                pass
        analysis.save()
        
        return analysis
        
    except Exception as e:
        print(f"Analiz oluşturma hatası: {e}")
        return None


# Yardımcı fonksiyonlar
def get_health_status_text(score):
    if score >= 80:
        return _('Mükemmel')
    elif score >= 70:
        return _('İyi')
    elif score >= 60:
        return _('Orta')
    elif score >= 50:
        return _('Zayıf')
    else:
        return _('Kritik')


def get_health_description(score):
    if score >= 80:
        return _('Finansal durumunuz çok iyi. Mevcut performansınızı koruyun.')
    elif score >= 70:
        return _('Finansal durumunuz iyi. Küçük iyileştirmeler yapabilirsiniz.')
    elif score >= 60:
        return _('Finansal durumunuz orta seviyede. Bazı alanlarda iyileştirme gerekli.')
    elif score >= 50:
        return _('Finansal durumunuz zayıf. Acil eylem planı gerekli.')
    else:
        return _('Finansal durumunuz kritik seviyede. Derhal müdahale gerekli.')


def get_risk_level(score):
    if score >= 70:
        return 'low'
    elif score >= 50:
        return 'medium'
    else:
        return 'high'


def get_ratio_status(value, ratio_type):
    thresholds = {
        'current': {'good': 1.2, 'average': 1.0},
        'quick': {'good': 1.0, 'average': 0.8},
        'profit_margin': {'good': 10, 'average': 5},
        'roa': {'good': 10, 'average': 5},
        'debt_to_equity': {'poor': 1.0, 'average': 0.5},  # Ters mantık
        'debt_ratio': {'poor': 60, 'average': 40}  # Ters mantık
    }
    
    if ratio_type in ['debt_to_equity', 'debt_ratio']:
        # Düşük değer iyi
        if value <= thresholds[ratio_type]['average']:
            return 'good'
        elif value <= thresholds[ratio_type]['poor']:
            return 'average'
        else:
            return 'poor'
    else:
        # Yüksek değer iyi
        if value >= thresholds[ratio_type]['good']:
            return 'good'
        elif value >= thresholds[ratio_type]['average']:
            return 'average'
        else:
            return 'poor'


def get_ratio_status_text(value, ratio_type):
    status = get_ratio_status(value, ratio_type)
    status_map = {
        'excellent': _('Mükemmel'),
        'good': _('İyi'),
        'average': _('Orta'),
        'poor': _('Zayıf'),
        'critical': _('Kritik')
    }
    return status_map.get(status, _('Bilinmeyen'))


# Hesaplama fonksiyonları
def calculate_total_revenue(company, start_date, end_date):
    return JournalEntry.objects.filter(
        journal_voucher__company=company,
        journal_voucher__date__gte=start_date,
        journal_voucher__date__lte=end_date,
        account__account_type='INCOME'
    ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')


def calculate_total_expenses(company, start_date, end_date):
    return JournalEntry.objects.filter(
        journal_voucher__company=company,
        journal_voucher__date__gte=start_date,
        journal_voucher__date__lte=end_date,
        account__account_type='EXPENSE'
    ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')


def calculate_current_assets(company, date):
    # Dönen varlıklar (1xx hesap grubu)
    return JournalEntry.objects.filter(
        journal_voucher__company=company,
        journal_voucher__date__lte=date,
        account__code__startswith='1'
    ).aggregate(
        total=Sum('debit_amount') - Sum('credit_amount')
    )['total'] or Decimal('0')


def calculate_current_liabilities(company, date):
    # Kısa vadeli borçlar (3xx hesap grubunun bir kısmı)
    return JournalEntry.objects.filter(
        journal_voucher__company=company,
        journal_voucher__date__lte=date,
        account__code__startswith='30'  # Kısa vadeli borçlar
    ).aggregate(
        total=Sum('credit_amount') - Sum('debit_amount')
    )['total'] or Decimal('0')


def calculate_total_assets(company, date):
    # Tüm aktif hesaplar
    return JournalEntry.objects.filter(
        journal_voucher__company=company,
        journal_voucher__date__lte=date,
        account__account_type__in=['ASSET', 'CURRENT_ASSET', 'FIXED_ASSET']
    ).aggregate(
        total=Sum('debit_amount') - Sum('credit_amount')
    )['total'] or Decimal('0')


def calculate_total_equity(company, date):
    # Özkaynaklar
    return JournalEntry.objects.filter(
        journal_voucher__company=company,
        journal_voucher__date__lte=date,
        account__account_type='EQUITY'
    ).aggregate(
        total=Sum('credit_amount') - Sum('debit_amount')
    )['total'] or Decimal('0')


def calculate_liquidity_score(analysis):
    # Likidite skoru hesaplama
    current_score = min(analysis.current_ratio * 50, 100)
    quick_score = min(analysis.quick_ratio * 50, 100)
    return (current_score + quick_score) / 2


def calculate_profitability_score(analysis):
    # Karlılık skoru hesaplama
    profit_score = min(analysis.profit_margin * 10, 100)
    roa_score = min(analysis.return_on_assets * 10, 100)
    roe_score = min(analysis.return_on_equity * 5, 100)
    return (profit_score + roa_score + roe_score) / 3


def calculate_debt_score(analysis):
    # Borçluluk skoru hesaplama (düşük borç = yüksek skor)
    debt_ratio_score = max(100 - analysis.debt_ratio, 0)
    debt_to_equity_score = max(100 - (analysis.debt_to_equity_ratio * 50), 0)
    return (debt_ratio_score + debt_to_equity_score) / 2


def generate_recommendations(analysis):
    """
    Analize dayalı öneriler üret
    """
    recommendations = []
    
    # Likidite önerileri
    if analysis.current_ratio < 1.0:
        recommendations.append({
            'title': _('Likidite İyileştirmesi'),
            'description': _('Cari oranınız düşük. Kısa vadeli borç ödeme gücünüzü artırmak için alacak tahsilat süresini kısaltın.'),
            'priority': 'high',
            'priority_text': _('Yüksek'),
            'impact': _('Yüksek'),
            'icon': 'tint',
            'color': 'danger'
        })
    
    # Karlılık önerileri
    if analysis.profit_margin < 5:
        recommendations.append({
            'title': _('Kar Marjı İyileştirmesi'),
            'description': _('Kar marjınız düşük. Maliyet yapısını gözden geçirin ve fiyatlandırma stratejinizi optimize edin.'),
            'priority': 'medium',
            'priority_text': _('Orta'),
            'impact': _('Yüksek'),
            'icon': 'chart-line',
            'color': 'warning'
        })
    
    # Borçluluk önerileri
    if analysis.debt_to_equity_ratio > 1.0:
        recommendations.append({
            'title': _('Borç Yönetimi'),
            'description': _('Borç/özkaynak oranınız yüksek. Borç yapısını optimize edin veya özkaynak artırımı düşünün.'),
            'priority': 'medium',
            'priority_text': _('Orta'),
            'impact': _('Orta'),
            'icon': 'balance-scale',
            'color': 'info'
        })
    
    return recommendations


def analyze_risk_factors(analysis):
    """
    Risk faktörlerini analiz et
    """
    risk_factors = []
    
    # Likidite riski
    liquidity_score = calculate_liquidity_score(analysis)
    risk_factors.append({
        'category': _('Likidite Riski'),
        'score': liquidity_score,
        'severity': 'good' if liquidity_score > 70 else 'average' if liquidity_score > 50 else 'poor',
        'severity_text': _('Düşük') if liquidity_score > 70 else _('Orta') if liquidity_score > 50 else _('Yüksek'),
        'description': _('Kısa vadeli borç ödeme gücü riski'),
        'icon': 'tint',
        'color': 'primary'
    })
    
    # Karlılık riski
    profitability_score = calculate_profitability_score(analysis)
    risk_factors.append({
        'category': _('Karlılık Riski'),
        'score': profitability_score,
        'severity': 'good' if profitability_score > 70 else 'average' if profitability_score > 50 else 'poor',
        'severity_text': _('Düşük') if profitability_score > 70 else _('Orta') if profitability_score > 50 else _('Yüksek'),
        'description': _('Sürdürülebilir karlılık riski'),
        'icon': 'chart-line',
        'color': 'success'
    })
    
    # Borçluluk riski
    debt_score = calculate_debt_score(analysis)
    risk_factors.append({
        'category': _('Borçluluk Riski'),
        'score': debt_score,
        'severity': 'good' if debt_score > 70 else 'average' if debt_score > 50 else 'poor',
        'severity_text': _('Düşük') if debt_score > 70 else _('Orta') if debt_score > 50 else _('Yüksek'),
        'description': _('Aşırı borçlanma riski'),
        'icon': 'weight-hanging',
        'color': 'warning'
    })
    
    return risk_factors


def generate_pdf_report(request, context):
    """
    PDF rapor oluştur
    """
    # PDF oluşturma kodu buraya gelecek
    # Şimdilik placeholder
    from django.http import HttpResponse
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="finansal_analiz_raporu.pdf"'
    response.write('PDF raporu yakında eklenecek.'.encode('utf-8'))
    return response


def generate_excel_report(request, context):
    """
    Excel rapor oluştur
    """
    # Excel oluşturma kodu buraya gelecek
    # Şimdilik placeholder
    from django.http import HttpResponse
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="finansal_analiz_raporu.xlsx"'
    response.write('Excel raporu yakında eklenecek.'.encode('utf-8'))
    return response


@login_required  
def ajax_cash_flow_data(request):
    """
    AJAX ile nakit akış verilerini getir
    """
    period = request.GET.get('period', '3m')
    company = request.user.company
    
    # Dönem sayısını belirle
    months = {'3m': 3, '6m': 6, '12m': 12}.get(period, 3)
    
    # Veri hazırlama
    labels = []
    inflow_data = []
    outflow_data = []
    
    for i in range(months):
        month_start = timezone.now().replace(day=1) - timedelta(days=i*30)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        inflow = JournalEntry.objects.filter(
            journal_voucher__company=company,
            journal_voucher__date__gte=month_start,
            journal_voucher__date__lte=month_end,
            credit_amount__gt=0
        ).aggregate(total=Sum('credit_amount'))['total'] or 0
        
        outflow = JournalEntry.objects.filter(
            journal_voucher__company=company,
            journal_voucher__date__gte=month_start,
            journal_voucher__date__lte=month_end,
            debit_amount__gt=0
        ).aggregate(total=Sum('debit_amount'))['total'] or 0
        
        labels.insert(0, month_start.strftime('%b'))
        inflow_data.insert(0, float(inflow))
        outflow_data.insert(0, float(outflow))
    
    return JsonResponse({
        'labels': labels,
        'inflow_data': inflow_data,
        'outflow_data': outflow_data
    })