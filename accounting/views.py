from django.shortcuts import render
from django.db import models
from .views_extra.company_views import *
from .views_extra.customer_views import *
from .views_extra.invoice_views import *
from .views_extra.expense_views import *
from .views_extra.product_views import *
from .views_extra.sale_views import *
from .views_extra.payment_views import *
from .views_extra.vendor_views import *
from .views_extra.purchase_invoice_views import *
from .views_extra.vendor_payment_views import *
from .views_extra.bankaccount_views import *
from .views_extra.banktransaction_views import *
from .views_extra.report_views import *
from .views_extra.scenario_views import *
from .services.edefter_service import send_edefter_to_gib, get_edefter_berat
from .models import EDefter
from django.shortcuts import get_object_or_404, redirect


def index(request):
    # Muhasebe ana sayfasını basit metin yerine zengin bir index şablonuyla göster
    return render(request, "accounting/index.html")


def home(request):
    from .models import Invoice, Expense, BankTransaction

    user = request.user
    # Kullanıcıya ait şirketler
    companies = (
        user.created_companies.all() if hasattr(user, "created_companies") else []
    )
    # Toplam gelir
    total_income = (
        Invoice.objects.filter(company__in=companies, is_active=True).aggregate(
            models.Sum("total_amount")
        )["total_amount__sum"]
        or 0
    )
    # Toplam gider
    total_expense = (
        Expense.objects.filter(company__in=companies, is_active=True).aggregate(
            models.Sum("amount")
        )["amount__sum"]
        or 0
    )
    # Son 5 fatura
    last_invoices = Invoice.objects.filter(
        company__in=companies, is_active=True
    ).order_by("-issue_date")[:5]
    # Son 5 gider
    last_expenses = Expense.objects.filter(
        company__in=companies, is_active=True
    ).order_by("-expense_date")[:5]
    # Son 5 banka işlemi (BankTransaction -> account -> company ilişkisi)
    if companies:
        last_banktransactions = BankTransaction.objects.filter(
            account__company__in=companies
        ).order_by("-date")[:5]
    else:
        last_banktransactions = BankTransaction.objects.none()
    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "last_invoices": last_invoices,
        "last_expenses": last_expenses,
        "last_banktransactions": last_banktransactions,
    }
    return render(request, "accounting/home.html", context)


def edefter_send_gib(request, pk: int):
    edefter = get_object_or_404(EDefter, pk=pk)
    try:
        send_edefter_to_gib(edefter)
    except Exception:
        pass
    return redirect("accounting:summary_report")


def edefter_get_berat(request, pk: int):
    edefter = get_object_or_404(EDefter, pk=pk)
    try:
        get_edefter_berat(edefter)
    except Exception:
        pass
    return redirect("accounting:summary_report")
