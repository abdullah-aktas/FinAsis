# -*- coding: utf-8 -*-
"""
Kullanıcı Kişisel Panel View
Giriş yapmış kullanıcının kendi verilerini görüntülediği güvenli dashboard.
Modern, rol ve izin bazlı dinamik modül erişim kartlarıyla zenginleştirilmiş.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
import json


def _get_user_role_tags(user):
    """Kullanıcı rol etiketlerini döndür (yönetici/muhasebeci/operasyon)"""
    roles = set()
    try:
        user_groups = list(user.groups.all().values_list("name", flat=True))
        for g in user_groups:
            g_lower = g.lower()
            if "manager" in g_lower or "yonetici" in g_lower:
                roles.add("manager")
            if "accountant" in g_lower or "muhasebeci" in g_lower:
                roles.add("accountant")
            if "operation" in g_lower or "operasyon" in g_lower:
                roles.add("operation")
            if "teacher" in g_lower or "ogretmen" in g_lower:
                roles.add("teacher")
            if "student" in g_lower or "ogrenci" in g_lower:
                roles.add("student")
    except Exception:
        pass

    if user.is_staff or user.is_superuser:
        roles.add("manager")

    return list(roles)


def _get_user_modules(user):
    """
    Kullanıcının erişebileceği modülleri rol ve izinlerine göre döndürür.
    Her modül: name, icon, color, url, description, category
    """
    modules = []
    user_roles = _get_user_role_tags(user)
    set(user.get_all_permissions())

    # Muhasebe Modülü
    if (
        user.has_perm("accounting.view_invoice")
        or user.has_perm("accounting.view_expense")
        or "accountant" in user_roles
        or "manager" in user_roles
    ):
        try:
            modules.append(
                {
                    "name": "Muhasebe",
                    "icon": "bi-calculator",
                    # Template, bg-gradient-{{ module.color }} pattern'i kullanıyor.
                    # Bu yüzden burada HEX kodu yerine tanımlı gradient sınıf adlarını
                    # (primary/success/info/warning/purple/secondary/dark) kullanıyoruz.
                    "color": "primary",
                    "url": reverse("accounting:dashboard"),
                    "description": "Fatura, defter, e-belge ve banka entegrasyonları",
                    "category": "finance",
                    "badge": None,
                }
            )
        except Exception:
            pass

    # Finansal Yönetim Modülü
    if (
        user.has_perm("finance.view_banktransaction")
        or "manager" in user_roles
        or "accountant" in user_roles
    ):
        try:
            modules.append(
                {
                    "name": "Finansal Yönetim",
                    "icon": "bi-graph-up-arrow",
                    "color": "success",
                    "url": reverse("finance:finance_home"),
                    "description": "KPI, bütçe, nakit akışı ve finansal raporlar",
                    "category": "finance",
                    "badge": None,
                }
            )
        except Exception:
            pass

    # Denetim Modülü
    if (
        user.has_perm("audit.view_auditlog")
        or "auditor" in user_roles
        or "manager" in user_roles
    ):
        try:
            modules.append(
                {
                    "name": "Denetim",
                    "icon": "bi-shield-check",
                    "color": "info",
                    "url": reverse("audit:landing"),
                    "description": "İşlem kayıtları, risk değerlendirme ve uyumluluk",
                    "category": "management",
                    "badge": None,
                }
            )
        except Exception:
            pass

    # Blockchain Modülü
    if user.has_perm("blockchain.view_blockchainrecord") or "manager" in user_roles:
        try:
            modules.append(
                {
                    "name": "Blockchain",
                    "icon": "bi-link-45deg",
                    "color": "purple",
                    "url": reverse("blockchain:home"),
                    "description": "Akıllı sözleşmeler ve değiştirilemez kayıtlar",
                    "category": "technology",
                    "badge": "Beta",
                }
            )
        except Exception:
            pass

    # AI Asistan - Tüm kullanıcılara açık
    try:
        modules.append(
            {
                "name": "Yapay Zeka",
                "icon": "bi-robot",
                "color": "purple",
                "url": reverse("ai_assistant:home"),
                "description": "Türkçe prompt kütüphanesi ve doğal dil raporları",
                "category": "ai",
                "badge": "Yeni",
            }
        )
    except Exception:
        pass

    # Mali Müşavirlik Modülü
    if (
        hasattr(user, "advisor_profile")
        or "financial_advisor" in user_roles
        or "mali_musavir" in user_roles
        or user.has_perm("advisors.view_advisorprofile")
    ):
        try:
            modules.append(
                {
                    "name": "Mali Müşavirlik",
                    "icon": "bi-briefcase",
                    "color": "primary",
                    "url": reverse("products_mali_musavir"),
                    "description": "Müşteri yönetimi ve danışmanlık oturumları",
                    "category": "management",
                    "badge": None,
                }
            )
        except Exception:
            pass

    # Eğitim Modülü - Öğretmen
    if "teacher" in user_roles or "egitimci" in user_roles:
        try:
            modules.append(
                {
                    "name": "Eğitim",
                    "icon": "bi-mortarboard",
                    "color": "warning",
                    "url": reverse("education:education_home"),
                    "description": "Rol bazlı LMS ve FinQuest görev motoru",
                    "category": "education",
                    "badge": None,
                }
            )
        except Exception:
            pass

    # Eğitim Modülü - Öğrenci
    if "student" in user_roles or "ogrenci" in user_roles:
        try:
            modules.append(
                {
                    "name": "Eğitim",
                    "icon": "bi-mortarboard",
                    "color": "warning",
                    "url": reverse("education:education_home"),
                    "description": "Dersler, görevler ve sertifikalar",
                    "category": "education",
                    "badge": None,
                }
            )
        except Exception:
            pass

    # Oyunlar - Tüm kullanıcılara
    try:
        modules.append(
            {
                "name": "Oyunlar",
                "icon": "bi-controller",
                "color": "purple",
                "url": reverse("games:games_index"),
                "description": "TradeSim ligleri ve finansal simülasyonlar",
                "category": "games",
                "badge": None,
            }
        )
    except Exception:
        pass

    # Yönetim Paneli
    if user.is_staff or user.is_superuser or "manager" in user_roles:
        try:
            modules.append(
                {
                    "name": "Yönetim",
                    "icon": "bi-gear",
                    "color": "secondary",
                    "url": reverse("management:admin_dashboard"),
                    "description": "Sistem ayarları ve kullanıcı yönetimi",
                    "category": "management",
                    "badge": None,
                }
            )
        except Exception:
            pass

    return modules


@login_required
def user_panel(request):
    """
    Kullanıcı kişisel paneli.
    Sadece giriş yapmış kullanıcının kendi verilerini gösterir.
    Rol ve izin bazlı dinamik modül kartları, istatistikler ve grafiklerle zenginleştirilmiş.
    """
    user = request.user

    # Kullanıcıya ait şirket bilgisi (varsa)
    user_company = getattr(user, "company", None)

    # Rol etiketleri
    user_roles = _get_user_role_tags(user)

    # Kullanıcının erişebileceği modüller
    user_modules = _get_user_modules(user)

    # Kategorilere göre modülleri grupla
    modules_by_category = {}
    for module in user_modules:
        category = module["category"]
        if category not in modules_by_category:
            modules_by_category[category] = []
        modules_by_category[category].append(module)

    # Kategori isimleri ve sıralaması
    category_labels = {
        "finance": "Finans & Muhasebe",
        "ai": "Yapay Zeka",
        "education": "Eğitim",
        "games": "Oyunlar",
        "technology": "Teknoloji",
        "management": "Denetim & Danışmanlık",
    }

    # Özet istatistikler (kullanıcıya özel)
    context = {
        "user": user,
        "company": user_company,
        "user_roles": user_roles,
        "user_modules": user_modules,
        "modules_by_category": modules_by_category,
        "category_labels": category_labels,
        "panel_title": f"{user.get_full_name() or user.username} - Kişisel Panel",
    }

    # Muhasebe modülü istatistikleri (eğer kullanıcının şirketi varsa)
    if user_company:
        try:
            from accounting.models import Invoice, Expense, BankTransaction

            # Son 30 günün verileri
            timezone.now() - timedelta(days=30)

            # Faturalar
            invoices_qs = Invoice.objects.filter(company=user_company)
            context["invoice_count"] = invoices_qs.count()
            context["recent_invoices"] = invoices_qs.order_by("-issue_date")[:5]

            # Son 6 aylık gelir trendi (grafik için)
            invoice_trend = []
            for i in range(5, -1, -1):
                month_start = timezone.now() - timedelta(days=30 * i)
                month_end = (
                    timezone.now() - timedelta(days=30 * (i - 1))
                    if i > 0
                    else timezone.now()
                )
                month_total = (
                    invoices_qs.filter(
                        issue_date__gte=month_start, issue_date__lt=month_end
                    ).aggregate(total=Sum("total_amount"))["total"]
                    or 0
                )
                invoice_trend.append(
                    {"month": month_start.strftime("%b"), "total": float(month_total)}
                )
            context["invoice_trend_json"] = json.dumps(invoice_trend)

            # Giderler
            expenses_qs = Expense.objects.filter(company=user_company)
            context["expense_count"] = expenses_qs.count()
            context["recent_expenses"] = expenses_qs.order_by("-date")[:5]

            # Son 6 aylık gider trendi
            expense_trend = []
            for i in range(5, -1, -1):
                month_start = timezone.now() - timedelta(days=30 * i)
                month_end = (
                    timezone.now() - timedelta(days=30 * (i - 1))
                    if i > 0
                    else timezone.now()
                )
                month_total = (
                    expenses_qs.filter(
                        date__gte=month_start, date__lt=month_end
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
                )
                expense_trend.append(
                    {"month": month_start.strftime("%b"), "total": float(month_total)}
                )
            context["expense_trend_json"] = json.dumps(expense_trend)

            # Banka işlemleri
            context["transaction_count"] = BankTransaction.objects.filter(
                bank_account__company=user_company
            ).count()

            # Son işlemler (gelir/gider karışık)
            recent_transactions = []
            for inv in context["recent_invoices"][:3]:
                recent_transactions.append(
                    {
                        "type": "income",
                        "description": f"Fatura: {getattr(inv, 'invoice_no', getattr(inv, 'number', 'N/A'))}",
                        "amount": getattr(inv, "total_amount", 0),
                        "date": getattr(inv, "issue_date", timezone.now()),
                    }
                )
            for exp in context["recent_expenses"][:3]:
                recent_transactions.append(
                    {
                        "type": "expense",
                        "description": f"Gider: {getattr(exp, 'description', getattr(exp, 'name', 'N/A'))}",
                        "amount": getattr(exp, "amount", 0),
                        "date": getattr(
                            exp, "date", getattr(exp, "created_at", timezone.now())
                        ),
                    }
                )
            # Tarihe göre sırala
            recent_transactions.sort(key=lambda x: x["date"], reverse=True)
            context["recent_transactions"] = recent_transactions[:5]

        except Exception:
            # Modül yüklü değilse sessizce geç
            pass

    # AI asistan etkileşim sayısı ve son öneriler
    try:
        from ai_assistant.models import UserInteraction

        context["ai_interaction_count"] = UserInteraction.objects.filter(
            user=user
        ).count()

        # Son AI önerileri (varsa)
        ai_recommendations = UserInteraction.objects.filter(
            user=user, interaction_type="recommendation"
        ).order_by("-created_at")[:3]
        context["ai_recommendations"] = ai_recommendations

    except Exception:
        pass

    # Kullanıcı başarıları (gamification)
    try:
        context["achievement_count"] = (
            user.achievements.count() if hasattr(user, "achievements") else 0
        )
        context["recent_achievements"] = (
            user.achievements.all()[:3] if hasattr(user, "achievements") else []
        )
    except Exception:
        pass

    # Rol bazlı öneri kartları
    role_insights = []
    if "manager" in user_roles:
        role_insights.append(
            {
                "title": "Yönetici İçgörüsü",
                "icon": "bi-briefcase",
                "color": "primary",
                "message": "Nakit akışı görünürlüğünü artırmak için haftalık raporları inceleyin.",
            }
        )
    if "accountant" in user_roles:
        role_insights.append(
            {
                "title": "Muhasebe Uyarısı",
                "icon": "bi-calculator",
                "color": "warning",
                "message": "Bekleyen mutabakat kayıtlarını kontrol edin.",
            }
        )
    if "operation" in user_roles:
        role_insights.append(
            {
                "title": "Operasyon",
                "icon": "bi-gear",
                "color": "info",
                "message": "Geciken tahsilatlar için otomatik hatırlatma ayarlayın.",
            }
        )

    context["role_insights"] = role_insights

    return render(request, "panel/user_panel.html", context)
