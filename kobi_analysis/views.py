"""
KOBİ Analysis Views
AI ve Blockchain Destekli KOBİ Analiz Sistemleri
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta, date
from decimal import Decimal

from .models import (
    KOBIFinancialAnalysis,
    BudgetPlan,
    CashFlowForecast,
    FinancialGoal,
    IndustryBenchmark,
    CompetitorAnalysis,
    SWOTAnalysis,
    RiskAssessment,
    RiskMitigation,
    PerformanceMetric,
    FinancialAlert,
    AdvisoryReport,
    FinancialHealthSnapshot,
)
from accounting.models import Invoice, Expense
from audit.kobi_analytics import KOBIAuditAnalytics
from audit.models import AuditEvent


@login_required
def kobi_dashboard(request):
    """
    Ana KOBİ Analiz Dashboard
    AI ve Blockchain destekli kapsamlı özet
    """
    company = getattr(request.user, "company", None)

    if not company:
        messages.warning(
            request, "Şirket bilgisi bulunamadı. Lütfen önce şirket oluşturun."
        )
        return redirect("accounting:company_create")

    # Son 30 günlük veriler
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    # Son finansal analiz
    latest_analysis = (
        KOBIFinancialAnalysis.objects.filter(company=company)
        .order_by("-created_at")
        .first()
    )

    # Finansal veriler
    total_revenue = (
        Invoice.objects.filter(company=company, issue_date__gte=start_date).aggregate(
            Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )

    total_expenses = (
        Expense.objects.filter(company=company, expense_date__gte=start_date).aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )

    net_profit = total_revenue - total_expenses

    # Audit events
    audit_events = AuditEvent.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )

    # KOBİ Sağlık Skoru (AI destekli)
    financial_data = {
        "net_profit_margin": (net_profit / total_revenue * 100)
        if total_revenue > 0
        else 0,
        "current_ratio": 1.5,  # Varsayılan
        "debt_ratio": 0.4,  # Varsayılan
    }

    kobi_health = KOBIAuditAnalytics.get_kobi_health_score(
        company, audit_events, financial_data
    )

    # Aktif uyarılar
    active_alerts = FinancialAlert.objects.filter(
        company=company, is_active=True, severity__in=["HIGH", "CRITICAL"]
    ).order_by("-triggered_at")[:5]

    # Hedefler
    active_goals = FinancialGoal.objects.filter(company=company, status="IN_PROGRESS")[
        :5
    ]

    # Son raporlar
    recent_reports = AdvisoryReport.objects.filter(company=company).order_by(
        "-report_date"
    )[:3]

    context = {
        "company": company,
        "latest_analysis": latest_analysis,
        "kobi_health": kobi_health,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "active_alerts": active_alerts,
        "active_goals": active_goals,
        "recent_reports": recent_reports,
        "period_start": start_date,
        "period_end": end_date,
    }

    return render(request, "kobi_analysis/dashboard.html", context)


@login_required
def financial_analysis_detail(request, analysis_id):
    """Finansal analiz detay sayfası"""
    company = getattr(request.user, "company", None)
    analysis = get_object_or_404(KOBIFinancialAnalysis, id=analysis_id, company=company)

    # Sektör karşılaştırması
    industry_benchmarks = IndustryBenchmark.objects.filter(
        industry_sector=company.industry if hasattr(company, "industry") else "Genel"
    ).order_by("-benchmark_year")[:5]

    context = {
        "company": company,
        "analysis": analysis,
        "industry_benchmarks": industry_benchmarks,
    }

    return render(request, "kobi_analysis/analysis_detail.html", context)


@login_required
def budget_planning(request):
    """Bütçe planlama sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Aktif bütçeler
    active_budgets = BudgetPlan.objects.filter(
        company=company, status="ACTIVE"
    ).order_by("-fiscal_year")

    # Taslak bütçeler
    draft_budgets = BudgetPlan.objects.filter(company=company, status="DRAFT")

    context = {
        "company": company,
        "active_budgets": active_budgets,
        "draft_budgets": draft_budgets,
    }

    return render(request, "kobi_analysis/budget_planning.html", context)


@login_required
def cash_flow_forecast(request):
    """Nakit akış tahmin sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Son tahminler
    forecasts = CashFlowForecast.objects.filter(company=company).order_by(
        "-forecast_date"
    )[:12]

    # Risk analizi
    at_risk_forecasts = forecasts.filter(cash_shortage_risk=True)

    context = {
        "company": company,
        "forecasts": forecasts,
        "at_risk_forecasts": at_risk_forecasts,
    }

    return render(request, "kobi_analysis/cash_flow_forecast.html", context)


@login_required
def goals_tracking(request):
    """Hedef takip sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Tüm hedefler
    all_goals = FinancialGoal.objects.filter(company=company)

    # Kategorilere göre grupla
    active_goals = all_goals.filter(status="IN_PROGRESS")
    completed_goals = all_goals.filter(status="COMPLETED")
    failed_goals = all_goals.filter(status="FAILED")

    context = {
        "company": company,
        "active_goals": active_goals,
        "completed_goals": completed_goals,
        "failed_goals": failed_goals,
        "total_goals": all_goals.count(),
    }

    return render(request, "kobi_analysis/goals_tracking.html", context)


@login_required
def risk_management(request):
    """Risk yönetimi sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Riskler
    all_risks = RiskAssessment.objects.filter(company=company)

    # Kritik riskler
    critical_risks = all_risks.filter(risk_score__gte=70, status="IDENTIFIED").order_by(
        "-risk_score"
    )

    # Risk kategorileri
    risk_by_category = {}
    for risk in all_risks:
        cat = risk.get_risk_category_display()
        risk_by_category[cat] = risk_by_category.get(cat, 0) + 1

    # Mitigasyon planları
    mitigation_plans = RiskMitigation.objects.filter(
        risk__company=company, status__in=["PLANNED", "IN_PROGRESS"]
    )

    context = {
        "company": company,
        "all_risks": all_risks,
        "critical_risks": critical_risks,
        "risk_by_category": risk_by_category,
        "mitigation_plans": mitigation_plans,
    }

    return render(request, "kobi_analysis/risk_management.html", context)


@login_required
def competitor_analysis(request):
    """Rakip analizi sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Rakip analizleri
    analyses = CompetitorAnalysis.objects.filter(company=company).order_by(
        "-analysis_date"
    )

    context = {
        "company": company,
        "analyses": analyses,
    }

    return render(request, "kobi_analysis/competitor_analysis.html", context)


@login_required
def swot_analysis(request):
    """SWOT analizi sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # En son SWOT
    latest_swot = (
        SWOTAnalysis.objects.filter(company=company).order_by("-analysis_date").first()
    )

    # Tüm SWOT'lar
    all_swots = SWOTAnalysis.objects.filter(company=company).order_by("-analysis_date")

    context = {
        "company": company,
        "latest_swot": latest_swot,
        "all_swots": all_swots,
    }

    return render(request, "kobi_analysis/swot_analysis.html", context)


@login_required
def performance_metrics(request):
    """Performans metrikleri sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Metrikler
    metrics = PerformanceMetric.objects.filter(company=company).order_by(
        "metric_category", "metric_name"
    )

    # Kategorilere göre grupla
    metrics_by_category = {}
    for metric in metrics:
        cat = metric.get_metric_category_display()
        if cat not in metrics_by_category:
            metrics_by_category[cat] = []
        metrics_by_category[cat].append(metric)

    context = {
        "company": company,
        "metrics": metrics,
        "metrics_by_category": metrics_by_category,
    }

    return render(request, "kobi_analysis/performance_metrics.html", context)


@login_required
def advisory_reports(request):
    """Danışmanlık raporları sayfası"""
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    # Raporlar
    reports = AdvisoryReport.objects.filter(company=company).order_by("-report_date")

    context = {
        "company": company,
        "reports": reports,
    }

    return render(request, "kobi_analysis/advisory_reports.html", context)


@login_required
def generate_analysis(request):
    """
    Yeni finansal analiz oluştur
    AI destekli otomatik analiz
    """
    company = getattr(request.user, "company", None)

    if not company:
        return redirect("kobi_analysis:dashboard")

    if request.method == "POST":
        # Tarih aralığı
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        analysis_type = request.POST.get("analysis_type", "MONTHLY")

        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            # Finansal verileri topla
            total_revenue = (
                Invoice.objects.filter(
                    company=company,
                    issue_date__gte=start_date,
                    issue_date__lte=end_date,
                ).aggregate(Sum("total_amount"))["total_amount__sum"]
                or 0
            )

            total_expenses = (
                Expense.objects.filter(
                    company=company,
                    expense_date__gte=start_date,
                    expense_date__lte=end_date,
                ).aggregate(Sum("amount"))["amount__sum"]
                or 0
            )

            # Analiz oluştur
            analysis = KOBIFinancialAnalysis.objects.create(
                company=company,
                analysis_type=analysis_type,
                analysis_period_start=start_date,
                analysis_period_end=end_date,
                total_revenue=total_revenue,
                total_expenses=total_expenses,
                net_profit=total_revenue - total_expenses,
                total_assets=Decimal("100000"),  # Varsayılan, gerçek veriden alınmalı
                total_liabilities=Decimal("40000"),  # Varsayılan
                created_by=request.user,
            )

            messages.success(
                request,
                f"Finansal analiz başarıyla oluşturuldu! Sağlık Skoru: {analysis.financial_health_score}",
            )
            return redirect("kobi_analysis:analysis_detail", analysis_id=analysis.id)

    context = {
        "company": company,
    }

    return render(request, "kobi_analysis/generate_analysis.html", context)


# AJAX Views
@login_required
def ajax_quick_stats(request):
    """Hızlı istatistikler için AJAX endpoint"""
    company = getattr(request.user, "company", None)

    if not company:
        return JsonResponse({"error": "Şirket bulunamadı"}, status=400)

    # Son 30 günlük veriler
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    stats = {
        "total_revenue": float(
            Invoice.objects.filter(
                company=company, issue_date__gte=start_date
            ).aggregate(Sum("total_amount"))["total_amount__sum"]
            or 0
        ),
        "total_expenses": float(
            Expense.objects.filter(
                company=company, expense_date__gte=start_date
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        ),
        "active_alerts": FinancialAlert.objects.filter(
            company=company, is_active=True
        ).count(),
        "goals_completed": FinancialGoal.objects.filter(
            company=company, status="COMPLETED"
        ).count(),
    }

    stats["net_profit"] = stats["total_revenue"] - stats["total_expenses"]

    return JsonResponse({"success": True, "stats": stats})


@login_required
def ajax_health_trend(request):
    """Sağlık skoru trend verisi"""
    company = getattr(request.user, "company", None)

    if not company:
        return JsonResponse({"error": "Şirket bulunamadı"}, status=400)

    # Son 12 aylık snapshot'lar
    snapshots = FinancialHealthSnapshot.objects.filter(company=company).order_by(
        "-snapshot_date"
    )[:12]

    trend_data = [
        {
            "date": snap.snapshot_date.strftime("%Y-%m-%d"),
            "score": float(snap.overall_score),
            "liquidity": float(snap.liquidity_score),
            "profitability": float(snap.profitability_score),
            "solvency": float(snap.solvency_score),
        }
        for snap in reversed(snapshots)
    ]

    return JsonResponse({"success": True, "trend": trend_data})
