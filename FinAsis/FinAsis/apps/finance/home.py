from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from FinAsis.apps.accounting.models import Company
from django.db.models import Sum, Count
from FinAsis.apps.finance.models import BankAccount, EInvoice
from FinAsis.apps.accounting.models import BankTransaction

def finance_home(request):
    # Özet metrikler
    bank_account_count = BankAccount.objects.count()
    txn_count = BankTransaction.objects.count()
    last_transactions = BankTransaction.objects.order_by('-date')[:5]

    einvoice_count = EInvoice.objects.count()
    totals = EInvoice.objects.aggregate(
        total_amount_sum=Sum('total'),
        subtotal_sum=Sum('subtotal'),
        tax_sum=Sum('tax_total'),
    )
    last_invoices = EInvoice.objects.order_by('-issue_date' if hasattr(EInvoice, 'issue_date') else '-invoice_date', '-created_at')[:5]

    context = {
        'bank_account_count': bank_account_count,
        'txn_count': txn_count,
        'last_transactions': last_transactions,
        'einvoice_count': einvoice_count,
        'invoice_totals': totals,
        'last_invoices': last_invoices,
    }
    return render(request, "finance/home.html", context)

@login_required
def companies_api(request):
    user = request.user
    companies = Company.objects.none()
    try:
        if hasattr(user, 'company') and user.company:
            companies = Company.objects.filter(id=user.company.id)
    except Exception:
        companies = Company.objects.filter(created_by=user)
    data = [{"id": c.id, "name": c.name} for c in companies]
    return JsonResponse({"results": data})