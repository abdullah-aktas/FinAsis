"""
AI-Powered Audit Dashboard Views
Yapay Zeka ve Blockchain Destekli Dashboard
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from ..models import AuditEvent
from ..ai_audit import AuditAIAnalyzer
from ..blockchain_audit import BlockchainAuditManager
from ..kobi_analytics import KOBIAuditAnalytics


@login_required
def ai_dashboard(request):
    """
    Ana AI-destekli audit dashboard
    """
    company = getattr(request.user, "company", None)

    # Son 30 günlük audit events
    cutoff = timezone.now() - timedelta(days=30)
    audit_events = AuditEvent.objects.filter(created_at__gte=cutoff)

    if company:
        audit_events = audit_events.filter(tenant__company=company)

    # AI Analizi
    anomalies = AuditAIAnalyzer.detect_anomalies(audit_events, lookback_days=30)

    # Risk skoru
    entity_data = {
        "transaction_count": audit_events.count(),
        "high_severity_count": audit_events.filter(
            severity__in=["high", "critical"]
        ).count(),
        "total_financial_impact": sum(
            [
                float(e.financial_impact)
                for e in audit_events.filter(financial_impact__isnull=False)
            ]
        ),
        "off_hours_count": audit_events.extra(
            where=[
                "EXTRACT(HOUR FROM created_at) >= 22 OR EXTRACT(HOUR FROM created_at) <= 6"
            ]
        ).count(),
    }

    risk_score, risk_breakdown = AuditAIAnalyzer.calculate_risk_score(entity_data)

    # AI Önerileri
    recommendations = AuditAIAnalyzer.generate_recommendations(anomalies, risk_score)

    # KOBİ Sağlık Skoru
    kobi_health = KOBIAuditAnalytics.get_kobi_health_score(company, audit_events)

    # Blockchain Doğrulama
    blockchain_manager = BlockchainAuditManager()
    blockchain_status = blockchain_manager.verify_audit_trail()

    context = {
        "anomalies": anomalies[:10],  # Top 10
        "total_anomalies": len(anomalies),
        "risk_score": risk_score,
        "risk_breakdown": risk_breakdown,
        "recommendations": recommendations[:5],  # Top 5
        "kobi_health": kobi_health,
        "blockchain_verified": blockchain_status["valid"],
        "blockchain_stats": blockchain_status.get("statistics", {}),
        "total_events": audit_events.count(),
        "critical_events": audit_events.filter(severity="critical").count(),
        "period_days": 30,
    }

    return render(request, "audit/ai_dashboard.html", context)


@login_required
def anomaly_detection_view(request):
    """Detaylı anomali tespit sayfası"""
    lookback_days = int(request.GET.get("days", 30))

    cutoff = timezone.now() - timedelta(days=lookback_days)
    audit_events = AuditEvent.objects.filter(created_at__gte=cutoff)

    company = getattr(request.user, "company", None)
    if company:
        audit_events = audit_events.filter(tenant__company=company)

    # Anomali tespiti
    anomalies = AuditAIAnalyzer.detect_anomalies(audit_events, lookback_days)

    # Gruplama
    by_type = {}
    by_severity = {}

    for anomaly in anomalies:
        atype = anomaly["type"]
        severity = anomaly["severity"]

        by_type[atype] = by_type.get(atype, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1

    context = {
        "anomalies": anomalies,
        "by_type": by_type,
        "by_severity": by_severity,
        "lookback_days": lookback_days,
        "total_events": audit_events.count(),
    }

    return render(request, "audit/anomaly_detection.html", context)


@login_required
def kobi_health_dashboard(request):
    """KOBİ Sağlık Dashboard"""
    company = getattr(request.user, "company", None)

    if not company:
        return render(
            request, "audit/kobi_health.html", {"error": "Şirket bilgisi bulunamadı"}
        )

    # Audit events
    audit_events = AuditEvent.objects.all()
    if company:
        audit_events = audit_events.filter(tenant__company=company)

    # Sağlık skoru
    health_score = KOBIAuditAnalytics.get_kobi_health_score(company, audit_events)

    # Sektör karşılaştırması
    sector = request.GET.get("sector", "genel")
    benchmarking = KOBIAuditAnalytics.get_sector_benchmarking(
        company, audit_events, sector
    )

    # Maliyet optimizasyonu
    cost_opportunities = KOBIAuditAnalytics.get_cost_optimization_opportunities(
        audit_events
    )

    # Yönetim özeti
    executive_summary = KOBIAuditAnalytics.generate_executive_summary(
        company, audit_events, period_days=30
    )

    context = {
        "company": company,
        "health_score": health_score,
        "benchmarking": benchmarking,
        "cost_opportunities": cost_opportunities,
        "executive_summary": executive_summary,
        "sector": sector,
    }

    return render(request, "audit/kobi_health_dashboard.html", context)


@login_required
def blockchain_verification_view(request):
    """Blockchain doğrulama sayfası"""
    blockchain_manager = BlockchainAuditManager()

    # Tam doğrulama
    verification = blockchain_manager.verify_audit_trail()

    # İstatistikler
    stats = verification.get("statistics", {})

    # Son 10 blok
    recent_blocks = (
        blockchain_manager.blockchain.chain[-10:]
        if len(blockchain_manager.blockchain.chain) > 1
        else []
    )

    context = {
        "verification": verification,
        "stats": stats,
        "recent_blocks": [block.to_dict() for block in recent_blocks],
        "chain_length": len(blockchain_manager.blockchain.chain),
    }

    return render(request, "audit/blockchain_verification.html", context)


@login_required
def ajax_risk_trend(request):
    """AJAX: Risk trend verisi"""
    days = int(request.GET.get("days", 90))

    # Son X günlük günlük risk skorları
    historical_scores = []

    for i in range(days):
        date = timezone.now() - timedelta(days=days - i)
        day_events = AuditEvent.objects.filter(created_at__date=date.date())

        if day_events.exists():
            entity_data = {
                "transaction_count": day_events.count(),
                "high_severity_count": day_events.filter(
                    severity__in=["high", "critical"]
                ).count(),
                "total_financial_impact": sum(
                    [
                        float(e.financial_impact)
                        for e in day_events.filter(financial_impact__isnull=False)
                    ]
                ),
                "off_hours_count": 0,
            }

            risk_score, _ = AuditAIAnalyzer.calculate_risk_score(entity_data)
            historical_scores.append((date, risk_score))

    # Trend tahmini
    trend_analysis = AuditAIAnalyzer.predict_risk_trend(historical_scores)

    return JsonResponse(
        {
            "status": "success",
            "data": [
                {"date": date.strftime("%Y-%m-%d"), "score": score}
                for date, score in historical_scores
            ],
            "trend": trend_analysis,
        }
    )


@login_required
def ajax_recommendations(request):
    """AJAX: Akıllı öneriler"""
    audit_events = AuditEvent.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )

    # Anomaliler
    anomalies = AuditAIAnalyzer.detect_anomalies(audit_events)

    # Risk skoru
    entity_data = {
        "transaction_count": audit_events.count(),
        "high_severity_count": audit_events.filter(
            severity__in=["high", "critical"]
        ).count(),
        "total_financial_impact": 0,
        "off_hours_count": 0,
    }

    risk_score, _ = AuditAIAnalyzer.calculate_risk_score(entity_data)

    # Öneriler
    recommendations = AuditAIAnalyzer.generate_recommendations(anomalies, risk_score)

    return JsonResponse({"status": "success", "recommendations": recommendations})


@login_required
def generate_audit_certificate(request):
    """Blockchain destekli audit sertifikası oluştur"""
    company = getattr(request.user, "company", None)

    if not company:
        return JsonResponse({"error": "Şirket bulunamadı"}, status=400)

    # Tarih aralığı
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date or not end_date:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
    else:
        from django.utils.dateparse import parse_datetime

        start_date = parse_datetime(start_date)
        end_date = parse_datetime(end_date)

    # Blockchain manager
    blockchain_manager = BlockchainAuditManager()

    # Sertifika oluştur
    certificate = blockchain_manager.generate_audit_certificate(
        company_name=company.name if hasattr(company, "name") else str(company),
        start_date=start_date,
        end_date=end_date,
    )

    return JsonResponse({"status": "success", "certificate": certificate})
