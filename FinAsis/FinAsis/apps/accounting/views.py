from django.shortcuts import render, HttpResponse
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
    return HttpResponse("Muhasebe ana sayfası")

def home(request):
    return render(request, 'accounting/home.html')

def edefter_send_gib(request, pk: int):
    edefter = get_object_or_404(EDefter, pk=pk)
    try:
        send_edefter_to_gib(edefter)
    except Exception:
        pass
    return redirect('accounting:summary_report')

def edefter_get_berat(request, pk: int):
    edefter = get_object_or_404(EDefter, pk=pk)
    try:
        get_edefter_berat(edefter)
    except Exception:
        pass
    return redirect('accounting:summary_report')
