from django.shortcuts import render, HttpResponse
from .views_extra.company_views import *
from .views_extra.customer_views import *
from .views_extra.invoice_views import *
from .views_extra.expense_views import *
from .views_extra.product_views import *
from .views_extra.sale_views import *
from .views_extra.payment_views import *
from .views_extra.bankaccount_views import *
from .views_extra.banktransaction_views import *
from .views_extra.report_views import *

def index(request):
    return HttpResponse("Muhasebe ana sayfası")

def home(request):
    return render(request, 'accounting/home.html')
