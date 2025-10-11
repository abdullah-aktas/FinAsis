from django.shortcuts import render, get_object_or_404, redirect
from django.db import models

# Re-export views from submodules used by urls.py
from ..views_extra.company_views import *  # noqa: F401,F403
from ..views_extra.customer_views import *  # noqa: F401,F403
from ..views_extra.invoice_views import *  # noqa: F401,F403
from ..views_extra.expense_views import *  # noqa: F401,F403
from ..views_extra.product_views import *  # noqa: F401,F403
from ..views_extra.sale_views import *  # noqa: F401,F403
from ..views_extra.payment_views import *  # noqa: F401,F403
from ..views_extra.vendor_views import *  # noqa: F401,F403
from ..views_extra.purchase_invoice_views import *  # noqa: F401,F403
from ..views_extra.vendor_payment_views import *  # noqa: F401,F403
from ..views_extra.bankaccount_views import *  # noqa: F401,F403
from ..views_extra.banktransaction_views import *  # noqa: F401,F403
from ..views_extra.report_views import *  # noqa: F401,F403
from ..views_extra.scenario_views import *  # noqa: F401,F403

from ..models import EDefter  # type: ignore


def index(request):
	"""Muhasebe ana sayfası."""
	return render(request, 'accounting/index.html')


def home(request):
	from ..models import Invoice, Expense, BankTransaction  # local import to avoid cycles
	user = request.user
	companies = user.created_companies.all() if hasattr(user, 'created_companies') else []
	total_income = (
		Invoice.objects.filter(company__in=companies, is_active=True)
		.aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0
	)
	total_expense = (
		Expense.objects.filter(company__in=companies, is_active=True)
		.aggregate(models.Sum('amount'))['amount__sum'] or 0
	)
	last_invoices = Invoice.objects.filter(company__in=companies, is_active=True).order_by('-issue_date')[:5]
	last_expenses = Expense.objects.filter(company__in=companies, is_active=True).order_by('-expense_date')[:5]
	if companies:
		last_banktransactions = BankTransaction.objects.filter(account__company__in=companies).order_by('-date')[:5]
	else:
		last_banktransactions = BankTransaction.objects.none()
	context = {
		'total_income': total_income,
		'total_expense': total_expense,
		'last_invoices': last_invoices,
		'last_expenses': last_expenses,
		'last_banktransactions': last_banktransactions,
	}
	return render(request, 'accounting/home.html', context)


def edefter_send_gib(request, pk: int):
	from ..services.edefter_service import send_edefter_to_gib
	edefter = get_object_or_404(EDefter, pk=pk)
	try:
		send_edefter_to_gib(edefter)
	except Exception:
		pass
	return redirect('accounting:summary_report')


def edefter_get_berat(request, pk: int):
	from ..services.edefter_service import get_edefter_berat
	edefter = get_object_or_404(EDefter, pk=pk)
	try:
		get_edefter_berat(edefter)
	except Exception:
		pass
	return redirect('accounting:summary_report')
