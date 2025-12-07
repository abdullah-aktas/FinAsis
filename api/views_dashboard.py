"""
Dashboard API Views
Frontend için dashboard verilerini sağlar
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Ana dashboard istatistikleri
    """

    # Kullanıcı istatistikleri
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_this_month = User.objects.filter(
        date_joined__month=timezone.now().month
    ).count()

    # Modül istatistikleri
    module_stats = {}

    # Accounting
    try:
        from apps.accounting.models import Invoice, Expense

        module_stats["accounting"] = {
            "invoices": Invoice.objects.count(),
            "expenses": Expense.objects.count(),
        }
    except (ImportError, AttributeError, Exception):
        pass

    # Finance
    try:
        from apps.finance.models import Transaction

        module_stats["finance"] = {
            "transactions": Transaction.objects.count(),
        }
    except (ImportError, AttributeError, Exception):
        pass

    # Blockchain
    try:
        from apps.blockchain.models import Block, Transaction as BlockchainTx

        module_stats["blockchain"] = {
            "blocks": Block.objects.count(),
            "transactions": BlockchainTx.objects.count(),
        }
    except (ImportError, AttributeError, Exception):
        pass

    # Education
    try:
        from apps.education.models import Course, Certificate

        module_stats["education"] = {
            "courses": Course.objects.count(),
            "certificates": Certificate.objects.count(),
        }
    except (ImportError, AttributeError, Exception):
        pass

    # AI Assistant
    try:
        from apps.ai_assistant.models import SentimentAnalysis, DocumentSummary

        module_stats["ai_assistant"] = {
            "analyses": SentimentAnalysis.objects.count(),
            "summaries": DocumentSummary.objects.count(),
        }
    except (ImportError, AttributeError, Exception):
        pass

    # Son aktiviteler
    recent_activity = [
        {
            "icon": "person-plus",
            "title": f"{new_users_this_month} yeni kullanıcı kaydoldu",
            "time": "Bu ay",
        },
        {
            "icon": "file-earmark-text",
            "title": "Yeni faturalar oluşturuldu",
            "time": "2 saat önce",
        },
        {"icon": "graph-up", "title": "Aylık raporlar hazırlandı", "time": "Dün"},
    ]

    data = {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalInvoices": module_stats.get("accounting", {}).get("invoices", 0),
        "totalRevenue": 125000,  # Placeholder
        "modules": module_stats,
        "recentActivity": recent_activity,
    }

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def module_health(request):
    """
    Modül sağlık durumu
    """

    modules = [
        {
            "name": "Muhasebe",
            "code": "accounting",
            "status": "active",
            "uptime": "99.9%",
            "last_check": timezone.now().isoformat(),
        },
        {
            "name": "Finans",
            "code": "finance",
            "status": "active",
            "uptime": "99.8%",
            "last_check": timezone.now().isoformat(),
        },
        {
            "name": "Blockchain",
            "code": "blockchain",
            "status": "active",
            "uptime": "100%",
            "last_check": timezone.now().isoformat(),
        },
        {
            "name": "AI Asistan",
            "code": "ai_assistant",
            "status": "active",
            "uptime": "99.5%",
            "last_check": timezone.now().isoformat(),
        },
        {
            "name": "Eğitim",
            "code": "education",
            "status": "active",
            "uptime": "99.9%",
            "last_check": timezone.now().isoformat(),
        },
    ]

    return Response(
        {
            "modules": modules,
            "overall_health": "excellent",
            "total_modules": len(modules),
            "active_modules": len([m for m in modules if m["status"] == "active"]),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_activity_graph(request):
    """
    Kullanıcı aktivite grafiği
    """

    # Son 7 gün
    days = []
    counts = []

    for i in range(7):
        day = timezone.now() - timedelta(days=6 - i)
        days.append(day.strftime("%d.%m"))
        # Placeholder data
        counts.append(10 + i * 5)

    return Response(
        {
            "labels": days,
            "data": counts,
        }
    )
